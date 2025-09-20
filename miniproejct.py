import BlynkLib
import time

blynk = BlynkLib.Blynk("nrOGpm8yNmEz8gINC40NzKjFyp6u5STK", server="blynk.cloud", port=80)

def send_data():
    try:
        blynk.virtual_write(22, entred)
        blynk.virtual_write(23, exited)
        blynk.virtual_write(5, inside)

        print("entred:", entred)
        print("exited:", exited)
        print("inside:", inside)

    except RuntimeError as e:
        print("error:", e)


last_time = time.time()
while True:
    blynk.run()
    
    
    if time.time() - last_time > 1:
        send_data()
        last_time=time.time()
#################################################

import board
import busio
from adafruit_pn532.i2c import PN532_I2C

# I2C connection setup
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to read NFC tags
pn532.SAM_configuration()

print("Waiting for an NFC tag...")

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        print(f"Found NFC tag with UID: {uid.hex()}")
