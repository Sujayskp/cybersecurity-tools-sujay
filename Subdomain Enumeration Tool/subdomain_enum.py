# subdomain_enum.py

import requests
import threading

# Set the target domain
domain = "youtube.com"

# Shared list to store working subdomains
discovered_subdomains = []

# Lock to make thread-safe changes
lock = threading.Lock()

# Read subdomains from file
with open("subdomains.txt") as file:
    subdomains = file.read().splitlines()

# Define a function to check each subdomain
def check_subdomain(subdomain):
    url = f"http://{subdomain}.{domain}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"[+] Found: {url}")
            with lock:
                discovered_subdomains.append(url)
    except requests.ConnectionError:
        pass  # Ignore subdomains that fail

# Create and start threads
threads = []
for sub in subdomains:
    t = threading.Thread(target=check_subdomain, args=(sub,))
    t.start()
    threads.append(t)

# Wait for all threads to complete
for t in threads:
    t.join()

# Save discovered subdomains to a file
with open("discovered_subdomains.txt", "w") as file:
    for url in discovered_subdomains:
        print(url, file=file)

print("✅ Done! Discovered subdomains saved to discovered_subdomains.txt")
