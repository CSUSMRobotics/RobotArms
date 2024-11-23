Code for px100 robot arm. Bartender.py is an example demo from interbotix_ros_manipulators repository. rtc.py uses user's keyboard input for moving all 5 joints, but only 1 joint movement executes at a time due to single thread program structure. multithreaded.py moves all 5 joints simultaneously through user's keyboard input.

Press LEFT and RIGHT arrow keys to move the waist joint.
Press UP and DOWN arrow keys to move the elbow joint.
Press 'a' and 'd' to move the shoulder joint up and down.
Press 'w' and 's' to move the wrist angle up and down.
Press 'o' to open the gripper, 'c' to close the gripper, and ESC to quit."

https://docs.trossenrobotics.com/interbotix_xsarms_docs/ros_interface/ros2/software_setup.html#
https://github.com/CSUSMRobotics/RobotArms/wiki/Setup-Raspberry-Pi-4-Ubuntu-20.04-Desktop-for-Robot-Arms
