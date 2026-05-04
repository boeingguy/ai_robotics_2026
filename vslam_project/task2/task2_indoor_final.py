import cv2
import numpy as np
import os
from matplotlib import pyplot as plt

print("="*60)
print("Task 2: VSLAM on My Own Indoor Space")
print("="*60)
print("Using indoor house walking video (inside_house_walking.MOV)")
print("Method: ORB Feature Detection + Essential Matrix + Pose Estimation")
print("Note: Full StellaVSLAM setup attempted but using Python VO due to vocab/binary issues.")
print()

video_path = "/home/ruchiksy/vslam_ws/inside_house_walking.MOV"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("ERROR: Cannot open video file.")
    exit()

print(f"Video loaded: {video_path}")
print(f"Resolution: {int(cap.get(3))}x{int(cap.get(4))}\n")

# Camera intrinsics (approximate for phone)
K = np.array([[2800, 0, 1920],
              [0, 2800, 1080],
              [0, 0, 1]], dtype=np.float32)

orb = cv2.ORB_create(nfeatures=3000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

trajectory = []
current_pose = np.eye(4)
frame_idx = 0
prev_kp = None
prev_des = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp, des = orb.detectAndCompute(gray, None)

    good = []
    if prev_des is not None and des is not None:
        matches = bf.knnMatch(prev_des, des, k=2)
        for m in matches:
            if len(m) == 2:
                if m[0].distance < 0.75 * m[1].distance:
                    good.append(m[0])

    if len(good) > 40:  # Higher threshold for stability
        pts1 = np.float32([prev_kp[m.queryIdx].pt for m in good])
        pts2 = np.float32([kp[m.trainIdx].pt for m in good])

        E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, threshold=1.0)
        if E is not None:
            _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K)
            T = np.eye(4)
            T[:3,:3] = R
            T[:3,3] = t.flatten()
            current_pose = current_pose @ T
            trajectory.append([current_pose[0,3], current_pose[2,3]])

    if frame_idx % 30 == 0:
        print(f"Frame {frame_idx:5d} | Good Matches: {len(good):4d} | Pos: ({current_pose[0,3]:.2f}, {current_pose[2,3]:.2f})")

    prev_kp = kp
    prev_des = des
    frame_idx += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

print(f"\nFinished processing {frame_idx} frames.")

# Plot
if len(trajectory) > 10:
    traj = np.array(trajectory)
    plt.figure(figsize=(12, 9))
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2.5, label='Estimated Camera Path')
    plt.plot(traj[0,0], traj[0,1], 'go', markersize=15, label='Start')
    plt.plot(traj[-1,0], traj[-1,1], 'ro', markersize=15, label='End')
    plt.xlabel('X (arbitrary scale)')
    plt.ylabel('Z (arbitrary scale)')
    plt.title('Task 2 - Monocular VO on Indoor House Walking Video')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.savefig('task2_indoor_final_trajectory.png', dpi=200)
    plt.show()
    print("Final plot saved as task2_indoor_final_trajectory.png")
else:
    print("Not enough frames processed.")

print("\nTask 2 completed with indoor video.")

