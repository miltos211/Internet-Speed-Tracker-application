# Internet Speed Tracker Application

## Overview
The Internet Speed Tracker application is designed to measure and analyze various aspects of network performance. It provides insights into internet connection quality, helping users understand and optimize their online experiences.

## Goals of the Project
The project aims to achieve the following goals:

1. **Jitter**: Measure and track variation in time between packets arriving to provide insights into the stability of a user's internet connection.
2. **Packet Loss**: Measure and log packet loss to help users identify problems in their network.
3. **DNS Resolution Time**: Measure DNS resolution time to diagnose slow website loading times not related to raw bandwidth limitations.
4. **TCP/UDP Connection Establishment Time**: Measure TCP/UDP connection establishment time to assess the responsiveness of services.
5. **Download Speed**: Measure and log the rate at which data is downloaded from the internet to the user's device.
6. **Upload Speed**: Measure and log the rate at which data is uploaded from the user's device to the internet.
7. **Ping**: Measure and display ping times for both upload and download to assess the efficiency of the data transmission.
8. **BBC Website Load Time Test**: Provide a real-world application test to measure how long it takes for a complete webpage to load under current internet speeds.

## Scripts Overview

### speedtest.net.py
This script utilizes the Speedtest library to perform internet speed tests. It measures download speed, upload speed, latency, and excludes server information. The results are saved to a CSV file with timestamps.

### fast.com.py
This script uses Selenium to automate speed tests on the fast.com website. It measures download speed, upload speed, latency, and bufferbloat. The results are saved to a CSV file with timestamps.

## License
This project is licensed under the GNU General Public License v3.0.
