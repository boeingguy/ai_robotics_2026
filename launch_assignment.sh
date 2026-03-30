#!/bin/bash

# Configuration
CONTAINER_ID="85c95dd78cb7"
WS_DIR="~/ros2_ws"

# We use 'bash -ic' to ensure your .bashrc and aliases are loaded
# The 'cd' command uses $HOME to ensure it finds your workspace correctly

wt.exe -d . wsl.exe bash -ic "docker exec -it $CONTAINER_ID bash -c 'source /opt/ros/jazzy/setup.bash && source /overlay_ws/install/setup.bash && export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && zenoh-bridge-ros2dds -l tcp/0.0.0.0:7447 --rest-http-port 8000'; exec bash" \
  split-pane -d . wsl.exe bash -ic "cd $WS_DIR && source dev_setup.sh && python3 zenoh_detection_node.py; exec bash" \
  split-pane -d . wsl.exe bash -ic "cd $WS_DIR && source dev_setup.sh && python3 ingest_worker.py; exec bash" \
  split-pane -d . wsl.exe bash -ic "cd $WS_DIR && watch -n 1 'psql -d robot_data -c \"SELECT class_label, confidence, event_timestamp FROM object_detections ORDER BY id DESC LIMIT 5;\"'; exec bash"
