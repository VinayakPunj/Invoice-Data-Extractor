"""
InvoiceIQ - Professional Invoice Data Extractor
Streamlit application for extracting and managing invoice data using AI and OCR.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

from config import Config
from src.database import DatabaseManager
from src.ocr import OCRProcessor
from src.llm import InvoiceExtractor
from src.utils import DateParser, AmountParser, Validator
from src.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)


def validate_configuration():
    """Validate application configuration and show warnings if needed."""
    errors = Config.validate()
    
    if errors:
        for error in errors:
            st.error(f"⚠️ Configuration Error: {error}")
        st.stop()
    
    # Validate OCR
    if not OCRProcessor.validate_tesseract_installation():
        st.error("⚠️ Tesseract OCR is not properly installed or configured.")
        st.info("Please install Tesseract and update the TESSERACT_CMD in your .env file.")
        st.stop()


def initialize_app():
    """Initialize application components."""
    if 'initialized' not in st.session_state:
        logger.info("Initializing application")
        
        # Initialize default state
        if 'selected_provider' not in st.session_state:
            st.session_state.selected_provider = Config.DEFAULT_PROVIDER
        
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = Config.LLM_MODEL
            
        if 'google_api_key' not in st.session_state:
            st.session_state.google_api_key = Config.GOOGLE_API_KEY
            
        if 'openai_api_key' not in st.session_state:
            st.session_state.openai_api_key = Config.OPENAI_API_KEY

        # Initialize components
        st.session_state.db_manager = DatabaseManager()
        st.session_state.ocr_processor = OCRProcessor()
        
        # Create initial extractor
        provider = st.session_state.selected_provider
        model = st.session_state.selected_model
        api_key = st.session_state.google_api_key if provider == 'google' else st.session_state.openai_api_key
        
        st.session_state.invoice_extractor = InvoiceExtractor(
            provider=provider,
            model_name=model,
            api_key=api_key
        )
        st.session_state.initialized = True
        
        logger.info(f"Application initialized with {provider} ({model})")


def render_header():
    """Render application header with logo and title."""
    col1, col2 = st.columns([1, 8])
    
    with col1:
        logo_path = Path("fevicon.png")
        if logo_path.exists():
            st.image(str(logo_path), width=80)
    
    with col2:
        st.title(f"📄 {Config.APP_TITLE}")
        st.caption("AI-Powered Invoice Data Extraction & Management")


def render_statistics():
    """Render statistics dashboard."""
    stats = st.session_state.db_manager.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Invoices", stats['total_invoices'])
    
    with col2:
        st.metric("Total Amount", f"${stats['total_amount']:,.2f}")
    
    with col3:
        st.metric("Unique Companies", stats['unique_companies'])


def process_invoice_file(uploaded_file, idx):
    """
    Process a single uploaded invoice file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        idx: Index for unique widget keys
    """
    st.subheader(f"📄 {uploaded_file.name}")
    
    try:
        # Create progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Extract text using OCR
        status_text.text("🔍 Extracting text from PDF...")
        progress_bar.progress(25)
        
        pdf_bytes = uploaded_file.read()
        
        # Save temporarily for processing
        temp_path = Path(uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        invoice_text = st.session_state.ocr_processor.extract_text_from_pdf(str(temp_path))
        
        # Cleanup temp file
        temp_path.unlink(missing_ok=True)
        
        # Step 2: Extract data using LLM
        status_text.text("🤖 Analyzing invoice with AI...")
        progress_bar.progress(50)
        
        extracted_data = st.session_state.invoice_extractor.extract_invoice_data(invoice_text)
        
        progress_bar.progress(75)
        status_text.text("✅ Extraction complete!")
        progress_bar.progress(100)
        
        # Step 3: Display and allow editing
        st.success("✅ Invoice data extracted successfully!")
        
        with st.form(key=f"invoice_form_{idx}"):
            st.write("**Review and edit the extracted information:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input(
                    "Company Name",
                    value=extracted_data['company_name'],
                    key=f"company_{idx}"
                )
                
                invoice_date_str = st.text_input(
                    "Invoice Date (DD-MM-YYYY or any format)",
                    value=extracted_data['invoice_date'],
                    key=f"date_{idx}",
                    help="Supports various date formats: DD-MM-YYYY, DD/MM/YYYY, DD-Mon-YY, etc."
                )
            
            with col2:
                total_amount_str = st.text_input(
                    "Total Amount",
                    value=extracted_data['total_amount'],
                    key=f"amount_{idx}",
                    help="Enter numeric amount (currency symbols will be removed)"
                )
            
            submitted = st.form_submit_button("💾 Save to Database", type="primary")
            
            if submitted:
                # Validate and parse data
                parsed_date = DateParser.parse_date(invoice_date_str)
                parsed_amount = AmountParser.parse_amount(total_amount_str)
                
                errors = []
                if not Validator.validate_company_name(company_name):
                    errors.append("Invalid company name")
                if not parsed_date:
                    errors.append(f"Invalid date format: {invoice_date_str}")
                if parsed_amount is None:
                    errors.append(f"Invalid amount: {total_amount_str}")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Save to database
                    try:
                        invoice_id = st.session_state.db_manager.insert_invoice(
                            company_name=company_name,
                            invoice_date=parsed_date,
                            total_amount=parsed_amount
                        )
                        st.success(f"✅ Invoice saved successfully! (ID: {invoice_id})")
                        logger.info(f"Invoice {invoice_id} saved for {company_name}")
                    except Exception as e:
                        st.error(f"❌ Error saving invoice: {e}")
                        logger.error(f"Failed to save invoice: {e}")
        
        # Cleanup
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        logger.error(f"Error processing file {uploaded_file.name}: {e}")


def render_upload_page():
    """Render the invoice upload and extraction page."""
    st.header("📤 Upload & Extract Invoices")
    
    st.info("💡 Upload one or more invoice PDFs. The AI will automatically extract company name, date, and amount.")
    
    uploaded_files = st.file_uploader(
        "Choose invoice PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF invoice files to process"
    )
    
    if uploaded_files:
        st.write(f"**Processing {len(uploaded_files)} file(s)**")
        
        for idx, uploaded_file in enumerate(uploaded_files):
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                process_invoice_file(uploaded_file, idx)
            
            if idx < len(uploaded_files) - 1:
                st.divider()


def render_search_page():
    """Render the search and download page."""
    st.header("🔍 Search & Download Data")
    
    # Statistics
    render_statistics()
    st.divider()
    
    # Search form
    with st.form(key="search_form"):
        st.subheader("Search Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            from_date = st.date_input(
                "From Date",
                value=None,
                help="Optional: Filter invoices from this date onwards"
            )
        
        with col2:
            to_date = st.date_input(
                "To Date",
                value=None,
                help="Optional: Filter invoices up to this date"
            )
        
        with col3:
            company_name = st.text_input(
                "Company Name",
                placeholder="Enter company name...",
                help="Optional: Search by company name (partial match)"
            )
        
        col_btn1, col_btn2 = st.columns([1, 5])
        
        with col_btn1:
            search_button = st.form_submit_button("🔍 Search", type="primary")
        
        with col_btn2:
            clear_button = st.form_submit_button("🔄 Clear & Show All")
    
    # Process search
    if search_button or clear_button:
        # Prepare search parameters
        from_date_str = from_date.strftime('%Y-%m-%d') if from_date and not clear_button else None
        to_date_str = to_date.strftime('%Y-%m-%d') if to_date and not clear_button else None
        company_filter = company_name.strip() if company_name and not clear_button else None
        
        # Validate date range
        if from_date_str and to_date_str:
            if not DateParser.validate_date_range(from_date_str, to_date_str):
                st.error("❌ Invalid date range: 'From Date' must be before or equal to 'To Date'")
                return
        
        # Search database
        try:
            results = st.session_state.db_manager.search_invoices(
                from_date=from_date_str,
                to_date=to_date_str,
                company_name=company_filter
            )
            
            if results:
                st.success(f"✅ Found {len(results)} invoice(s)")
                
                # Create DataFrame
                df = pd.DataFrame(
                    results,
                    columns=["ID", "Company Name", "Invoice Date", "Total Amount"]
                )
                
                # Format amount column
                df['Total Amount'] = df['Total Amount'].apply(lambda x: f"${x:,.2f}")
                
                # Display table
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download options
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download as CSV",
                        data=csv,
                        file_name=f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Excel download (if openpyxl available)
                    try:
                        from io import BytesIO
                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Invoices')
                        
                        st.download_button(
                            label="📊 Download as Excel",
                            data=buffer.getvalue(),
                            file_name=f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except ImportError:
                        st.caption("Excel export requires openpyxl package")
            
            else:
                st.warning("📭 No invoices found matching your criteria")
                
        except Exception as e:
            st.error(f"❌ Search error: {e}")
            logger.error(f"Search failed: {e}")


def render_sidebar():
    """Render sidebar with navigation and model configuration."""
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Choose an option:",
        ["📤 Upload & Extract Invoices", "🔍 Search & Download Data"],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    st.sidebar.title("🤖 Model Configuration")
    
    # Provider Selection
    providers = {
        "google": "Google Gemini",
        "ollama": "Ollama (Local)",
        "openai": "OpenAI (GPT)"
    }
    
    selected_provider_label = st.sidebar.selectbox(
        "Select Provider",
        options=list(providers.values()),
        index=list(providers.keys()).index(st.session_state.selected_provider)
    )
    
    # Get provider key from label
    new_provider = [k for k, v in providers.items() if v == selected_provider_label][0]
    
    # Update provider in session state
    if new_provider != st.session_state.selected_provider:
        st.session_state.selected_provider = new_provider
        # Reset model to default for provider
        if new_provider in Config.AVAILABLE_MODELS and Config.AVAILABLE_MODELS[new_provider]:
            st.session_state.selected_model = Config.AVAILABLE_MODELS[new_provider][0]
        else:
            st.session_state.selected_model = ""
        st.rerun()

    # API Key Input
    api_key_updated = False
    if st.session_state.selected_provider == 'google':
        google_key = st.sidebar.text_input(
            "Google API Key",
            value=st.session_state.google_api_key,
            type="password",
            help="Enter your Google API Key. If empty, uses value from .env"
        )
        if google_key != st.session_state.google_api_key:
            st.session_state.google_api_key = google_key
            api_key_updated = True
            
    elif st.session_state.selected_provider == 'openai':
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_api_key,
            type="password",
            help="Enter your OpenAI API Key. If empty, uses value from .env"
        )
        if openai_key != st.session_state.openai_api_key:
            st.session_state.openai_api_key = openai_key
            api_key_updated = True
    
    # Model Selection
    available_models = []
    
    # Create a temporary extractor for listing models
    temp_extractor = InvoiceExtractor(
        provider=st.session_state.selected_provider,
        api_key=st.session_state.google_api_key if st.session_state.selected_provider == 'google' else st.session_state.openai_api_key
    )
    
    with st.sidebar:
        with st.spinner("Fetching available models..."):
            available_models = temp_extractor.list_available_models()

    if st.session_state.selected_provider == 'ollama':
        if not available_models:
            st.sidebar.error("❌ Could not connect to Ollama or no models found.")
            st.sidebar.info("Make sure Ollama is running.")
        else:
            st.sidebar.success(f"✓ Connected to Ollama ({len(available_models)} models)")
    elif not available_models:
        st.sidebar.warning(f"No models found or API key is invalid/missing.")

    if available_models:
        # Ensure current model is in available models
        current_model = st.session_state.selected_model
        try:
            model_index = available_models.index(current_model) if current_model in available_models else 0
        except ValueError:
            model_index = 0
            
        new_model = st.sidebar.selectbox(
            "Select Model",
            options=available_models,
            index=model_index
        )
        
        if new_model != st.session_state.selected_model or api_key_updated:
            st.session_state.selected_model = new_model
            # Re-initialize extractor
            api_key = st.session_state.google_api_key if st.session_state.selected_provider == 'google' else st.session_state.openai_api_key
            st.session_state.invoice_extractor = InvoiceExtractor(
                provider=st.session_state.selected_provider,
                model_name=new_model,
                api_key=api_key
            )
            st.toast(f"Model updated: {new_model}")
    else:
        if st.session_state.selected_provider != 'ollama':
            st.sidebar.warning(f"No models available for {selected_provider_label}")

    st.sidebar.divider()
    st.sidebar.caption(f"InvoiceIQ v1.1.0")
    st.sidebar.caption(f"Current: {st.session_state.selected_provider} ({st.session_state.selected_model})")
    
    return page


def main():
    """Main application entry point."""
    # Initialize session state for models if not exists
    if 'selected_provider' not in st.session_state:
        st.session_state.selected_provider = Config.DEFAULT_PROVIDER
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = Config.LLM_MODEL
    
    # Validate configuration
    validate_configuration()
    
    # Initialize app
    initialize_app()
    
    # Render header
    render_header()
    
    # Sidebar navigation and config
    page = render_sidebar()
    
    # Render selected page
    if page == "📤 Upload & Extract Invoices":
        render_upload_page()
    else:
        render_search_page()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        st.error(f"❌ Application Error: {e}")