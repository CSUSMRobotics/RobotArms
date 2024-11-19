from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from pynput import keyboard
import numpy as np
import time
import threading

# Initialize variables for joint and gripper control
moving_direction_waist = 0  # 0 = idle, 1 = clockwise, -1 = counter-clockwise
moving_direction_elbow = 0  # 0 = idle, 1 = down, -1 = up (flipped)
moving_direction_shoulder = 0  # 0 = idle, 1 = up, -1 = down
moving_direction_wrist = 0  # 0 = idle, 1 = up, -1 = down
gripper_action = 0          # 0 = idle, 1 = open, -1 = close

def on_press(key):
    global moving_direction_waist, moving_direction_elbow, moving_direction_shoulder, moving_direction_wrist, gripper_action
    try:
        if key == keyboard.Key.left:
            moving_direction_waist = 1
        elif key == keyboard.Key.right:
            moving_direction_waist = -1
        elif key == keyboard.Key.up:
            moving_direction_elbow = -1  # Flipped: UP key moves elbow up
        elif key == keyboard.Key.down:
            moving_direction_elbow = 1   # Flipped: DOWN key moves elbow down
        elif hasattr(key, 'char') and key.char == 'a':  # Shoulder joint up
            moving_direction_shoulder = 1
        elif hasattr(key, 'char') and key.char == 'd':  # Shoulder joint down
            moving_direction_shoulder = -1
        elif hasattr(key, 'char') and key.char == 'w':  # Wrist angle up
            moving_direction_wrist = 1
        elif hasattr(key, 'char') and key.char == 's':  # Wrist angle down
            moving_direction_wrist = -1
        elif hasattr(key, 'char') and key.char == 'o':  # Open gripper
            gripper_action = 1
            threading.Thread(target=control_gripper, args=(gripper_action,)).start()  # Start gripper thread
        elif hasattr(key, 'char') and key.char == 'c':  # Close gripper
            gripper_action = -1
            threading.Thread(target=control_gripper, args=(gripper_action,)).start()  # Start gripper thread
    except AttributeError:
        pass

def on_release(key):
    global moving_direction_waist, moving_direction_elbow, moving_direction_shoulder, moving_direction_wrist
    if key in (keyboard.Key.left, keyboard.Key.right):
        moving_direction_waist = 0
    if key in (keyboard.Key.up, keyboard.Key.down):
        moving_direction_elbow = 0
    if hasattr(key, 'char') and key.char in ('a', 'd'):
        moving_direction_shoulder = 0
    if hasattr(key, 'char') and key.char in ('w', 's'):
        moving_direction_wrist = 0
    if key == keyboard.Key.esc:
        # Stop listener
        return False

def control_gripper(action):
    """Function to control the gripper in a separate thread."""
    global gripper_action
    bot = control_gripper.bot  # Access the robot instance
    if action == 1:
        bot.gripper.release(delay=2.5)
        print("Gripper opening")
    elif action == -1:
        bot.gripper.grasp(delay=2.5)
        print("Gripper closing")
    gripper_action = 0  # Reset the action

def main():
    global gripper_action  # Declare gripper_action as global to use it in this function
    bot = InterbotixManipulatorXS("px100", "arm", "gripper")
    control_gripper.bot = bot  # Assign the robot instance to the gripper control function
    robot_startup()

    # Move the arm to the home position
    bot.arm.go_to_home_pose()
    time.sleep(2)  # Wait for 2 seconds

    # Start the key listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Define joint limits for the waist, elbow, shoulder, and wrist (in radians)
    waist_limit_min = np.deg2rad(-180)
    waist_limit_max = np.deg2rad(180)
    elbow_limit_min = np.deg2rad(-121)
    elbow_limit_max = np.deg2rad(92)
    shoulder_limit_min = np.deg2rad(-111)
    shoulder_limit_max = np.deg2rad(107)
    wrist_limit_min = np.deg2rad(-100)
    wrist_limit_max = np.deg2rad(123)

    # Increase the step size for faster movement (doubled speed)
    step_angle = np.deg2rad(4)  # Previously 2, now doubled for faster movement

    print("Use LEFT and RIGHT arrow keys to move the waist joint continuously.")
    print("Use UP and DOWN arrow keys to move the elbow joint (flipped control).")
    print("Use 'a' and 'd' to move the shoulder joint up and down.")
    print("Use 'w' and 's' to move the wrist angle up and down.")
    print("Press 'o' to open the gripper, 'c' to close the gripper, and ESC to quit.")

    try:
        while listener.is_alive():
            # Move the waist joint if a direction is specified
            if moving_direction_waist != 0:
                current_angle_waist = bot.arm.get_single_joint_command("waist")
                new_angle_waist = current_angle_waist + step_angle * moving_direction_waist
                new_angle_waist = np.clip(new_angle_waist, waist_limit_min, waist_limit_max)  # Ensure within limits
                bot.arm.set_single_joint_position("waist", new_angle_waist, moving_time=0.05)
                direction_text_waist = "clockwise" if moving_direction_waist == 1 else "counter-clockwise"
                print(f"Moving waist {direction_text_waist} to {np.rad2deg(new_angle_waist)} degrees")

            # Move the elbow joint if a direction is specified
            if moving_direction_elbow != 0:
                current_angle_elbow = bot.arm.get_single_joint_command("elbow")
                new_angle_elbow = current_angle_elbow + step_angle * moving_direction_elbow
                new_angle_elbow = np.clip(new_angle_elbow, elbow_limit_min, elbow_limit_max)  # Ensure within limits
                direction_text_elbow = "down" if moving_direction_elbow == 1 else "up"
                print(f"Moving elbow {direction_text_elbow} to {np.rad2deg(new_angle_elbow)} degrees")
                bot.arm.set_single_joint_position("elbow", new_angle_elbow, moving_time=0.05)

            # Move the shoulder joint if a direction is specified
            if moving_direction_shoulder != 0:
                current_angle_shoulder = bot.arm.get_single_joint_command("shoulder")
                new_angle_shoulder = current_angle_shoulder + step_angle * moving_direction_shoulder
                new_angle_shoulder = np.clip(new_angle_shoulder, shoulder_limit_min, shoulder_limit_max)  # Ensure within limits
                direction_text_shoulder = "up" if moving_direction_shoulder == 1 else "down"
                print(f"Moving shoulder {direction_text_shoulder} to {np.rad2deg(new_angle_shoulder)} degrees")
                bot.arm.set_single_joint_position("shoulder", new_angle_shoulder, moving_time=0.05)

            # Move the wrist angle if a direction is specified
            if moving_direction_wrist != 0:
                current_angle_wrist = bot.arm.get_single_joint_command("wrist_angle")
                new_angle_wrist = current_angle_wrist + step_angle * moving_direction_wrist
                new_angle_wrist = np.clip(new_angle_wrist, wrist_limit_min, wrist_limit_max)  # Ensure within limits
                direction_text_wrist = "up" if moving_direction_wrist == 1 else "down"
                print(f"Moving wrist {direction_text_wrist} to {np.rad2deg(new_angle_wrist)} degrees")
                bot.arm.set_single_joint_position("wrist_angle", new_angle_wrist, moving_time=0.05)

            time.sleep(0.05)  # Short delay for smooth continuous movement
    finally:
        listener.stop()

    # Move the arm to the sleep position
    bot.arm.go_to_sleep_pose()
    time.sleep(2)  # Wait for 2 seconds

    # Shutdown the robot
    robot_shutdown()
    print("Program finished successfully.")

if __name__ == '__main__':
    main()
