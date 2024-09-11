# Import necessary modules
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import io
import os
import sqlite3  # For SQL database operations
from langchain.schema import Document  # Import Document schema for langchain

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Connect to SQLite Database
conn = sqlite3.connect('invoices.db')
cursor = conn.cursor()

# Create 'invoices' table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    invoice_date TEXT,
                    total_amount TEXT
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

# Extract text from PDF invoices without saving to file
pdf_path = 'sample invoices/-4180389598760657265.MB TIMBER 15.pdf'
invoice_text = extract_text_from_images_directly(pdf_path)

# Now, instead of saving to a txt file, we directly process the text with the LLM
# Create Document object from extracted text
documents = [Document(page_content=invoice_text)]

# Initialize Hugging Face Embeddings and Chroma vector store
embeddings = HuggingFaceEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_documents = text_splitter.split_documents(documents)  # Now using the correct Document object
db = Chroma.from_documents(split_documents, embeddings)

# Initialize LLM
llm = Ollama(model="llama2")

# Prompt for extracting relevant fields (Company Name, Date, and Total Amount)
prompt_template = """
Extract the company name, invoice date, and total amount from the following invoice text. 
Ensure that the total amount is returned as a numeric value only, do not give it in word form.
<context>
{context}
</context>
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# Document chain for processing
document_chain = create_stuff_documents_chain(llm, prompt)
retriever = db.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Define the query for LLM to extract the relevant information
query = "Extract the company name, date, and total amount from the invoice."

# Invoke the retrieval chain
response = retrieval_chain.invoke({"input": query})

# The extracted result from the LLM might contain structured information
# You can parse the result to extract the company name, date, and total amount
llm_output = response['answer']
print("LLM Output:", llm_output)  # Inspect the raw output

# Example parsing the LLM output assuming it gives well-structured info like:
# "Company Name: XYZ Ltd\nDate: 2023-09-01\nTotal Amount: $1000"
import re


# Regex to extract the company name, invoice date, and total amount (numeric)
company_name_match = re.search(r"Company name:\s*(.*)", llm_output)
date_match = re.search(r"Invoice date:\s*(.*)", llm_output)
# Regex to capture total amount in INR format
total_amount_match = re.search(r"Total amount:\s*INR\s*([\d,]+\.\d{2})", llm_output)

# Extract the values if found
company_name = company_name_match.group(1).strip() if company_name_match else "Unknown"
invoice_date = date_match.group(1).strip() if date_match else "Unknown"
total_amount = total_amount_match.group(1).replace(",", "") if total_amount_match else "Unknown"

# Convert total amount to a float (numeric) type if it exists
if total_amount != "Unknown":
    total_amount = float(total_amount)

# Print extracted fields
print(f"Company Name: {company_name}")
print(f"Invoice Date: {invoice_date}")
print(f"Total Amount: {total_amount}")

# Save extracted details to SQL database
cursor.execute('INSERT INTO invoices (company_name, invoice_date, total_amount) VALUES (?, ?, ?)',
               (company_name, invoice_date, total_amount))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Invoice details saved to database.")
