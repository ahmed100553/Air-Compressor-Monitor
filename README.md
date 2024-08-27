
# Air Compressor Condition Monitoring and Reporting System

## Project Overview

This project focuses on developing an advanced monitoring and reporting system for air compressors used in industrial applications. The system enhances the reliability, efficiency, and safety of air compressors by monitoring air, oil, and electrical systems through various sensors and a Raspberry Pi. The data collected is processed and visualized in real-time, enabling proactive maintenance and reduced downtime.

## Features

- **Real-time Monitoring:** Continuous monitoring of air pressure, oil pressure, temperature, and humidity.
- **Predictive Maintenance:** Early detection of potential issues to prevent failures.
- **Cost-effective:** Uses affordable sensors and components to deliver a robust solution.
- **Data Visualization:** Real-time and offline data visualization using Streamlit.

## Hardware Components

- **Raspberry Pi 4 Model B:** The core processing unit for data collection and analysis.
- **Pressure Transducer Sensors (300 PSI & 100 PSI):** Used for monitoring air and oil pressure.
- **HYT939 Humidity Sensor:** Measures humidity in the air system.
- **FD-Frienda-F5166 K-Type Temperature Sensor:** Measures temperature at critical points.
- **Three-phase Multi-function Smart Meter:** Monitors electrical parameters such as current, voltage, and phase status.

## Booting the Raspberry Pi

1. **Download and Install Raspberry Pi OS:**
   - Download Raspberry Pi OS and use the Raspberry Pi Imager to install it on a microSD card.

2. **Preconfigure the Following:**
   - Username and password
   - WiFi credentials
   - Device hostname
   - Time zone
   - Keyboard layout
   - Remote connectivity

## Installing Python Dependencies

1. **Update the System:**
   ```bash
   sudo apt-get update
   ```

2. **Install Essential Development Tools:**
   ```bash
   sudo apt-get install build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
   ```

3. **Install Python 3.10:**
   ```bash
   wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tar.xz
   tar -xvf Python-3.10.0.tar.xz
   cd Python-3.10.0
   ./configure --enable-optimizations
   make -j 4
   sudo make altinstall
   ```

4. **Verify the Installation:**
   ```bash
   python3.10 --version
   ```

## Setting Up a Virtual Environment

1. **Create a Project Directory:**
   ```bash
   mkdir capstone
   ```

2. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv envCapstone
   source envCapstone/bin/activate
   ```

## Install Pandas and Streamlit

1. **Install Required Libraries:**
   ```bash
   pip install pandas
   pip install streamlit
   ```

2. **Validate Streamlit Installation:**
   ```bash
   streamlit hello
   ```

## Install GPIO and its Dependencies

1. **Install GPIO and Supporting Packages:**
   ```bash
   sudo apt-get install build-essential python-dev python-smbus git
   pip install RPi.GPIO
   ```

2. **Install Additional Python Libraries:**
   ```bash
   pip3 install adafruit-circuitpython-max31855
   pip3 install adafruit-circuitpython-ads1x15
   ```

3. **Configure the Raspberry Pi for RS485 Communication:**
   - Edit the configuration file:
     ```bash
     sudo nano /boot/config.txt
     dtoverlay=sc16is752-spi1,int_pin=24
     sudo reboot
     ```

4. **Install Python3 and Serial Library:**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   sudo apt-get install python3-serial
   ```

5. **Install WiringPi:**
   - Fetch and build the package:
     ```bash
     sudo apt install git
     git clone https://github.com/WiringPi/WiringPi.git
     cd WiringPi
     ./build debian
     mv debian-template/wiringpi-3.0-1.deb .
     sudo apt install ./wiringpi-3.0-1.deb
     ```

6. **Extract and Install RS485 HAT Code:**
   ```bash
   sudo apt-get install p7zip-full
   wget https://files.waveshare.com/upload/4/44/2-CH_RS485_HAT_code.7z
   7z x 2-CH_RS485_HAT_code.7z
   sudo chmod 777 -R  2-CH_RS485_HAT
   cd 2-CH_RS485_HAT/
   ```

7. **Run the Example Python Script:**
   ```bash
   cd python 
   cd examples
   sudo python main.py
   ```

8. **Begin RS485 Communication:**
   ```python
   RS485.RS485_CH2_begin(115200)
   RS485.RS485_CH1_begin(115200)
   ```

## Software Components

The software for this project is primarily written in Python, leveraging several key libraries:

- **Streamlit:** For creating real-time data visualization dashboards.
- **Pandas:** For data manipulation and processing.
- **Plotly Express:** For generating interactive plots.
- **MinimalModbus:** For communication with the multi-function smart meter using Modbus RTU.

### Key Python Scripts

1. **HYT939-Sensor.py:**
   - Reads humidity and temperature data from the HYT939 sensor via I2C.
   - Outputs the readings to the console.

2. **pressureReadings.py:**
   - Collects pressure data from multiple pressure transducers using the ADS1115 ADC.
   - Saves the readings to a CSV file with a timestamp.

3. **readADS1115.py & readadsDiff.py:**
   - Interfaces with the ADS1115 ADC to read analog inputs and convert them to meaningful pressure values.

4. **sensorsAq2.py:**
   - Aggregates readings from multiple sensors, including pressure, temperature, and humidity.
   - Designed for streamlined data collection and integration.

5. **stData.py & StDataCollection.py:**
   - Visualizes real-time sensor data using Streamlit.
   - Provides an interactive interface for monitoring and analyzing sensor data over time.

### Installation and Setup

1. **Hardware Setup:**
   - Connect the sensors to the Raspberry Pi according to the provided schematics.
![image](https://github.com/user-attachments/assets/5a786d80-fd94-4dac-a723-299a73d3efac)
![image](https://github.com/user-attachments/assets/806b06e3-1d41-4c61-8c56-95408ffe6f2a)
![image](https://github.com/user-attachments/assets/81f08331-0cdf-4e0a-aae7-b3e92095b523)
![image](https://github.com/user-attachments/assets/1e62d8b3-fb6d-4aeb-adbc-32e8e62bd6f8)


2. **Running the System:**
   - Start the data collection script:
     ```bash
     python pressureReadings.py
     ```
   - Launch the Streamlit dashboard for real-time visualization:
     ```bash
     streamlit run stData.py
     ```

### Data Visualization

- **Real-time Monitoring:** The Streamlit app (`stData.py`) visualizes sensor data as it is collected, providing interactive plots and metrics.
- **Offline Analysis:** The `StDataCollection.py` script allows users to upload and analyze previously collected data.
![image](https://github.com/user-attachments/assets/aafd96b4-9850-484f-9ea6-b21a9bbcbf98)


### Future Enhancements

- **Additional Sensor Integration:** Expand the system to monitor more parameters or include different types of sensors.
- **Cloud Integration:** Enable remote monitoring and data storage in the cloud for broader access and analysis.
