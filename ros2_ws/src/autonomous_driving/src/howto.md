ssh:
cd ~/ros2_ws

colcon build --packages-up-to <your_package_name>

source install/setup.bash

ros2 run <your_package_name> autonomous_driving

another terminal:
ros2 topic pub --once /autonomous_command interfaces/msg/AutonomousCommand "{start: true}"

arreter:
ros2 topic pub --once /autonomous_command interfaces/msg/AutonomousCommand "{start: false}"


Il faut lancer ces nodes en meme temps et en different terminaux:
- CAN Rx
- CAN Tx
- Ultrasonic
- Motors orders

Maybe need to change something if this file is not found: autonous_driver, just change it to autonomous

Change sequence in autonomous_driving.cpp
