import cv2
import numpy as np
import os
from matplotlib import pyplot as plt

print("=== Task 2: Visual SLAM on My Own Space (Airfield Video) ===")

video_path = "/home/ruchiksy/vslam_ws/IMG_3673.MOV"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Cannot open video: {video_path}")
    print("Check if the file exists and is not corrupted.")
    exit()

print(f"Video opened: {video_path}")
print(f"Resolution: {int(cap.get(3))} x {int(cap.get(4))}")
print("Starting processing... Press 'q' to stop early.\n")

orb = cv2.ORB_create(nfeatures=3000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

K = np.array([[2800, 0, 1920],
              [0, 2800, 1080],
              [0, 0, 1]], dtype=np.float32)

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

    if prev_des is not None and des is not None:
        matches = bf.knnMatch(prev_des, des, k=2)
        good = [m for m, n in matches if m.distance < 0.75 * n.distance]

        if len(good) > 30:
            pts1 = np.float32([prev_kp[m.queryIdx].pt for m in good])
            pts2 = np.float32([kp[m.trainIdx].pt for m in good])

            E, mask = cv2.findEssentialMat(pts1, pts2, K, method=cv2.RANSAC, threshold=1.0)
            if E is not None:
                _, R, t, _ = cv2.recoverPose(E, pts1, pts2, K)
                T = np.eye(4)
                T[:3, :3] = R
                T[:3, 3] = t.flatten()
                current_pose = current_pose @ T

                trajectory.append([current_pose[0,3], current_pose[2,3]])

    if frame_idx % 30 == 0:
        matches_count = len(good) if 'good' in locals() else 0
        print(f"Frame {frame_idx:5d} | Matches: {matches_count:4d} | Pos: ({current_pose[0,3]:.2f}, {current_pose[2,3]:.2f})")

    prev_kp = kp
    prev_des = des
    frame_idx += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nFinished processing {frame_idx} frames.")

if len(trajectory) > 5:
    traj = np.array(trajectory)
    plt.figure(figsize=(12, 8))
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, label='Estimated Path')
    plt.plot(traj[0,0], traj[0,1], 'go', markersize=12, label='Start')
    plt.plot(traj[-1,0], traj[-1,1], 'ro', markersize=12, label='End')
    plt.xlabel('X')
    plt.ylabel('Z')
    plt.title('Task 2 - Camera Trajectory on Airfield Video')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.savefig('task2_airfield_trajectory.png')
    plt.show()
    print("Plot saved as task2_airfield_trajectory.png")
else:
    print("Not enough frames for a meaningful trajectory.")
