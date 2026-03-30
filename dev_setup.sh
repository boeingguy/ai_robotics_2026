#!/bin/bash

# 1. Source the System ROS 2 installation
echo "Sourcing ROS 2 Jazzy System..."
source /opt/ros/jazzy/setup.bash

# 2. Source your local Workspace
if [ -f "install/setup.bash" ]; then
    echo "Sourcing Local Workspace..."
    source install/setup.bash
fi

# 3. Activate the Virtual Environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating Python Virtual Environment..."
    source .venv/bin/activate
fi

echo "Environment Ready (Jazzy + .venv)!"

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

export ROS_DOMAIN_ID=0
