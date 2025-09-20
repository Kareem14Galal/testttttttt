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
