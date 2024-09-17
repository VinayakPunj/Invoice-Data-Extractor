import re
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import io
import os
import sqlite3
import pandas as pd  # For handling CSV export
from datetime import datetime  # For date handling

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
config = {"temperature": 0, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192}
KEY = 'AIzaSyAvp9ZEf0kgQQ2uUSBZe6xMXkLKPrwcvug'
genai.configure(api_key=KEY)

# Streamlit UI
st.title("Invoice Uploader, Extractor, and Search")

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

# Page selection
page = st.sidebar.selectbox("Choose an option", ["Upload & Extract Invoices", "Search & Download Data"])

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

# Invoice Upload and Extraction Page
if page == "Upload & Extract Invoices":
    uploaded_files = st.file_uploader("Choose multiple PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files is not None:
        for idx, uploaded_file in enumerate(uploaded_files):
            # Extract the text from each uploaded PDF
            pdf_bytes = uploaded_file.read()
            with open(uploaded_file.name, "wb") as f:
                f.write(pdf_bytes)

            # Extract text from the PDF file
            invoice_text = extract_text_from_images_directly(uploaded_file.name)

            # Define the query for LLM to extract the relevant information
            prompt = """Extract the company name, invoice date, and total amount from the invoice. 
            Only return the required information without adding extra words or sentences. The date shouls be in the format DD-MM-YYY.
            The output should strictly follow this format:
            Company name: <company_name> Invoice date: <invoice_date> Total amount: <total_amount>

            Ensure:
            - The company name is enclosed within `Company name:`
            - The invoice date is enclosed within `Invoice date:`
            - The total amount is enclosed within `Total amount:`
            - No extra text or comments are included.
            - Use the exact field names and order as provided above.
            - The date is in dd-mm-yyyy format.
            """

            instruction = """
            You are an invoice examiner. Your job is to interpret the text of an invoice and extract the 
            information from the document.
            """

            # Prompt parts: text extracted from invoice and the instruction
            prompt_parts = [invoice_text, prompt]

            # Generate structured text using the LLM
            llm_output = generate_text(instruction, prompt_parts)

            # Parse the LLM output to extract relevant information
            company_name_match = re.search(r"Company name:\s*([^\n]+?)\s*Invoice date:", llm_output)
            date_match = re.search(r"Invoice date:\s*([^\n]+?)\s*Total amount:", llm_output)
            total_amount_match = re.search(r"Total amount:\s*([\d,]+\.\d{2})", llm_output)

            company_name = company_name_match.group(1).strip() if company_name_match else "Unknown"
            invoice_date = date_match.group(1).strip() if date_match else "Unknown"
            total_amount = total_amount_match.group(1).replace(",", "") if total_amount_match else "Unknown"

            if total_amount != "Unknown":
                total_amount = float(total_amount)

            # Show the extracted values in editable input fields with unique keys
            st.write(f"Review and edit the information for {uploaded_file.name}:")
            company_name_input = st.text_input(f"Company Name ({uploaded_file.name})", value=company_name, key=f"company_name_{idx}")
            invoice_date_input = st.text_input(f"Invoice Date ({uploaded_file.name})", value=invoice_date, key=f"invoice_date_{idx}")
            total_amount_input = st.number_input(f"Total Amount ({uploaded_file.name})", value=total_amount, key=f"total_amount_{idx}")

            # Confirmation button
            if st.button(f"Confirm for {uploaded_file.name}", key=f"confirm_{idx}"):
                # Save the edited details to the database
                cursor.execute('INSERT INTO invoices (company_name, invoice_date, total_amount) VALUES (?, ?, ?)',
                               (company_name_input, invoice_date_input, total_amount_input))

                conn.commit()

                # Success message for each file
                st.success(f"Invoice details for {uploaded_file.name} have been saved to the database.")

            # Add space between invoices
            st.divider()  # Add a horizontal line
            st.write("")  # Add extra space

# Search and Download Page
elif page == "Search & Download Data":
    st.header("Search Invoices")

    # Search form for from date, to date, and company name
    with st.form(key="search_form"):
        search_from_date = st.text_input("From Date (dd-mm-yyyy)")
        search_to_date = st.text_input("To Date (dd-mm-yyyy)")
        search_company_name = st.text_input("Search by Company Name")
        submit_search = st.form_submit_button(label="Search")

    # If search is submitted, query the database
    if submit_search:
        query = "SELECT * FROM invoices WHERE 1=1"
        params = []

        # Handle date format conversion for the search query
        def convert_to_iso(date_str):
            return datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')

        # Add date filtering based on the "From Date" and "To Date"
        if search_from_date:
            from_date_iso = convert_to_iso(search_from_date)
            query += " AND invoice_date >= ?"
            params.append(from_date_iso)
        if search_to_date:
            to_date_iso = convert_to_iso(search_to_date)
            query += " AND invoice_date <= ?"
            params.append(to_date_iso)

        # Add company name filtering
        if search_company_name:
            query += " AND company_name LIKE ?"
            params.append(f"%{search_company_name}%")

        # Execute the query
        cursor.execute(query, params)
        results = cursor.fetchall()

        # Display the results
        if results:
            st.write("Search Results:")
            df = pd.DataFrame(results, columns=["ID", "Company Name", "Invoice Date", "Total Amount"])
            st.dataframe(df)

            # Provide an option to download the search results as CSV
            csv = df.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name="invoice_search_results.csv", mime="text/csv")
        else:
            st.write("No results found for the given criteria.")
