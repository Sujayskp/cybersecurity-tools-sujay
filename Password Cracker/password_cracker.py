import hashlib # For hashing passwords 
import itertools # For generating password combinations (brute-force) 
import string # For accessing sets of characters (e.g., lowercase letters, digits) 
import concurrent.futures # For multi-threading 
import argparse # For parsing command-line arguments 
from tqdm import tqdm # For displaying progress bars 

# Define a list of supported hash algorithms to make it easier to validate user input later
HASH_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
}
# Function to check if a generated password matches the target hash
def check_hash(password, target_hash, hash_function):
    """
    Hashes a given password and compares it to a target hash.

    Args:
        password (str): The password string to hash.
        target_hash (str): The hash to compare against.
        hash_function (callable): The hashlib function to use (e.g., hashlib.md5).

    Returns:
        str or None: The cracked password if a match is found, otherwise None.
    """
    # Uncomment the print statement below ONLY IF the script still gets stuck
    # after these changes, to help debug where it might be hanging.
    # print(f"DEBUG: Checking password: {password}")

    try:
        hashed_password = hash_function(password.encode('utf-8')).hexdigest()
        if hashed_password == target_hash:
            return password
    except Exception as e:
        print(f"Error hashing password '{password}': {e}")
    return None
# Generator function to create password combinations for brute-force attack
def generate_passwords(chars, min_length, max_length):
    """
    Generates password combinations using itertools.product.

    Args:
        chars (str): The set of characters to use for generating passwords (e.g., 'abc', '0123').
        min_length (int): The minimum length of passwords to generate.
        max_length (int): The maximum length of passwords to generate.

    Yields:
        str: A generated password.
    """
    for length in range(min_length, max_length + 1):
        for combo in itertools.product(chars, repeat=length):
            yield "".join(combo)

def crack_hash(target_hash, hash_type, wordlist_path=None, min_length=1, max_length=8, chars=string.ascii_letters + string.digits):
    # Mapping hash type strings to hashlib functions
    hash_functions = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }

    hash_function = hash_functions.get(hash_type)
    if not hash_function:
        print(f"Error: Unsupported hash type '{hash_type}'. Supported types: {', '.join(hash_functions.keys())}")
        return None

    cracked_password = None

    # Use ThreadPoolExecutor for multi-threading
    # The number of workers can be adjusted based on CPU cores.
    # We'll use a sensible default like 8 (or based on CPU cores if more advanced).
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        total_passwords_estimate = 0
        passwords_to_check = [] # Initialize here for scope

        # Determine attack type and prepare passwords
        if wordlist_path:
            # Dictionary Attack
            print(f"Attempting dictionary attack using wordlist: {wordlist_path}")
            try:
                with open(wordlist_path, 'r', encoding='latin-1') as f: # Use latin-1 for broader compatibility with wordlists
                    passwords_to_check = [line.strip() for line in f if line.strip()]
                    total_passwords_estimate = len(passwords_to_check)
            except FileNotFoundError:
                print(f"Error: Wordlist file '{wordlist_path}' not found.")
                return None
        else:
            # Brute-Force Attack
            print(f"Attempting brute-force attack with min_length={min_length}, max_length={max_length}, chars='{chars}'")
            # For brute-force, estimating total is hard, tqdm will show count as it processes
            passwords_to_check_generator = generate_passwords(chars, min_length, max_length)
            passwords_to_check = passwords_to_check_generator # Assign generator to the variable

        if not passwords_to_check:
            print("No passwords to check. Exiting.")
            return None

        # Initialize progress bar
        # For wordlist, we know the total. For brute-force, tqdm will update dynamically.
        pbar = tqdm(total=total_passwords_estimate, unit="pass", desc="Cracking", dynamic_ncols=True, leave=True)

        # Submit tasks to the thread pool and collect futures
        # Reset futures list just before submitting tasks
        futures = []
        for password_attempt in passwords_to_check:
            future = executor.submit(check_hash, password_attempt, target_hash, hash_function)
            futures.append(future)

        # Process results as they complete, updating the progress bar
        for future in concurrent.futures.as_completed(futures):
            pbar.update(1) # Update progress bar for each completed task
            result = future.result()
            if result:
                cracked_password = result
                pbar.close() # Close progress bar explicitly when found
                break # Exit loop once found

    if cracked_password:
        print(f"\nPassword cracked: {cracked_password}")
    else:
        pbar.close() # Close progress bar if loop finishes without finding
        print("\nPassword not found.")

    return cracked_password
# ... (previous functions: check_hash, generate_passwords, crack_hash) ...

# Main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sujay's Python-based Password Cracker")

    # Required argument: target hash
    parser.add_argument("hash", help="The hashed password to crack (e.g., MD5, SHA-256).")
    
    # Required argument: hash type
    parser.add_argument("-t", "--type", required=True, choices=HASH_ALGORITHMS.keys(),
                        help=f"The type of hash (e.g., md5, sha1, sha256). Supported: {', '.join(HASH_ALGORITHMS.keys())}.")

    # Optional argument: wordlist for dictionary attack
    parser.add_argument("-w", "--wordlist", help="Path to a wordlist file for dictionary attack.")

    # Optional arguments for brute-force attack
    parser.add_argument("-min", "--min_length", type=int, default=1,
                        help="Minimum length for brute-force passwords (default: 1).")
    parser.add_argument("-max", "--max_length", type=int, default=8,
                        help="Maximum length for brute-force passwords (default: 8).")
    parser.add_argument("-c", "--chars", default=string.ascii_letters + string.digits,
                        help=f"Character set for brute-force (default: '{string.ascii_letters + string.digits}').")

    args = parser.parse_args()

    # Determine cracking method based on arguments
    if args.wordlist:
        cracked = crack_hash(args.hash, args.type, wordlist_path=args.wordlist)
    else:
        # Check if min_length and max_length are valid
        if args.min_length <= 0:
            print("Error: Minimum length must be greater than 0.")
        elif args.min_length > args.max_length:
            print("Error: Minimum length cannot be greater than maximum length.")
        else:
            cracked = crack_hash(args.hash, args.type, 
                                 min_length=args.min_length, 
                                 max_length=args.max_length, 
                                 chars=args.chars)

    # Optional: You can add more output here if you want a final summary
    # if cracked:
    #     print(f"Cracking completed successfully. Found: {cracked}")
    # else:
    #     print("Cracking completed. Password not found.")