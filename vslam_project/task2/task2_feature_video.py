import cv2
import numpy as np

print("=== Creating Feature Detection Demo Video for Task 2 ===")

video_path = "/home/ruchiksy/vslam_ws/inside_house_walking.MOV"
output_path = "/home/ruchiksy/vslam_ws/task2_indoor_features_demo.mp4"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Cannot open video")
    exit()

fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

orb = cv2.ORB_create(nfeatures=2000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

prev_kp = None
prev_des = None
frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp, des = orb.detectAndCompute(gray, None)

    display = frame.copy()

    # Draw keypoints
    cv2.drawKeypoints(display, kp, display, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Draw matches
    if prev_des is not None and des is not None:
        matches = bf.knnMatch(prev_des, des, k=2)
        good = [m[0] for m in matches if len(m) == 2 and m[0].distance < 0.75 * m[1].distance]

        for m in good[:100]:  # limit for clarity
            pt1 = tuple(map(int, prev_kp[m.queryIdx].pt))
            pt2 = tuple(map(int, kp[m.trainIdx].pt))
            cv2.line(display, pt1, pt2, (255, 0, 0), 1)

    # Info text
    cv2.putText(display, f"Frame: {frame_idx}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    cv2.putText(display, f"Features: {len(kp)}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.putText(display, "Task 2 - Indoor VSLAM Demo", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)

    out.write(display)

    if frame_idx % 30 == 0:
        print(f"Processed frame {frame_idx}")

    prev_kp = kp
    prev_des = des
    frame_idx += 1

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"\n✅ Demo video created:")
print(f"   {output_path}")
print("This video shows ORB features and matches - perfect for your YouTube demo.")
