from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
import numpy as np
import sys
import curses

# This script makes the end-effector perform pick, pour, and place tasks
# Note that this script is adapted for the px100 robot arm
# Make sure to adjust commanded joint positions and poses as necessary
#
# To get started, open a terminal and type 'roslaunch interbotix_xsarm_control xsarm_control.launch robot_model:=px100'
# Then change to this directory and type 'python bartender_px100.py  # python3 bartender_px100.py if using ROS Noetic'

def main():
    bot = InterbotixManipulatorXS("px100", "arm", "gripper")

    robot_startup()

    if (bot.arm.group_info.num_joints < 4):
        bot.get_node().logfatal(
            'This demo requires the robot to have at least 4 joints!'
        )
        robot_shutdown()
        sys.exit()

    # allows user input through keyboard
    curses.wrapper(gripper_control, bot)

    bot.arm.go_to_home_pose()
    bot.arm.go_to_sleep_pose()
    robot_shutdown()


def gripper_control(stdscr, bot):
    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.addstr("Press left arrow for clockwise rotation of waist, right arrow to rotate counter-clockwise." +
        "Press up arrow to move shoulder up, down arrow to move shoulder down." +
        "Press 'o' to open the gripper, 'c' to close the gripper, 'q' to quit.\n")
    
    # Define joint limits (in radians)
    joint_limits = {
        "waist": {"min": np.deg2rad(-180), "max": np.deg2rad(180)},
        "shoulder": {"min": np.deg2rad(-111), "max": np.deg2rad(107)},
        "elbow": {"min": np.deg2rad(-121), "max": np.deg2rad(92)},
        "wrist_angle": {"min": np.deg2rad(-100), "max": np.deg2rad(123)},
    }

    while True:
        key = stdscr.getch()
       
        if key == ord('o'):
            # open gripper
            bot.gripper.release(delay=2.5)
            print("Opening gripper\n\r")
        elif key == ord('c'):
            # close gripper
            bot.gripper.grasp(delay=2.5)
            print("Closing gripper\n\r")

        elif key == curses.KEY_LEFT:
            # adjust waist joint clockwise
            new_angle = bot.arm.get_single_joint_command("waist") + np.deg2rad(5)
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["waist"]["min"], joint_limits["waist"]["max"])
            bot.arm.set_single_joint_position(joint_name='waist', position=new_angle, moving_time=0.05)
            print("Moving waist clockwise\n\r")
        elif key == curses.KEY_RIGHT:
            # adjust waist joint counter_clockwise
            new_angle = bot.arm.get_single_joint_command("waist") - np.deg2rad(5)
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["waist"]["min"], joint_limits["waist"]["max"])
            bot.arm.set_single_joint_position(joint_name='waist', position=new_angle, moving_time=0.05)
            print("Moving waist counter-clockwise\n\r")

        elif key == curses.KEY_UP:
            # Move the shoulder joint up
            new_angle = bot.arm.get_single_joint_command("shoulder") + np.deg2rad(5)  # Move shoulder up
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["shoulder"]["min"], joint_limits["shoulder"]["max"])
            bot.arm.set_single_joint_position(joint_name='shoulder', position=new_angle, moving_time=0.05)
            print("Moving shoulder up\n\r")
        elif key == curses.KEY_DOWN:
            # Move the shoulder joint down
            new_angle = bot.arm.get_single_joint_command("shoulder") - np.deg2rad(5)  # Move shoulder down
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["shoulder"]["min"], joint_limits["shoulder"]["max"])
            bot.arm.set_single_joint_position(joint_name='shoulder', position=new_angle, moving_time=0.05)
            print("Moving shoulder down\n\r")

        elif key == ord('a'):
            # Move the elbow joint up (increase angle)
            new_angle = bot.arm.get_single_joint_command("elbow") + np.deg2rad(5)  # Increase elbow angle
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["elbow"]["min"], joint_limits["elbow"]["max"])
            bot.arm.set_single_joint_position(joint_name='elbow', position=new_angle, moving_time=0.05)
            print("Moving elbow up\n")
        elif key == ord('d'):
            # Move the elbow joint down (decrease angle)
            new_angle = bot.arm.get_single_joint_command("elbow") - np.deg2rad(5)  # Decrease elbow angle
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["elbow"]["min"], joint_limits["elbow"]["max"])
            bot.arm.set_single_joint_position(joint_name='elbow', position=new_angle, moving_time=0.05)
            print("Moving elbow down\n")

        elif key == ord('w'):
            # Move the wrist_angle joint up (increase angle)
            new_angle = bot.arm.get_single_joint_command("wrist_angle") + np.deg2rad(5)  # Increase wrist_angle angle
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["wrist_angle"]["min"], joint_limits["wrist_angle"]["max"])
            bot.arm.set_single_joint_position(joint_name='wrist_angle', position=new_angle, moving_time=0.05)
            print("Moving wrist_angle up\n")
        elif key == ord('s'):
            # Move the wrist_angle joint down (decrease angle)
            new_angle = bot.arm.get_single_joint_command("wrist_angle") - np.deg2rad(5)  # Decrease wrist_angle angle
            # Ensure the angle is within valid limits
            new_angle = np.clip(new_angle, joint_limits["wrist_angle"]["min"], joint_limits["wrist_angle"]["max"])
            bot.arm.set_single_joint_position(joint_name='wrist_angle', position=new_angle, moving_time=0.05)
            print("Moving wrist_angle down\n")

        elif key == ord('q'):
            stdscr.addstr("Quitting keyboard control...\n")
            return # go back to main for shutdown
        # time.sleep(0.05)

if __name__ == '__main__':
    main()
