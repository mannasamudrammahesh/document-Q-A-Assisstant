import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Set your Gemini API Key 
GOOGLE_API_KEY = "AIzaSyAe5AkeTyf1rHojxSQ6roTgQYUTTu9Ykw4"  # Replace with your actual Google API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Streamlit page configuration
st.set_page_config(
    page_title="Document Q&A Assisstant",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #2E4053;  /* More professional dark blue color */
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-width: 100px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #2E4053;
        color: white;
    }
    /* Center the file uploader */
    [data-testid="stFileUploader"] {
        width: 60%;
        margin: 0 auto;
        display: block;
    }
    .chat-message {
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .query {
        background-color: #f8f9fa;
        border-left: 4px solid #2E4053;
    }
    .response {
        background-color: #f1f8ff;
        border-left: 4px solid #28a745;
    }
    .history-item {
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        cursor: pointer;
        transition: all 0.2s;
    }
    .history-item:hover {
        background-color: #e9ecef;
        transform: translateX(5px);
    }
    .history-question {
        color: #2E4053;
        font-weight: 500;
        font-size: 0.9rem;
    }
    .main-content {
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    /* Center align the title */
    h1 {
        text-align: center;
        color: #2E4053;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📄 Document Q&A App")
st.sidebar.info("Upload a document and ask questions based on its content.")
st.sidebar.markdown("### 📝 Chat History")
if st.session_state.chat_history:
    for i, (q, a) in enumerate(st.session_state.chat_history):
        st.sidebar.markdown(
            f"""<div class="history-item">
                <div class="history-question">Q: {q[:50]}{'...' if len(q) > 50 else ''}</div>
                </div>""", 
            unsafe_allow_html=True
        )
        if st.sidebar.button(f"View Answer", key=f"hist_{i}"):
            st.session_state.selected_qa = (q, a)

st.sidebar.markdown("---")
st.sidebar.write("Created with ❤️ using Streamlit by MuniMahesh.")

# Main Content
st.title("Document Q&A Assisstant")
st.subheader("Upload your document and ask any question!")

# File Uploader
uploaded_file = st.file_uploader("Upload your document (PDF only)", type="pdf")

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error("Error reading the PDF file. Ensure it's not password-protected or corrupted.")
        return None

def answer_question(question, context):
    """Get answer to a question based on the provided context using Gemini."""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')

        # Construct the prompt
        prompt = f"""Context: {context}\n\nQuestion: {question}\n
        Based on the context provided above, please answer the question. 
        If the answer cannot be found in the context, please say so."""

        # Generate response
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        st.error(f"Error generating the answer: {str(e)}")
        return None

if uploaded_file:
    # Extract text from uploaded PDF
    with st.spinner("Extracting text from the document..."):
        document_text = extract_text_from_pdf(uploaded_file)

    if document_text:
        st.success("Text extracted successfully!")
        # Display a preview of the extracted text
        with st.expander("Show Extracted Text (Preview)"):
            st.text_area("Extracted Document Text", value=document_text, height=300)

        # Question Input
        st.subheader("Ask a Question")
        
        # Create columns for question input
        col_q, col_space = st.columns([4, 1])
        
        with col_q:
            # Using a form to handle Enter key submission
            with st.form(key='question_form'):
                question = st.text_input("Your question:", label_visibility="collapsed")
                submit_form = st.form_submit_button("Submit", type="primary")

        # Handle form submission
        if submit_form and question:
            with st.spinner("Generating answer..."):
                answer = answer_question(question, document_text)

            if answer:
                # Add to chat history
                st.session_state.chat_history.append((question, answer))
                
                # Display current Q&A
                st.markdown("### Latest Response")
                st.markdown(f'<div class="chat-message query"><strong>Question:</strong> {question}</div>', 
                            unsafe_allow_html=True)
                st.markdown(f'<div class="chat-message response"><strong>Answer:</strong> {answer}</div>', 
                            unsafe_allow_html=True)
    else:
        st.info("👆 Upload a PDF file to get started!")

# Display selected Q&A from history if any
if 'selected_qa' in st.session_state:
    st.markdown("### Selected Response")
    q, a = st.session_state.selected_qa
    st.markdown(f'<div class="chat-message query"><strong>Question:</strong> {q}</div>', 
                unsafe_allow_html=True)
    st.markdown(f'<div class="chat-message response"><strong>Answer:</strong> {a}</div>', 
                unsafe_allow_html=True)