# Network Scanner (Python)

## Project Overview

This project implements a Python-based network scanner designed to discover active devices within a specified IP range. [cite_start]It leverages network protocols and Python libraries to provide insights into your local network's topology. [cite: 1]

## How It Works

The scanner operates by:
* [cite_start]Accepting a CIDR-based network address (e.g., `192.168.1.0/24`) as user input. [cite: 6]
* [cite_start]Extracting all valid host IP addresses from the provided subnet. [cite: 7]
* [cite_start]Sending ARP (Address Resolution Protocol) requests to each IP address to identify active devices. [cite: 8, 35]
* [cite_start]Collecting the MAC (Media Access Control) address of any responding device. [cite: 9]
* [cite_start]Attempting to resolve the hostname of discovered devices using reverse DNS lookup. [cite: 10, 67]
* [cite_start]Utilizing multi-threading to scan multiple devices concurrently, which speeds up the process. [cite: 11, 75]
* [cite_start]Displaying the discovered devices (IP, MAC, and Hostname) in a clear, tabular format. [cite: 12]

## Key Features

* [cite_start]**ARP-based Scanning:** Identifies active hosts using ARP requests. [cite: 8]
* [cite_start]**MAC Address Retrieval:** Collects hardware addresses of discovered devices. [cite: 9]
* [cite_start]**Hostname Resolution:** Attempts to find human-readable hostnames for IPs. [cite: 10]
* [cite_start]**Multi-threading:** Enhances scan speed for larger networks. [cite: 11]
* [cite_start]**User-friendly Input:** Accepts CIDR notation for flexible network range definition. [cite: 6]
* [cite_start]**Structured Output:** Presents scan results in an easy-to-read table. [cite: 12]

## Requirements

* Python 3.x
* [cite_start]`scapy` library: Install using `pip install scapy` [cite: 16, 39]

## Usage

1.  **Save the script:** Save the provided Python code as `network_scanner.py`.
2.  **Run with privileges:** This tool requires elevated permissions to interact with network packets.
    * **Windows:** Open your terminal or VS Code as **Administrator**.
    * [cite_start]**Linux:** Run the script using `sudo` (e.g., `sudo python network_scanner.py`). [cite: 82]
3.  **Execute the script:**
    ```bash
    python network_scanner.py
    ```
4.  [cite_start]**Enter network CIDR:** When prompted, provide your local network's CIDR (e.g., `192.168.1.0/24`). [cite: 6]

## Disclaimer

This Network Scanner project is developed for **educational and learning purposes only**. [cite_start]It demonstrates concepts related to network scanning, ARP protocols, and multi-threading in Python. [cite: 2, 20, 21]

* **Ethical Use:** This tool should only be used on networks for which you have explicit permission to scan. Unauthorized network scanning can be illegal and unethical.
* **No Warranty:** The tool is provided "as is" without any warranty, express or implied. The developers are not responsible for any misuse or damage caused by this software.
* [cite_start]**Permissions:** As this script interacts with low-level network packets, it requires administrator (Windows) or root (Linux) privileges to function correctly. [cite: 63, 82]
* **Network Behavior:** Scan results may vary based on network configuration, firewalls, and device activity. [cite_start]Some networks or devices may not respond to ARP requests. [cite: 85]
