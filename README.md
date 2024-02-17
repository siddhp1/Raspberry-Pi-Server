# Raspberry Pi Server 

Customizable Python script to add a power/sleep button, LED status indicators, and an LCD information display to a Raspberry Pi server. 

## Table of Contents

1. [Setup](#setup)
2. [Usage](#usage)
3. [License](#license)

## Setup

### Physical Components
The following GPIO components are required to run this project:
- Raspberry Pi running Ubuntu Server
- 1x IC2 LCD16x2
- 2x Momentary push button
- 1x Red LED
- 1x Yellow LED
- 1x Green LED
- 3x 100Ω resistor
- 2x 1000Ω resistor
- Jumper wires

Connect the components following the diagram below:

<p align="center"><a><img width="600" alt="Thumbnail Image of ConnectX" src="https://raw.githubusercontent.com/siddhp1/Raspberry-Pi-Server/main/circuit-diagram.png"></a></p>

### Install Dependencies

To run this project, you will need to install the following dependencies:

1. **Install smbus2, psutil, and pytz:**

    ```bash
    $ sudo pip3 install smbus2 psutil pytz
    ```
2. **Install RPI GPIO:**

    ```bash
    $ sudo apt install python3-rpi.gpio
    ```

### Download Script

Next, download the script and configure the config and server files:

1. **Clone the repository:**

    ```bash
    $ git clone https://github.com/siddhp1/Raspberry-Pi-Server.git
    ```
2. **Navigate to the project directory:**

    ```bash
    $ cd repository
    ```
3. **Modify config file:**

    Adjust the pin settings to your wiring configuration and save the file

    ```bash
    $ sudo nano config.json
    ```
4. **Modify script:**

    Modify the script sleep settings with commands compatible with your system and relevant to your use case
    ```bash
    $ sudo nano server.py
    ```

### Setup Service

Finally, setup a service so the script runs in the background on startup:

1. **Create a service file:**

    ```bash
    $ sudo nano /etc/systemd/system/server.service
    ```
2. **Configure the service file:**

    ```bash
    [Unit]
    Description=Server
    After=multi-user.target

    [Service]
    # Edit this path to the script
    ExecStart=/usr/bin/python3 /path/to/your/script/server.py
    # Edit this path to the script working directory
    WorkingDirectory=/path/to/your/script/
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    # Change this user to the root user
    User=pi

    [Install]
    WantedBy=multi-user.target
    ```
3. **Enable the service:**

    ```bash
    $ sudo systemctl enable server.service
    ```
4. **Start the service:**

    ```bash
    $ sudo systemctl start server.service
    ```
5. **Check the service status:**

    ```bash
    $ sudo systemctl status server.service
    ```
    If there are any issues, the command will provide information. 
6. **Reboot your Raspberry Pi:**

    ```bash
    $ sudo reboot
    ```
    The script should automatically start when your Raspberri Pi turns on. 

## Usage

Once the service is setup, the script will automatically run on startup. 

The green LED will be on when the server is in its normal state, while the yellow LED will run when the server is in its sleep mode. The red LED will only flash prior to shutdown. 

To put the server in sleep and to lift the server from sleep, press the power button. Hold the power button for more than 3 seconds to shut down. 

The LCD display will show live system statistics, refreshed every 30 seconds. The cycle button will cycle between the different screens defined in the config file.

# License
This project is licensed under the MIT License.