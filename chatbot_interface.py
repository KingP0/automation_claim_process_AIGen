import os
import time
import fitz  # PyMuPDF
import streamlit as st
from langchain_community.llms.ollama import Ollama

# Init Ollama model
MODEL = "llava-phi3"  # LLaVA for text and image analysis
model = Ollama(model=MODEL, temperature=0)

# PDF folder path
PDF_FOLDER_PATH = "lemans-courses-share/claims/"
IMAGE_FOLDER = "images/"

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# --- Utility Functions ---
def extract_data_from_pdf(pdf_path):
    """Extracts text and images from a PDF file."""
    doc = fitz.open(pdf_path)
    fnol_text = doc[0].get_text() if doc.page_count > 0 else ""
    contract_text = doc[2].get_text() if doc.page_count > 2 else ""

    images = []
    if doc.page_count > 1:
        for img_index, img in enumerate(doc[1].get_images(full=True)):
            image_name = f"{os.path.basename(pdf_path).split('.')[0]}_sinistre_image_{img_index}.png"
            image_path = os.path.join(IMAGE_FOLDER, image_name)
            if not os.path.exists(image_path):
                xref = img[0]
                base_image = doc.extract_image(xref)
                with open(image_path, "wb") as img_file:
                    img_file.write(base_image["image"])
            images.append(image_path)

    return {
        "fnol_text": fnol_text,
        "contract_text": contract_text,
        "images": images
    }


def format_context(fnol_text, contract_text, image_paths, question):
    """Formats the context to include text and image references."""
    images_section = "\n".join(image_paths) if image_paths else "No images available."
    return f"""
    Role: You are an assistant specialized in evaluating insurance claims using textual and visual evidence.

    Objective:
    1. Assess the provided evidence for consistency and accuracy regarding the incident description.
    2. Answer the given questions concisely, focusing on key elements that support your decision.

    Guidelines:
    - Responses must only indicate whether the information is right or wrong based on the evidence provided.
    - Do not highlight missing information from the text or images.
    - Be lenient when assessing images, as they may be poorly taken. If at least one correct element is identifiable, even if minimal, it is sufficient.
    (e.g., the right vehicle is shown, it is the right vehicle model or similar, etc.)
    - Provide answers as "Yes" or "No" to indicate your conclusion.

    Incident Text:
    {fnol_text}

    Contract Text:
    {contract_text}

    Images:
    {images_section}

    Question:
    {question}
    """


# --- Streamlit Interface ---
st.set_page_config(page_title="GenAI Claim Automatisation", layout="wide")
st.title("Automation of a Claim Process with GenAI")

# Select PDFs to extract
pdf_files = [file for file in os.listdir(PDF_FOLDER_PATH) if file.endswith(".pdf")]
if "selected_pdfs" not in st.session_state:
    st.session_state.selected_pdfs = []

if st.button("Select All PDFs"):
    st.session_state.selected_pdfs = pdf_files
else:
    if st.session_state.selected_pdfs != pdf_files:
        st.session_state.selected_pdfs = st.multiselect("Select PDF file(s) to extract:", pdf_files, default=st.session_state.selected_pdfs)

# Extract and display data
database = {}
if st.session_state.selected_pdfs:
    for pdf_file in st.session_state.selected_pdfs:
        pdf_path = os.path.join(PDF_FOLDER_PATH, pdf_file)
        database[pdf_file] = extract_data_from_pdf(pdf_path)
    st.success(f"Extracted data from {len(st.session_state.selected_pdfs)} PDF(s).")
else:
    st.warning("Please select at least one PDF to extract.")

# Analyze selected PDF
if database:
    selected_pdf = st.selectbox("Select a PDF file to analyze:", list(database.keys()))

    col1, col2, col3 = st.columns(3)
    if selected_pdf:
        pdf_data = database[selected_pdf]
        fnol_text = pdf_data["fnol_text"]
        contract_text = pdf_data["contract_text"]
        
        with col1:
            # Display FNOL Text
            st.subheader("FNOL Text")
            updated_fnol_text = st.text_area("Edit FNOL Text:", value=fnol_text, height=400)

            # Update FNOL text
            if st.button("Update FNOL Text"):
                database[selected_pdf]["fnol_text"] = updated_fnol_text
                st.success("FNOL text updated.")

        with col2:
            # Display contract text and images
            st.subheader("Contract Text")
            st.write(contract_text)

        with col3:
            st.subheader("Incident Images")
            for img_path in pdf_data["images"]:
                st.image(img_path)

        # Response Type
        st.subheader(f"{MODEL} Response")
        response_type = st.selectbox("Select Response Type:", [
            "Plausibility Check",
            "Coverage Insurance Matching"
        ], index=0)

        # Generate and display response
        if st.button("Generate Response"):
            question = "Can you assess the plausibility of the reported incident based on the provided FNOL information and image (without checking contract)? (1 sentence)" \
                if response_type == "Plausibility Check" else \
                "Does the incident align with the terms of the insurance contract based on the FNOL and contract text? (1 sentence)"
            context = format_context(
                updated_fnol_text,
                contract_text,
                pdf_data["images"],
                question
            )
            start_time = time.time()
            response = model.invoke(context)
            end_time = time.time()
            response_time = end_time - start_time
            
            st.write(f"Response Time: {response_time:.2f} seconds")
            st.write(f"{MODEL}'s Response:", response)