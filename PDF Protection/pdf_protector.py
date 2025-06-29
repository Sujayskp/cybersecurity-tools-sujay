import sys
import PyPDF2

def add_password(input_pdf, output_pdf, password):
    try:
        # Open the input PDF file in read-binary mode
        with open(input_pdf, "rb") as file:
            reader = PyPDF2.PdfReader(file)  # Read the PDF
            writer = PyPDF2.PdfWriter()      # Create a new PDF writer object

            # Loop through all the pages and add to the new PDF
            for page in reader.pages:
                writer.add_page(page)

            # Apply password protection
            writer.encrypt(password)

            # Save the protected PDF to output
            with open(output_pdf, "wb") as output_file:
                writer.write(output_file)

        print(f"✅ Protected PDF saved as: {output_pdf}")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_pdf}' was not found.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

# Main code runs only when script is directly executed
if __name__ == "__main__":
    # Check if exactly 4 arguments are passed (including script name)
    if len(sys.argv) != 4:
        print("📌 Usage: python pdf_protector.py input.pdf output.pdf password")
        sys.exit()

    # Get command-line arguments
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    password = sys.argv[3]

    # Call the function with arguments
    add_password(input_pdf, output_pdf, password)
