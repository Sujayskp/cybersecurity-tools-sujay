import argparse
import itertools
import string
import pikepdf
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Load passwords from a wordlist
def load_passwords(wordlist_file):
    with open(wordlist_file, 'r') as file:
        for line in file:
            yield line.strip()

# Generate passwords using brute-force
def generate_passwords(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for pwd in itertools.product(charset, repeat=length):
            yield ''.join(pwd)

# Try opening the PDF with a given password
def try_password(pdf_file, password):
    try:
        with pikepdf.open(pdf_file, password=password) as pdf:
            return password
    except pikepdf._core.PasswordError:
        return None

# Main decryption function
def decrypt_pdf(pdf_file, passwords, threads=4):
    found = None
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(try_password, pdf_file, pwd): pwd for pwd in passwords}
        for future in tqdm(futures, desc="Cracking PDF"):
            result = future.result()
            if result:
                found = result
                break
    return found

# Parse command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Cracker Tool")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--wordlist", help="Path to a wordlist file")
    parser.add_argument("--brute", action="store_true", help="Use brute-force attack")
    parser.add_argument("--min", type=int, default=1, help="Minimum password length")
    parser.add_argument("--max", type=int, default=3, help="Maximum password length")
    parser.add_argument("--charset", default=string.digits, help="Character set for brute-force")

    args = parser.parse_args()

    if args.wordlist:
        passwords = load_passwords(args.wordlist)
    elif args.brute:
        passwords = generate_passwords(args.charset, args.min, args.max)
    else:
        print("Provide --wordlist or --brute option")
        exit(1)

    result = decrypt_pdf(args.pdf, passwords)
    if result:
        print(f"\nPassword found: {result}")
    else:
        print("\nPassword not found.")
