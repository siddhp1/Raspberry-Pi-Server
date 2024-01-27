import RPi.GPIO as GPIO
import subprocess
import time

# Set the GPIO mode and pin for the power button
GPIO.setmode(GPIO.BCM)
power_button_pin = 21
GPIO.setup(power_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup LEDs
red_led_pin = 13
GPIO.setup(red_led_pin, GPIO.OUT)
GPIO.output(red_led_pin, GPIO.LOW)

yellow_led_pin = 6
GPIO.setup(yellow_led_pin, GPIO.OUT)
GPIO.output(yellow_led_pin, GPIO.LOW)

green_led_pin = 5
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.output(green_led_pin, GPIO.LOW)
 
# Initial state
in_sleep_mode = False
GPIO.output(green_led_pin, GPIO.HIGH)

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
    GPIO.output(green_led_pin, GPIO.LOW)
    GPIO.output(yellow_led_pin, GPIO.HIGH)
    
    time.sleep(1)  # Placeholder for sleep duration
    print("Exiting sleep mode.")

# Wake function
def wake_up():
    print("Waking up...")
    GPIO.output(yellow_led_pin, GPIO.LOW)
    GPIO.output(green_led_pin, GPIO.HIGH)

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
        GPIO.output(green_led_pin, GPIO.LOW)
        GPIO.output(yellow_led_pin, GPIO.LOW)
        GPIO.output(red_led_pin, GPIO.HIGH)
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])