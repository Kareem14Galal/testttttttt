from gpiozero import DistanceSensor, Servo
import time
import BlynkLib
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import subprocess

blynk = BlynkLib.Blynk("nrOGpm8yNmEz8gINC40NzKjFyp6u5STK", server="blynk.cloud", port=80)

sensor1 = DistanceSensor(echo=5, trigger=6)     # entrance
sensor2 = DistanceSensor(echo=15, trigger=14)   # exit

i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

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

# Camera
def take_picture():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"/home/pi/security_{timestamp}.jpg"
    subprocess.run(["rpicam-still", "-o", filename, "-n", "-t", "1000"])
    print(f"[OK] Picture saved: {filename}")


def open_servo(direction, hold_time=2):
    if direction == "enter":
        print("Please scan your card...")

        # Wait up to 5 seconds for a card
        start = time.time()
        uid = None
        while time.time() - start < 5 and uid is None:
            uid = pn532.read_passive_target(timeout=0.5)

        if uid:
            uid_str = ''.join(['%02x' % i for i in uid])
            print("Card UID:", uid_str)

            if uid_str == "03af3435":   
                servo.max()
                print("Access granted - Door opened RIGHT (entry)")
                time.sleep(hold_time)
                servo.mid()
                return True
            else:
                take_picture()
                print("? Access denied - Wrong card")
                return False
        else:
            take_picture()
            print("? Access denied - No card detected")
            return False

    elif direction == "exit":
        servo.min()
        print("Door opened LEFT (exit)")
        time.sleep(hold_time)
        servo.mid()
        return True


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
        state2 = False
        if open_servo("enter"):
            count += 1
            entered_count += 1
        else:
            print("Entry blocked")

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
    blynk.virtual_write(0, entered_count)
    blynk.virtual_write(2, exited_count)
    blynk.virtual_write(1, count)

    print(f"Inside: {count} | Entered: {entered_count} | Exited: {exited_count} | i={i}")
    print("-" * 40)

    time.sleep(1)

