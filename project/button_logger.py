import RPi.GPIO as GPIO
import time
from monitor import log_entry, init_db

BUTTON_PINS = {
    "Computer Lab": 17,
    "Chemistry Lab": 27,
    "Faculty": 22
}

button_state = {lab: False for lab in BUTTON_PINS}

def setup():
    GPIO.setmode(GPIO.BCM)
    for pin in BUTTON_PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    init_db()

def loop():
    try:
        while True:
            for lab, pin in BUTTON_PINS.items():
                if GPIO.input(pin) == GPIO.HIGH:
                    action = "Time In" if not button_state[lab] else "Time Out"
                    log_entry(lab, action)
                    print(f"{lab} - {action} logged.")
                    button_state[lab] = not button_state[lab]
                    while GPIO.input(pin) == GPIO.HIGH:
                        pass
        time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__name__":
    setup()
    loop()