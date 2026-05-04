#!/bin/bash
echo "=== Task 3: Full StellaVSLAM + Nav2 Demo ==="

echo "1. Launch Gazebo (in another terminal)"
echo "   export TURTLEBOT3_MODEL=waffle"
echo "   ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py"

echo "2. Launch StellaVSLAM"
ros2 run stella_vslam_ros run_slam \
  -v /home/ruchiksy/vslam_ws/orb_vocab.fbow \
  -c /home/ruchiksy/vslam_ws/my_indoor_camera.yaml &

echo "3. Launch Nav2"
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true map:=/dev/null &

echo "4. Launch RViz"
ros2 run rviz2 rviz2 &

echo "Use teleop to move the robot."
echo "Task 3 demo ready."
