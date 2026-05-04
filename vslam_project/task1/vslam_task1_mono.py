import cv2
import numpy as np
import os
from matplotlib import pyplot as plt

print("=== Task 1: Monocular Visual Odometry on KITTI (with GT) ===")

# Paths (your current layout)
basedir = '/home/ruchiksy/vslam_ws'
sequence = '00'

calib_file = os.path.join(basedir, 'data_odometry_calib', 'dataset', 'sequences', sequence, 'calib.txt')
img_path   = os.path.join(basedir, 'data_odometry_gray', 'dataset', 'sequences', sequence, 'image_0')
gt_file    = os.path.join(basedir, 'data_odometry_poses', 'dataset', 'poses', f'{sequence}.txt')

print(f"Calibration: {calib_file}")
print(f"Images: {img_path}")
print(f"Ground Truth: {gt_file}\n")

# Load K
with open(calib_file, 'r') as f:
    P0 = np.array([float(x) for x in f.readline().split()[1:]]).reshape(3,4)
K = P0[:3, :3]
print("K Matrix:\n", K)

# Images
img_files = sorted([os.path.join(img_path, f) for f in os.listdir(img_path) if f.endswith('.png')])
print(f"Found {len(img_files)} images\n")

# VO
orb = cv2.ORB_create(nfeatures=3000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

trajectory = []
current_pose = np.eye(4)

for i in range(len(img_files)-1):
    img1 = cv2.imread(img_files[i], cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img_files[i+1], cv2.IMREAD_GRAYSCALE)

    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        trajectory.append([current_pose[0,3], current_pose[2,3]])
        continue

    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]

    if len(good) > 30:
        pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

        E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, threshold=1.0)
        if E is not None:
            _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K)
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = t.flatten()
            current_pose = current_pose @ T

    trajectory.append([current_pose[0,3], current_pose[2,3]])

    if i % 30 == 0:
        print(f"Frame {i:4d} | Matches: {len(good):4d} | Pos: ({current_pose[0,3]:.2f}, {current_pose[2,3]:.2f})")

print(f"\nFinished {len(img_files)} frames.")

# Plot with GT
traj = np.array(trajectory)
plt.figure(figsize=(12, 9))
plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, label='Estimated Path (Monocular VO)')
plt.plot(traj[0,0], traj[0,1], 'go', markersize=12, label='Start')
plt.plot(traj[-1,0], traj[-1,1], 'ro', markersize=12, label='End')

if os.path.exists(gt_file):
    gt_poses = np.loadtxt(gt_file)
    gt_traj = gt_poses[:, [3, 11]]  # x, z
    plt.plot(gt_traj[:,0], gt_traj[:,1], 'r--', linewidth=2, label='Ground Truth')
    print("Ground Truth plotted for comparison.")
else:
    print("Ground Truth file not found.")

plt.xlabel('X')
plt.ylabel('Z')
plt.title(f'Task 1 - Monocular VO vs Ground Truth (Sequence {sequence})')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig('task1_mono_with_gt.png')
plt.show()

print("Plot saved as task1_mono_with_gt.png")
