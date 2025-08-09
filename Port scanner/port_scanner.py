import socket
import concurrent.futures
import sys
import time # We'll use this later for progress tracking

# ANSI Color Codes for formatted output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
# ... (Previous code: imports and color codes) ...

def scan_port(target_ip, port):
    """
    Scans a single port on the target IP and returns its status, service, and banner.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a timeout for the connection attempt
        result = sock.connect_ex((target_ip, port))

        service_name = "Unknown"
        banner_info = ""

        if result == 0:  # Port is open 
            try:
                service_name = socket.getservbyport(port, "tcp") # attempts to get the common service name associated with that port 
            except OSError:
                service_name = "Unknown Service"
            
            banner_info = get_banner(sock) # Call get_banner to retrieve the banner 
            return "Open", service_name, banner_info
        else:
            return "Closed", service_name, banner_info # returns 0 for success (open port) or an error code (closed) 
    except socket.timeout:
        return "Filtered (Timeout)", "N/A", ""
    except Exception as e:
        return f"Error: {e}", "N/A", ""
    finally:
        sock.close() # Ensure the socket is closed
        # ... (Previous code: imports, color codes, scan_port function) ...

def get_banner(sock):
    """
    Attempts to retrieve the banner from an open socket.
    """
    try:
        # Receive up to 1024 bytes of data from the socket
        banner = sock.recv(1024).decode().strip() #
        return banner
    except socket.timeout:
        return "No banner (timeout)"
    except Exception as e:
        return f"No banner (error: {e})"
    # ... (Previous code: imports, color codes, scan_port, get_banner functions) ...

def format_port_results(results):
    """
    Formats and displays the scan results in a structured table.
    """
    if not results:
        print(f"\n{YELLOW}No open ports found.{RESET}")
        return

    print(f"\n{GREEN}--- Port Scan Results ---{RESET}")
    # Print table header
    print(f"{'Port':<8} {'Status':<15} {'Service':<20} {'Banner'}") # 
    print("-" * 70) # Adjust line length as needed

    for port, status, service, banner in results:
        # Determine color based on status (e.g., green for Open)
        status_color = GREEN if status == "Open" else YELLOW if status == "Filtered (Timeout)" else RED
        
        port_str = str(port) # Ensure port is a string for formatting
        
        print(f"{port_str:<8} {status_color}{status:<15}{RESET} {service:<20} {banner}") # 
    
    print(f"\n{GREEN}--- Scan Complete ---{RESET}")
    # ... (Previous code: imports, color codes, scan_port, get_banner, format_port_results functions) ...

def port_scan(target, start_port, end_port):
    """
    Orchestrates the multithreaded port scanning process.
    """
    print(f"\n{YELLOW}Starting scan on target: {target} (Ports: {start_port}-{end_port}){RESET}")
    
    try:
        # Resolve hostname to IP address
        target_ip = socket.gethostbyname(target) # 
        print(f"{YELLOW}Resolved IP: {target_ip}{RESET}")
    except socket.gaierror:
        print(f"{RED}Error: Could not resolve hostname '{target}'. Please check the target.{RESET}")
        return

    open_ports_info = []
    total_ports = end_port - start_port + 1
    scanned_count = 0

    # Use ThreadPoolExecutor for concurrent scanning 
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor: # 
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(start_port, end_port + 1)} # 

        for future in concurrent.futures.as_completed(futures): # 
            port = futures[future]
            scanned_count += 1
            
            # Update progress dynamically on the same line 
            sys.stdout.write(f"\r{YELLOW}Progress: {scanned_count}/{total_ports} ports scanned ({port}) {RESET}") # 
            sys.stdout.flush() # 

            try:
                status, service, banner = future.result()
                if status == "Open":
                    open_ports_info.append((port, status, service, banner))
            except Exception as exc:
                # Handle exceptions that might occur during future execution (e.g., if scan_port itself failed unexpectedly)
                sys.stdout.write(f"\r{RED}Error scanning port {port}: {exc}{RESET}\n")
                sys.stdout.flush()

    # Clear the progress line and print results
    sys.stdout.write("\n") # Move to next line after progress
    sys.stdout.flush()

    format_port_results(open_ports_info)
    # ... (Previous code: all functions including port_scan) ...

if __name__ == "__main__":
    print(f"{GREEN}--- Python Port Scanner by Sujay ---{RESET}") #
    
    target_host = input("Enter target IP address or hostname (e.g., 127.0.0.1 or scanme.nmap.org): ").strip() # 
    
    while True:
        try:
            start_port_str = input("Enter start port (e.g., 1): ").strip()
            end_port_str = input("Enter end port (e.g., 100): ").strip()
            
            start_port = int(start_port_str)
            end_port = int(end_port_str)

            if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535): # 
                print(f"{RED}Error: Port numbers must be between 1 and 65535.{RESET}")
                continue
            
            if start_port > end_port:
                print(f"{RED}Error: Start port cannot be greater than end port.{RESET}")
                continue
            
            break # Exit loop if inputs are valid
        except ValueError:
            print(f"{RED}Invalid port number. Please enter a valid integer.{RESET}")

    port_scan(target_host, start_port, end_port)