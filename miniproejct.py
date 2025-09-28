from gpiozero import DistanceSensor, Servo
import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import subprocess
import paho.mqtt.client as mqtt
import ssl
import json


# MQTT broker
MQTT_BROKER = "bc9dc2eab7c04e9bbaf9474216ba75f6.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_INSIDE = "count/inside"
MQTT_TOPIC_ENTERED = "count/entered"
MQTT_TOPIC_EXITED = "count/exited"
MQTT_USERNAME = "Kareem"
MQTT_PASSWORD = "kareemGALAL13"


client = mqtt.Client(client_id = "pi")
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set(tls_version=ssl.PROTOCOL_TLS)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()


def publish_mqtt(topic, value):
    try:
        client.publish(topic, value)
        print(f"[MQTT] Published {value} to {topic}")
    except Exception as e:
        print("[MQTT ERROR]", e)
        

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

THS = 0.2 

# Servo setup
servo = Servo(17, min_pulse_width=0.0005, max_pulse_width=0.0025)


# Camera
def take_picture():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"/home/pi/security_photage/security_{timestamp}.jpg"
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

            if uid_str == "b359b834":   
                servo.max()
                print("Access granted - Door opened RIGHT (entry)")
                time.sleep(hold_time)
                servo.mid()
                return True
            else:
                take_picture()
                print("Access denied - Wrong card")
                return False
        else:
            take_picture()
            print("Access denied - No card detected")
            return False

    elif direction == "exit":
        servo.min()
        print("Door opened LEFT (exit)")
        time.sleep(hold_time)
        servo.mid()
        return True


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

    print(f"Inside: {count} | Entered: {entered_count} | Exited: {exited_count} | i={i}")
    print("-" * 40)
    publish_mqtt(MQTT_TOPIC_INSIDE, count)
    publish_mqtt(MQTT_TOPIC_ENTERED, entered_count)
    publish_mqtt(MQTT_TOPIC_EXITED, exited_count)
    
    time.sleep(0.5)
