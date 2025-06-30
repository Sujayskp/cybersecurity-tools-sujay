import scapy.all as scapy # For creating and sending network packets 
import ipaddress # For parsing CIDR notation and generating IP addresses 
import threading # For running scan tasks concurrently 
import queue # For thread-safe storage of results 
import socket # For resolving hostnames from IP addresses 
import sys # For exiting the script gracefully

# --- Configuration ---
NUM_THREADS = 10 # Number of threads to use for scanning. Adjust as needed.

# --- Global Queue for Results ---
# This queue will hold the results (IP, MAC, Hostname) found by each thread.
results_queue = queue.Queue()

# --- Scan Function ---
def scan_ip(ip, q):
    """
    Sends an ARP request to a single IP and resolves its hostname.
    Stores the result (IP, MAC, Hostname) in the shared queue.
    """
    try:
        # 1. Create ARP request 
        arp_request = scapy.ARP(pdst=str(ip))
        # 2. Create Ethernet broadcast frame 
        # ff:ff:ff:ff:ff:ff is the broadcast MAC address
        broadcast_ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        # 3. Combine them into a single packet 
        packet = broadcast_ether / arp_request

        # 4. Send packet and receive response 
        # timeout=1: Wait for 1 second for a response
        # verbose=False: Don't show scapy's internal output
        answered_list = scapy.srp(packet, timeout=1, verbose=False)[0]

        if answered_list:
            # An active device responded 
            # result[0][1] refers to the response packet
            # .psrc is the source IP of the responder
            # .hwsrc is the MAC address of the responder
            active_ip = answered_list[0][1].psrc
            mac_address = answered_list[0][1].hwsrc

            # 5. Attempt Hostname Resolution 
            hostname = "Unknown"
            try:
                # socket.gethostbyaddr() performs a reverse DNS lookup 
                # It returns a tuple: (hostname, aliaslist, ipaddrlist)
                hostname = socket.gethostbyaddr(active_ip)[0]
            except socket.herror:
                # Handle cases where hostname resolution fails 
                pass # hostname remains "Unknown"

            # 6. Store result in the queue 
            q.put({"ip": active_ip, "mac": mac_address, "hostname": hostname})

    except Exception as e:
        # Handle potential errors during scanning (e.g., network issues)
        # print(f"Error scanning {ip}: {e}") # Uncomment for debugging if needed
        pass

# --- Display Results Function ---
def print_results(q):
    """
    Retrieves results from the queue and prints them in a structured table.
    """
    if q.empty():
        print("\nNo active devices found in the specified range.")
        return

    print("\n--- Network Scan Results ---")
    print("{:<15} {:<18} {:<30}".format("IP Address", "MAC Address", "Hostname"))
    print("-" * 63) # Separator line

    # Retrieve all results from the queue
    all_results = []
    while not q.empty():
        all_results.append(q.get())

    # Sort results by IP address for better readability
    all_results.sort(key=lambda x: [int(part) for part in x['ip'].split('.')])

    for device in all_results:
        print("{:<15} {:<18} {:<30}".format(
            device['ip'],
            device['mac'],
            device['hostname']
        ))
    print("-" * 63)

# --- Main Function ---
def main():
    """
    Main function to get user input, generate IPs, start threads, and display results.
    """
    print("Python Network Scanner")
    print("----------------------")

    # 1. Get network input from user 
    while True:
        network_input = input("Enter network in CIDR format (e.g., 192.168.1.0/24): ")
        try:
            # 2. Generate IP addresses from the subnet 
            # ipaddress.ip_network() parses the CIDR string 
            network = ipaddress.ip_network(network_input, strict=False)
            break
        except ValueError:
            print("Invalid CIDR format. Please try again (e.g., 192.168.1.0/24)")

    # Get all valid host IPs from the network
    # Note: For very large networks, network.hosts() might consume a lot of memory.
    # For typical home networks (/24), it's fine.
    target_ips = list(network.hosts())
    print(f"Scanning {len(target_ips)} possible hosts in {network_input}...")

    # 3. Implement multi-threading 
    threads = []
    for ip in target_ips:
        # Create a thread for each IP to scan it concurrently 
        thread = threading.Thread(target=scan_ip, args=(ip, results_queue))
        threads.append(thread)
        thread.start() # Start the thread 

        # Optional: Limit active threads to prevent overwhelming the system
        # If the number of IPs is much larger than NUM_THREADS, this logic
        # would be more complex, involving a worker pool. For simplicity,
        # we're just creating NUM_THREADS at a time.
        while threading.active_count() > NUM_THREADS:
            # Wait for some threads to finish before spawning new ones
            # A more robust solution might use a ThreadPoolExecutor
            pass


    # Wait for all threads to complete their execution 
    for thread in threads:
        thread.join()

    # 4. Display the scan results 
    print_results(results_queue)

# --- Entry Point ---
if __name__ == "__main__":
    # Ensure the script is run with appropriate privileges
    if sys.platform.startswith('linux') and not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix') and not sys.getuid() == 0:
        print("This script requires root privileges on Linux. Please run with 'sudo python network_scanner.py'")
        sys.exit(1)
    elif sys.platform == 'win32':
        # On Windows, user needs to run command prompt/VS Code terminal as administrator
        print("Ensure you are running this script from a Command Prompt or VS Code Terminal opened as Administrator on Windows.")
        print("Press Enter to continue, or close this window if not running as admin.")
        input() # Wait for user confirmation

    main()