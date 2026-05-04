import cv2
import numpy as np
import os
from matplotlib import pyplot as plt

print("=== Task 2: Visual SLAM on My Own Indoor Space ===")

video_path = "/home/ruchiksy/vslam_ws/inside_house_walking.MOV"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"ERROR: Cannot open video: {video_path}")
    exit()

print(f"Video opened successfully!")
print(f"Resolution: {int(cap.get(3))} x {int(cap.get(4))}")
print("Processing indoor walking video... Press 'q' to stop.\n")

orb = cv2.ORB_create(nfeatures=2500)
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

    good = []
    if prev_des is not None and des is not None:
        matches = bf.knnMatch(prev_des, des, k=2)
        for match in matches:
            if len(match) == 2:
                m, n = match
                if m.distance < 0.75 * n.distance:
                    good.append(m)

    if len(good) > 35:
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
        print(f"Frame {frame_idx:5d} | Good Matches: {len(good):4d} | Pos: ({current_pose[0,3]:.2f}, {current_pose[2,3]:.2f})")

    prev_kp = kp
    prev_des = des
    frame_idx += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\nFinished processing {frame_idx} frames from indoor video.")

if len(trajectory) > 10:
    traj = np.array(trajectory)
    plt.figure(figsize=(12, 9))
    plt.plot(traj[:,0], traj[:,1], 'b-', linewidth=2, label='Estimated Path')
    plt.plot(traj[0,0], traj[0,1], 'go', markersize=12, label='Start')
    plt.plot(traj[-1,0], traj[-1,1], 'ro', markersize=12, label='End')
    plt.xlabel('X')
    plt.ylabel('Z')
    plt.title('Task 2 - Camera Trajectory on Indoor House Walking')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.savefig('task2_indoor_trajectory.png')
    plt.show()
    print("Plot saved as task2_indoor_trajectory.png")
else:
    print("Not enough good frames for trajectory.")
