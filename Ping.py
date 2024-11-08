import time
import socket
import struct
import select
import random

# Constants for ICMP packet types and error descriptions
ICMP_ECHO_REQUEST = 8  # ICMP type for echo requests
ICMP_CODE = socket.getprotobyname('icmp')  # Protocol number for ICMP
ERROR_DESCR = {
    1: ' - Note that ICMP messages can only be sent from processes running as root.',
    10013: ' - Note that ICMP messages can only be sent by users or processes with administrator rights.'
}

def checksum(source_string):
    # Calculate checksum for a given input string (used for error-checking in packets)
    sum = 0
    count_to = (len(source_string) // 2) * 2
    count = 0

    # Sum all 16-bit words in the string
    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff
        count += 2

    # Add any remaining byte (if string length is odd)
    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    # Add high 16 bits to low 16 bits and invert to get checksum
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id):
    # Create an ICMP packet with a specified ID
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = bytes(192 * 'Q', 'utf-8')  # Payload with repetitive character 'Q'
    my_checksum = checksum(header + data)  # Calculate checksum for packet data

    # Re-pack the header with computed checksum
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, 1)
    return header + data  # Combine header and data into a single packet

def do_one(dest_addr, timeout=1):
    # Sends a single ICMP echo request to the destination address
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
    except socket.error as e:
        # Check for permissions error and re-raise with description if necessary
        if e.errno in ERROR_DESCR:
            raise socket.error(''.join((e.args[1], ERROR_DESCR[e.errno])))
        raise

    try:
        host = socket.gethostbyname(dest_addr)  # Resolve destination address
    except socket.gaierror:
        return  # If the host can't be resolved, exit the function

    packet_id = int((id(timeout) * random.random()) % 65535)  # Generate packet ID
    packet = create_packet(packet_id)  # Create the packet
    while packet:
        sent = my_socket.sendto(packet, (dest_addr, 1))  # Send packet to destination
        packet = packet[sent:]  # Continue sending if packet is not fully sent

    delay = receive_ping(my_socket, packet_id, time.time(), timeout)  # Measure delay
    my_socket.close()  # Close the socket after sending
    return delay  # Return round-trip time

def receive_ping(my_socket, packet_id, time_sent, timeout):
    # Receives the ping response and calculates round-trip delay
    time_left = timeout
    while True:
        started_select = time.time()
        ready = select.select([my_socket], [], [], time_left)  # Wait for socket to be ready
        how_long_in_select = time.time() - started_select
        if ready[0] == []:
            return  # Timeout occurred, no response received

        time_received = time.time()
        rec_packet, addr = my_socket.recvfrom(1024)  # Receive packet from socket
        icmp_header = rec_packet[20:28]  # Extract ICMP header from packet

        # Unpack header fields to verify packet ID
        type, code, checksum, p_id, sequence = struct.unpack('bbHHh', icmp_header)
        if p_id == packet_id:
            return time_received - time_sent  # Return delay if IDs match

        # Update time remaining for waiting
        time_left -= time_received - time_sent
        if time_left <= 0:
            return  # Timeout if no response received in time

def is_host_online(host, timeout=1):
    # Check if the specified host is online by sending an ICMP request
    delay = do_one(host, timeout)
    if delay is None:
        return f"{host} is offline."  # Return offline status if no response

    else:
       return f"{host} is online.                   Response time: {round(delay * 1000, 2)} ms"  # Return response time if online
