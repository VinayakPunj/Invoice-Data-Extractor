import re
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import io
import os
import sqlite3  # For SQL database operations
from langchain.schema import Document  # Import Document schema for langchain

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
config = {"temperature": 0, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192}
KEY = 'AIzaSyAvp9ZEf0kgQQ2uUSBZe6xMXkLKPrwcvug'
genai.configure(api_key=KEY)

# Streamlit UI
st.title("Invoice Uploader and Extractor")
st.write("Upload an invoice in PDF format to extract the company name, date, and total amount.")

# Connect to SQLite Database
conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

# Create 'invoices' table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    invoice_date TEXT,
                    total_amount REAL
                )''')


# Function to extract text from PDF images without saving to a file
def extract_text_from_images_directly(pdf_path, max_pages=10):
    pages = convert_from_path(pdf_path)
    pg_cntr = 1
    extracted_text = ""

    for page in pages:
        if pg_cntr <= max_pages:
            text = pytesseract.image_to_string(page)
            extracted_text += text + "\n"
            pg_cntr += 1
        else:
            break
    return extracted_text


def generate_text(instruction, prompt_parts):
    model = get_model(instruction)
    try:
        response = model.generate_content(prompt_parts)
        if response is None or not response.text:
            if response and hasattr(response, 'candidate') and hasattr(response.candidate, 'safety_ratings'):
                safety_ratings = response.candidate.safety_ratings
                return f'Generation blocked due to safety ratings: {safety_ratings}'
            else:
                return 'No valid response generated.'
        return response.text
    except Exception as ex:
        return str(ex)


def get_model(instruction):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=config,
        system_instruction=instruction,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    )
    return model


# Upload PDF invoice via Streamlit
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract the text from the uploaded PDF
    pdf_bytes = uploaded_file.read()
    with open("uploaded_invoice.pdf", "wb") as f:
        f.write(pdf_bytes)

    # Extract text from the PDF file
    invoice_text = extract_text_from_images_directly("uploaded_invoice.pdf")

    # Define the query for LLM to extract the relevant information
    prompt = """Extract the company name, invoice date, and total amount from the invoice. 
    Only return the required information without adding extra words or sentences.
    The output should strictly follow this format:
    Company name: <company_name> Invoice date: <invoice_date> Total amount: <total_amount>

    Ensure:
    - The company name is enclosed within `Company name:`
    - The invoice date is enclosed within `Invoice date:`
    - The total amount is enclosed within `Total amount:`
    - No extra text or comments are included.
    - Use the exact field names and order as provided above.
    """

    instruction = """
    You are an invoice examiner. Your job is to interpret the text of an invoice and extract the 
    information from the document.
    """

    # Prompt parts: text extracted from invoice and the instruction
    prompt_parts = [invoice_text, prompt]

    # Generate structured text using the LLM
    llm_output = generate_text(instruction, prompt_parts)

    # Display the extracted LLM output
    st.write("Invoice Information: ")
    st.text(llm_output)

    # Parse the LLM output to extract relevant information
    company_name_match = re.search(r"Company name:\s*([^\n]+?)\s*Invoice date:", llm_output)
    date_match = re.search(r"Invoice date:\s*([^\n]+?)\s*Total amount:", llm_output)
    total_amount_match = re.search(r"Total amount:\s*([\d,]+\.\d{2})", llm_output)

    company_name = company_name_match.group(1).strip() if company_name_match else "Unknown"
    invoice_date = date_match.group(1).strip() if date_match else "Unknown"
    total_amount = total_amount_match.group(1).replace(",", "") if total_amount_match else "Unknown"

    if total_amount != "Unknown":
        total_amount = float(total_amount)

    # Display extracted values in Streamlit
    st.write(f"Company Name: {company_name}")
    st.write(f"Invoice Date: {invoice_date}")
    st.write(f"Total Amount: {total_amount}")

    # Save extracted details to the database
    cursor.execute('INSERT INTO invoices (company_name, invoice_date, total_amount) VALUES (?, ?, ?)',
                   (company_name, invoice_date, total_amount))

    conn.commit()

    # Display success message
    st.success("Invoice details have been saved to the database.")
