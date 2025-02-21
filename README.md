# Nmap Simulation Project 🚀

## Overview 🌐

This project simulates basic functionalities of the popular `nmap` tool using a custom-built server and client application. The server allows clients to perform network operations such as pinging a host, checking open ports, and testing response times to ports. 🖧💻

The simulation includes:
- **Ping** using ICMP to check if a host is online.
- **Port Scanning** to check if specific ports on a host are open.
- **Response Time** to measure how quickly a port responds.

---

## Features ✨

- **/ping <hostname/IP>**: Sends an ICMP ping request to check if a host is online. 🌍
- **/port <hostname/IP> <start_port> <end_port> <#num_requests>**: Scans a range of ports to check if they are open. 🔓
- **/res_time <hostname/IP> <port> <#num_requests>**: Measures the response time of a specific port. ⏱️
- **/GET <user_ID>**: Retrieves information about a specific user. 📥
- **/POST <user_name> <user_age>**: Adds a new user to the server. ➕

---
## Example Commands 💬

- **Ping a host**:
  ```bash
  /ping 192.168.1.1
  /ping google.com
  ```

- **Check open ports**:
  ```bash
  /port 192.168.1.1 22 80 5
  /port google.com 22 80 5
  ```

- **Check response time for a port**:
  ```bash
  /res_time 192.168.1.1 80 3
  /res_time google.com 80 3
  ```

- **Get user information**:
  ```bash
  /GET user1
  ```

- **Add new user**:
  ```bash
  /POST "John Doe" 28
  ```

---
