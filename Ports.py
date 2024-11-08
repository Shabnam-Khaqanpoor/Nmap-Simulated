import re
import time
import socket


def is_port_open(ip, port, num_requests=1, timeout=1):
    # Checks if a specific port on a given IP address is open
    delays = []
    result = ""

    # Repeat check based on the number of requests
    for request in range(num_requests):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Set socket timeout
        start_time = time.perf_counter()  # Start timer to measure response time

        try:
            sock.connect((ip, port))  # Try to connect to the specified IP and port
            end_time = time.perf_counter()
            delay = end_time - start_time  # Calculate response time
            delays.append(delay)  # Store delay in list
            result += f"\nPort {port} on {ip} is open.                   Response time: {round(delay * 1000, 3)} ms"
        except (socket.timeout, socket.error):
            result += f"\nPort {port} on {ip} is closed."  # Report port as closed if connection fails
        time.sleep(0.2)  # Short pause between requests

    # Calculate and display average response time if multiple requests were made
    if delays and num_requests > 1:
        average_delay = sum(delays) / len(delays)
        result += f"\n\nAverage response time for {num_requests} requests: {round(average_delay * 1000, 3)} ms"

    # Display service name and DNS or IP information
    result += f"     {get_service_name(port)}      {dns_or_ip(ip)}\n"
    return result


def check_range_of_open_ports(ip, start_port, end_port, num_requests=1, timeout=1):
    # Checks a range of ports on a given IP to see if they are open
    result = ""
    for port in range(start_port, end_port + 1):
        result += f"{is_port_open(ip, port, num_requests, timeout)}\n"  # Check each port in the range
    return result


def get_service_name(port, protocol='tcp'):
    # Returns the service name associated with a given port
    try:
        service_name = socket.getservbyport(port, protocol)  # Look up service name for the port
        return f"Service name: {service_name}"
    except OSError:
        return "Unknown service"  # Return "Unknown service" if no match is found


def get_host_name(ip):
    # Returns the hostname for a given IP address, if available
    try:
        host = socket.gethostbyaddr(ip)  # Reverse DNS lookup
        return f"Hostname for IP: {host[0]}"
    except socket.herror:
        return "Hostname not found for IP address."  # If no hostname is found, report it


def get_ip_address(hostname):
    # Returns the IP address for a given hostname
    try:
        ip_address = socket.gethostbyname(hostname)  # Resolve hostname to IP address
        return f"IP address of {hostname}: {ip_address}"
    except socket.gaierror:
        return f"Unable to get IP address for {hostname}"  # Return error message if resolution fails


def dns_or_ip(ip):
    # Determines if the input is an IP address or hostname and returns the appropriate information
    match = re.search(r'\d+$', ip)
    if match:
        return get_host_name(ip)  # If input ends in digits, assume it's an IP and get hostname
    else:
        return get_ip_address(ip)  # Otherwise, assume it's a hostname and get IP address
