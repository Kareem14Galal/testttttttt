from gpiozero import DistanceSensor, Servo
import time

sensor1 = DistanceSensor(echo=5, trigger=6)     # entrance
sensor2 = DistanceSensor(echo = 15, trigger = 14)

# People counting variables
count = 0
entered_count = 0
exited_count = 0

# State tracking
state1 = True
state2 = True
i = 1  # sequence flag

THS = 0.5  

# Servo setup
servo = Servo(17)


def open_servo(direction, hold_time=2):
    """Move servo to open in a direction, wait, then return to center"""
    if direction == "enter":
        servo.max()   # right
        print("Servo opened RIGHT (entry)")
    elif direction == "exit":
        servo.min()   # left
        print("Servo opened LEFT (exit)")
    
    time.sleep(hold_time)   # keep door open
    servo.mid()             # return to center
    time.sleep(0.5)         # small cooldown

while True:
        dist1 = sensor1.distance  # meters
        dist2 = sensor2.distance
        print(f"Dist1: {dist1*100:.1f} cm | Dist2: {dist2*100:.1f} cm")

        # Entry detection
        if dist1 < THS and i == 1 and state1:
            time.sleep(0.1)
            i = 2
            state1 = False
        elif dist2 < THS and i == 2 and state2:
            time.sleep(0.1)
            i = 1
            count += 1
            entered_count += 1
            state2 = False
            open_servo("enter")

        # Exit detection
        elif dist2 < THS and i == 1 and state2:
            time.sleep(0.1)
            i = 2
            state2 = False
        elif dist1 < THS and i == 2 and state1:
            time.sleep(0.1)
            count -= 1
            if count < 0:
                count = 0
            exited_count += 1
            i = 1
            state1 = False
            open_servo("exit")

        # Reset states when sensors clear
        if dist1 > THS + 0.05:
            state1 = True
        if dist2 > THS + 0.05:
            state2 = True

        # Debug output
        print(f"Dist1: {dist1*100:.1f} cm | Dist2: {dist2*100:.1f} cm")
        print(f"Inside: {count} | Entered: {entered_count} | Exited: {exited_count} | i={i}")
        print("-" * 40)

        time.sleep(1)