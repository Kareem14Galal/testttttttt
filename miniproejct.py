rom gpiozero import DistanceSensor, Servo
import time
import BlynkLib

blynk = BlynkLib.Blynk("nrOGpm8yNmEz8gINC40NzKjFyp6u5STK", server="blynk.cloud", port=80)

sensor1 = DistanceSensor(echo=5, trigger=6)     # entrance
sensor2 = DistanceSensor(echo = 15, trigger = 14)

# People counting variables
count = 0
entered_count = 0
exited_count = 0


state1 = True
state2 = True
i = 1  

THS = 0.5  


servo = Servo(17)


def open_servo(direction, hold_time=2):
    if direction == "enter":
        servo.max()   
        print("Servo opened RIGHT (entry)")
    elif direction == "exit":
        servo.min()   
        print("Servo opened LEFT (exit)")
    
    time.sleep(hold_time)   # keep door open
    servo.mid()             # return to center
    time.sleep(0.5)         # small cooldown

while True:
        blynk.run()
        
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

        
        if dist1 > THS + 0.05:
            state1 = True
        if dist2 > THS + 0.05:
            state2 = True

        
        blynk.virtual_write(0, entered_count)
        blynk.virtual_write(2, exited_count)
        blynk.virtual_write(1, count)

        print(f"Dist1: {dist1*100:.1f} cm | Dist2: {dist2*100:.1f} cm")
        print(f"Inside: {count} | Entered: {entered_count} | Exited: {exited_count} | i={i}")
        print("-" * 40)
        
        time.sleep(1)

