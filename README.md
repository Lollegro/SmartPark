# SmartPark

## Description
The **SmartPark** project is an IoT-based system that automates **access control** and **environmental monitoring** for a garage using multiple sensors, actuators, and cloud connectivity.

A vehicle can enter the garage when it is available and exit only after entering the correct authentication code.  
It also includes a **safety alarm** that triggers in case of high temperature, initiating an **emergency evacuation**.

---

## System Architecture

### Hardware Overview
The system uses **two ESP32 microcontrollers**:

- **Primary ESP32:** handles sensors, actuators, logic, and MQTT communication.  
- **Secondary ESP32:** manages the external display, traffic light (LEDs), and buzzer.

### Components
- 2 × OLED **SSD1306 displays**
- 1 × **DHT22** temperature and humidity sensor  
- 1 × **Traffic light** (three LEDs)  
- 1 × **28BYJ-48 stepper motor** for barrier control  
- 1 × **4x4 Keypad** for code entry  
- 2 × **HC-SR04 ultrasonic sensors** for vehicle detection  
- 1 × **Passive buzzer** for alarms  

---

## Remote Management
A **Node-RED dashboard** provides full remote control and monitoring via the **MQTT** protocol  
(using the public broker `test.mosquitto.org`).

Through the dashboard, users can:

-  Open or close the barrier remotely  
-  Adjust parameters such as code length, temperature threshold, and distance sensitivity  
-  Activate or deactivate the alarm state  
-  View live sensor data and statistics  

---

##  System Features

-  **Authentication system:** Generates random numeric codes for vehicle exit  
-  **Environmental monitoring:** Real-time temperature and humidity readings  
-  **Emergency management:** Detects overheating and triggers evacuation  
-  **Dual-display system:**  
  - Internal display → sensor data & feedback  
  - External display → system status  
-  **Traffic light control:** Indicates garage availability (red/yellow/green LEDs)  
-  **Remote data logging:** Saves emergency history (timestamp and duration) in Node-RED  

---

##  Dashboard Overview

The Node-RED dashboard is divided into three sections:

1. **Remote Control** – barrier, alarm, and system parameters  
2. **Statistics** – temperature, humidity, and entry graphs over time  
3. **Readings** – current measurements and garage state/code  

### Dashboard Flows
- **Input Flow:** Handles MQTT inputs and user actions  
- **Output Flow:** Displays data, graphs, and logs emergencies via JavaScript  
- **Style Flow:** Customizes the dashboard’s appearance using CSS  

---

##  Conclusion
The **Smart Garage** project successfully integrates hardware and software into a secure and automated access control system.  
It demonstrates IoT principles such as **sensor integration**, **MQTT communication**, **cloud data exchange**, and **remote monitoring**, resulting in a connected, intelligent garage that enhances both **convenience** and **safety**.
