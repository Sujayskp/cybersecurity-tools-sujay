# PDF Cracker Tool

A Python-based tool designed to decrypt password-protected PDF files. This project demonstrates practical applications of file handling, password security, and automation in Python. It supports both **dictionary-based** and **brute-force** attacks and leverages **multi-threading** for improved performance.

---

## 🔧 Features

- **🔐 Dictionary Attack**: Tries passwords from a provided wordlist file.
- **💣 Brute-Force Attack**: Generates and tests combinations of characters based on user-defined parameters.
- **🚀 Multi-threading**: Utilizes `ThreadPoolExecutor` for faster execution.
- **🖥 Command-Line Interface**: Uses `argparse` for passing inputs and settings.
- **📊 Progress Tracking**: Displays a live progress bar using `tqdm`.
- **⚠️ Error Handling**: Manages missing arguments, unreadable files, or failed attempts.

---

## 📦 Installation

Install the required Python libraries before running the tool:

```bash
pip install pikepdf tqdm
▶️ How to Run
Make sure your script file (pdf_cracker.py), the password-protected PDF (e.g., protected.pdf), and the wordlist file (if using) are in the same directory or provide correct paths.

1️⃣ Dictionary Attack
Attempts passwords from a wordlist file:

bash
python pdf_cracker.py protected.pdf --wordlist wordlist.txt
protected.pdf: Path to the password-protected PDF.

wordlist.txt: Path to the wordlist containing possible passwords.

2️⃣ Brute-Force Attack
Generates and tests all combinations within the specified character set and length:

bash
python pdf_cracker.py protected.pdf --brute-force --min-length 1 --max-length 4 --chars abcdefg123
--brute-force: Enables brute-force mode.

--min-length: Minimum length of password to generate.

--max-length: Maximum length of password to generate.

--chars: Characters to use when generating passwords.

⚙️ Optional Arguments
--workers <NUMBER>: Number of threads to run in parallel (default is number of CPU cores).

✅ Expected Outcome
If the password is found, it will be displayed in the terminal.

If the password is not found, the script will notify you.

If required arguments are missing or the PDF is unreadable, the tool will handle and report the error.

⚠️ Disclaimer
This tool is developed for educational and ethical purposes only.
Do not use it to target domains you do not own or do not have permission to test.

The developer is not responsible for any misuse or illegal activity done using this tool.

🛡️ Learn. Practice. Respect cyber laws.
