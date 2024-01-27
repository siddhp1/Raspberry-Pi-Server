import RPi.GPIO as GPIO
import subprocess
import time

# Set the GPIO mode and pin for the power button
GPIO.setmode(GPIO.BCM)
power_button_pin = 21
GPIO.setup(power_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initial state
in_sleep_mode = False

'''
Still need to add the functionality
to put the pi in a low power "sleep" mode

Stuff to add:
- Turn off the LCD1602
- Suspend command
- Power GPIO pins using auxillary power so that they turn off with the shutdown command
'''

# Sleep function
def sleep_mode():
    print("Entering sleep mode...")
    # Add code to enter sleep mode here
    time.sleep(1)  # Placeholder for sleep duration
    print("Exiting sleep mode.")

# Wake function
def wake_up():
    print("Waking up...")

# Check for button press
while True:
    GPIO.wait_for_edge(power_button_pin, GPIO.FALLING)

    # Calculate duration of the button press
    start_time = time.time()
    while GPIO.input(power_button_pin) == GPIO.LOW:
        time.sleep(0.1)
    duration = time.time() - start_time

    # Either toggle sleep or shutdown based on length of press
    if duration < 3:
        if in_sleep_mode:
            wake_up()
            in_sleep_mode = False
        else:
            sleep_mode()
            in_sleep_mode = True
    else:
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])