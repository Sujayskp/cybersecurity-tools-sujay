# Subdomain Enumeration Tool

This is a simple Python-based tool that identifies valid subdomains of a given domain by checking a list of possible subdomain names. It uses multithreading and the `requests` library to test URLs quickly and efficiently.

## 🔍 Features

- Reads subdomain names from a file (`subdomains.txt`)
- Constructs full URLs like `http://sub.example.com`
- Sends HTTP requests to test each URL
- Uses multithreading for fast execution
- Saves working subdomains to `discovered_subdomains.txt`

## 🚀 How to Use

1. Make sure Python 3 and the `requests` library are installed:
   ```bash
   pip install requests
2. Add your target subdomains to subdomains.txt (one per line).

3. Edit the script to set your target domain:
   python
   domain = "example.com"
4. Run the script:
    bash
    python subdomain_enum.py
5. Check the output file:
   discovered_subdomains.txt
📁 Example subdomains.txt
nginx

www
mail
ftp
blog
api
⚠️ Disclaimer
This tool is developed for educational and ethical purposes only.
Do not use it to target domains you do not own or do not have permission to test.

The developer is not responsible for any misuse or illegal activity done using this tool.

🛡️ Learn. Practice. Respect cyber laws.
