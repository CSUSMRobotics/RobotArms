from interbotix_common_modules.common_robot.robot import robot_shutdown, robot_startup
from interbotix_xs_modules.xs_robot.arm import InterbotixManipulatorXS
from pynput import keyboard
import time
import threading

# Initialize variables for joint control
moving_direction_waist = 0  # 0 = idle, 1 = clockwise, -1 = counter-clockwise
moving_direction_elbow = 0  # 0 = idle, 1 = down, -1 = up (flipped)
moving_direction_shoulder = 0  # 0 = idle, 1 = up, -1 = down
moving_direction_wrist = 0  # 0 = idle, 1 = up, -1 = down
gripper_action = 0  # 0 = idle, 1 = open, -1 = close

# Speed and acceleration control
step_angle = 0.01  # Smaller step angle for smoother movement
moving_time = 0.01  # Reduced moving time for smoother updates

# Initialize robot
bot = None
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
        elif hasattr(key, 'char') and key.char == 'w':  # Wrist joint up
            moving_direction_wrist = 1
        elif hasattr(key, 'char') and key.char == 's':  # Wrist joint down
            moving_direction_wrist = -1
        elif hasattr(key, 'char') and key.char == 'o':  # Open gripper
            gripper_action = 1
        elif hasattr(key, 'char') and key.char == 'c':  # Close gripper
            gripper_action = -1
    except AttributeError:
        pass
        
def on_release(key):
    global moving_direction_waist, moving_direction_elbow, moving_direction_shoulder, moving_direction_wrist, gripper_action
    if key in (keyboard.Key.left, keyboard.Key.right):
        moving_direction_waist = 0
    if key in (keyboard.Key.up, keyboard.Key.down):
        moving_direction_elbow = 0
    if hasattr(key, 'char') and key.char in ('a', 'd'):
        moving_direction_shoulder = 0
    if hasattr(key, 'char') and key.char in ('w', 's'):
        moving_direction_wrist = 0
    if hasattr(key, 'char') and key.char in ('o', 'c'):
        gripper_action = 0
    if key == keyboard.Key.esc:
        # Stop listener
        return False
        
def move_waist():
    global moving_direction_waist, bot
    while True:
        if moving_direction_waist != 0:
            current_angle_waist = bot.arm.get_single_joint_command("waist")
            new_angle_waist = current_angle_waist + step_angle * moving_direction_waist
            new_angle_waist = max(min(new_angle_waist, 3.14), -3.14)  # Limit to -180 to 180 degrees
            bot.arm.set_single_joint_position("waist", new_angle_waist, moving_time=moving_time)
        time.sleep(0.01)  # Short delay for smooth continuous movement
        
def move_elbow():
    global moving_direction_elbow, bot
    while True:
        if moving_direction_elbow != 0:
            current_angle_elbow = bot.arm.get_single_joint_command("elbow")
            new_angle_elbow = current_angle_elbow + step_angle * moving_direction_elbow
            new_angle_elbow = max(min(new_angle_elbow, 1.60), -2.11)  # Limit to -121 to 92 degrees
            bot.arm.set_single_joint_position("elbow", new_angle_elbow, moving_time=moving_time)
        time.sleep(0.01)  # Short delay for smooth continuous movement
        
def move_shoulder():
    global moving_direction_shoulder, bot
    while True:
        if moving_direction_shoulder != 0:
            current_angle_shoulder = bot.arm.get_single_joint_command("shoulder")
            new_angle_shoulder = current_angle_shoulder + step_angle * moving_direction_shoulder
            new_angle_shoulder = max(min(new_angle_shoulder, 1.87), -1.87)  # Limit to -107 to 107 degrees
            bot.arm.set_single_joint_position("shoulder", new_angle_shoulder, moving_time=moving_time)
        time.sleep(0.01)  # Short delay for smooth continuous movement
        
def move_wrist():
    global moving_direction_wrist, bot
    while True:
        if moving_direction_wrist != 0:
            current_angle_wrist = bot.arm.get_single_joint_command("wrist_angle")
            new_angle_wrist = current_angle_wrist + step_angle * moving_direction_wrist
            new_angle_wrist = max(min(new_angle_wrist, 1.57), -1.57)  # Limit to -90 to 90 degrees
            bot.arm.set_single_joint_position("wrist_angle", new_angle_wrist, moving_time=moving_time)
        time.sleep(0.01)  # Short delay for smooth continuous movement
        
def control_gripper():
    global gripper_action, bot
    while True:
        if gripper_action == 1:
            bot.gripper.release()  # Use 'release()' to open the gripper
            gripper_action = 0
        elif gripper_action == -1:
            bot.gripper.grasp()  # Use 'grasp()' to close the gripper
            gripper_action = 0
        time.sleep(0.01)  # Short delay for smooth continuous movement

def main():
    global bot
    bot = InterbotixManipulatorXS("px100", "arm", "gripper")
    robot_startup()
    
    # Move the arm to the home position
    bot.arm.go_to_home_pose()
    time.sleep(2)  # Wait for 2 seconds
    print("Use LEFT and RIGHT arrow keys to move the waist joint continuously.")
    print("Use UP and DOWN arrow keys to move the elbow joint (flipped control). Press 'a' and 'd' to move the shoulder, and 'w' and 's' to move the wrist. Press 'o' to open the gripper, 'c' to close the gripper. Press ESC to quit.")
    
    # Start the key listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    # Start the movement threads for each joint
    waist_thread = threading.Thread(target=move_waist)
    elbow_thread = threading.Thread(target=move_elbow)
    shoulder_thread = threading.Thread(target=move_shoulder)
    wrist_thread = threading.Thread(target=move_wrist)
    gripper_thread = threading.Thread(target=control_gripper)
    waist_thread.daemon = True
    elbow_thread.daemon = True
    shoulder_thread.daemon = True
    wrist_thread.daemon = True
    gripper_thread.daemon = True
    waist_thread.start()
    elbow_thread.start()
    shoulder_thread.start()
    wrist_thread.start()
    gripper_thread.start()
    
    try:
        listener.join()  # Wait until the listener is stopped
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
