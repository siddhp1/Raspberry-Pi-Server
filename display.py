import subprocess
import threading
import smbus
import psutil
import json
from time import sleep, strftime
from datetime import datetime, timedelta
import pytz
from LCD1602 import CharLCD1602
import RPi.GPIO as GPIO

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)
    
# Get cycle button GPIO pin from config file
CYCLE_BUTTON_PIN = config.get("Button Pin", 18)

# Get screen layouts from config file
screens = config.get("Screens", [])

# Initialize the LCD1602
lcd1602 = CharLCD1602()

# Initialize GPIO 
GPIO.setmode(GPIO.BCM)
GPIO.setup(CYCLE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to get system time
def get_time_now(timezone='EST'):
    # Get the current time in the specified time zone
    current_time = datetime.now(pytz.timezone(timezone))
    # Format and return the time as a string
    return current_time.strftime('%H:%M:%S')

# Function to get system uptime
def get_uptime():
    uptime_bytes = subprocess.check_output("awk '{print $1}' /proc/uptime", shell=True)
    uptime_str = uptime_bytes.decode('utf-8').strip()
    uptime_seconds = float(uptime_str)
    uptime_timedelta = timedelta(seconds=uptime_seconds)

    # Extract days, hours, minutes, and seconds
    days = uptime_timedelta.days
    hours, remainder = divmod(uptime_timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format and return the result
    formatted_result = f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_result

# Function to get IP address
def get_ip_address():
    global last_ip_address
    try:
        ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode('utf-8').strip()
        # Return the results
        last_ip_address = ip_address
        return ip_address
    # Use the last updated data on error
    except subprocess.CalledProcessError:
        return last_ip_address

# Function to get network usage
def get_network_usage(interface='eth0'):
    global last_network_usage
    try:
        net_stats = psutil.net_io_counters(pernic=True)[interface]
        sent_bytes = net_stats.bytes_sent
        recv_bytes = net_stats.bytes_recv
        # Convert bytes to megabytes (MB)
        sent_mb = sent_bytes / (1024 * 1024)
        recv_mb = recv_bytes / (1024 * 1024)
        # Round values to integers
        sent_mb = round(sent_mb)
        recv_mb = round(recv_mb)
        # Return the results
        last_network_usage = f'{sent_mb}/{recv_mb} MB'
        return f'U:{sent_mb}/{recv_mb} MB'
    except KeyError:
        return 'Network Usage: N/A (Invalid Interface)'

# Function to get CPU temperature
def get_cpu_temp():
    global last_cpu_temp
    try:
        # Read the temperature file
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
            cpu_temp = temp_file.read()
            # Return the results
            last_cpu_temp = '{:.2f}'.format(float(cpu_temp) / 1000) + 'C'
            return last_cpu_temp
    # Use the last updated data on error
    except FileNotFoundError:
        return last_cpu_temp 

# Function to get CPU usage
def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    # Return the result
    last_cpu_usage = f"{cpu_percent}%"
    return f"{cpu_percent}%"

# Get RAM usage
def get_ram_usage():
    global last_ram_usage
    try:
        ram_usage = subprocess.check_output("free -m | awk 'NR==2{printf \"%s/%s MB\", $3, $2}'", shell=True).decode('utf-8').strip()
        # Return the result
        last_ram_usage = ram_usage
        return ram_usage
    # Use the last updated data on error
    except subprocess.CalledProcessError:
        return last_ram_usage

# Get Disk usage
def get_disk_usage():
    global last_disk_usage
    try:
        # Get used and total disk space
        df_output = subprocess.check_output("df -h / | awk 'NR==2{print $3,$2}'", shell=True).decode('utf-8').strip().split()
        # Convert used and total disk space to floats
        used_disk = float(df_output[0].strip('G'))
        total_disk = float(df_output[1].strip('G'))
        # Return the result
        last_disk_usage = f"{used_disk}/{total_disk}GB"
        return last_disk_usage
    # Use the last updated data on error
    except subprocess.CalledProcessError:
        return last_disk_usage
    
# Lock for thread synchronization
update_lock = threading.Lock()

# Thread to update data in the background every 30 seconds
def update_data():
    global last_ip_address, last_cpu_temp, last_cpu_usage, last_ram_usage, last_disk_usage
    
    # Call functions to update information
    while True:
        with update_lock:
            last_ip_address = get_ip_address()
            last_network_usage = get_network_usage()
            last_cpu_temp = get_cpu_temp()
            last_cpu_usage = get_cpu_usage()
            last_ram_usage = get_ram_usage()
            last_disk_usage = get_disk_usage()
        # Sleep for 30 seconds before the next update
        sleep(30)
        
# Thread for updating the display every second
def display_thread():
    global screen
    
    # Update the display every second
    while True:
        update_display(screen)
        sleep(1)

# Function for updating the screen
def update_display(screen):
    # Clear the display
    lcd1602.clear()
    with update_lock:
        if 0 <= screen < len(screens):
            # Get the screen config
            screen_config = screens[screen]
            top_content = screen_config.get("Top", "")
            bottom_content = screen_config.get("Bottom", "")
            
            # Display text
            if top_content:
                display_text(top_content, 0)
            if bottom_content:
                display_text(bottom_content, 1)

# Function for displaying text on the display
def display_text(content, row):
    # Display data with proper formatting
    if content.lower() == "system_time":
        lcd1602.write(4, row, get_time_now())
    elif content.lower() == "uptime":
        lcd1602.write(0, row, 'UP: ' + get_uptime())
    elif content.lower() == "ip":
        lcd1602.write(2, row, last_ip_address)
    elif content.lower() == "network_usage":
        lcd1602.write(0, row, last_network_usage)
    elif content.lower() == "cpu_temp":
        lcd1602.write(0, row, 'CPU TEMP: ' + last_cpu_temp)
    elif content.lower() == "cpu_usage":
        lcd1602.write(0, row, 'CPU USAGE: ' + last_cpu_usage)
    elif content.lower() == "ram_usage":
        lcd1602.write(0, row, 'RAM: ' + last_ram_usage)
    elif content.lower() == "disk_usage":
        lcd1602.write(0, row, 'DISK: ' + last_disk_usage)

# Thread for checking buttons every 0.1 seconds
def button_thread():
    global screen
    while True:
        if debounce_button(CYCLE_BUTTON_PIN):
            # Cycle screen
            screen = (screen + 1) % len(screens)
        sleep(0.1)
        
# Debounce period
def debounce_button(pin):
    # Sleep for 0.08 seconds to prevent double press
    sleep(0.08)
    return GPIO.input(pin) == GPIO.LOW

# Main program loop
def loop():
    lcd1602.init_lcd()
    global screen
    
    # Start the background thread for data update
    update_thread = threading.Thread(target=update_data)
    update_thread.daemon = True  # This makes the thread exit when the main program exits
    update_thread.start()

    # Start the display update thread
    display_update_thread = threading.Thread(target=display_thread)
    display_update_thread.daemon = True
    display_update_thread.start()

    # Start the button checking thread
    button_check_thread = threading.Thread(target=button_thread)
    button_check_thread.daemon = True
    button_check_thread.start()

    # Main thread sleeps
    while True:
        sleep(10)  # You can adjust the sleep time as needed

# Clean up before the program exits
def destroy():
    GPIO.cleanup()
    lcd1602.clear()
    
# Run program   
if __name__ == '__main__':
    screen = 0
    try:
        loop()
    except KeyboardInterrupt:
        destroy()