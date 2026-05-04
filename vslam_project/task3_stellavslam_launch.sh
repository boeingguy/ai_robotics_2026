#!/bin/bash
echo "=== Task 3: StellaVSLAM Launch ==="

ros2 run stella_vslam_ros run_slam \
  -v /home/ruchiksy/vslam_ws/orb_vocab.fbow \
  -c /home/ruchiksy/vslam_ws/my_indoor_camera.yaml \
  --viewer none
