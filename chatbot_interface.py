import os
import time
import json
import fitz  # PyMuPDF
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from langchain_community.llms.ollama import Ollama
import torch
from torch.nn.functional import softmax
import base64  # For PDF encoding

# Init Ollama model
MODEL = "llava-phi3"  # LLaVA for text and image analysis
model = Ollama(model=MODEL, temperature=0)

# Paths
PDF_FOLDER_PATH = "lemans-courses-share/claims/"
IMAGE_FOLDER = "images/"

# Ensure folders exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Load embedding model and CLIP model
embedder = SentenceTransformer("all-MiniLM-L6-v2")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

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

def describe_image_with_clip(image_path):
    """Classifies an image into vehicle categories using CLIP."""
    image = Image.open(image_path).convert("RGB")
    prompts = [
        "Vehicle: helicopter",
        "Vehicle: airplane",
        "Vehicle: glider"
    ]
    
    # Prepare inputs for CLIP
    inputs = clip_processor(text=prompts, images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    
    # Score normalization
    logits_per_image = outputs.logits_per_image[0]
    probabilities = softmax(logits_per_image, dim=0)  # Convert to probabilities

    # Select the most probable category
    best_index = torch.argmax(probabilities).item()
    best_category = prompts[best_index].split(": ")[1]
    best_score = probabilities[best_index].item()

    return f"Predicted category: {best_category} (Confidence: {best_score:.2f})"

def format_context(fnol_text, contract_text, image_paths, question, predicted_category=None):
    """Formats the context to prepare the prompt."""
    images_section = "\n".join(image_paths) if image_paths else "No images available."
    return f"""
    Role: You are an assistant specialized in evaluating insurance claims using textual and visual evidence.

    Objective:
    Assess the provided evidence for consistency and accuracy regarding the incident description.
    The response needs to take a side (yes/no) and provide a brief justification based on the evidence.
    
    Category : HELI or Gyro (for helicopter), AIR or PLANE (for airplane) and GLI (for glider)
    When assessing the images, you only need to consider analyzing the vehicle type.
    Compare with detected Vehicle Category : {predicted_category}
    
    Incident Text:
    {fnol_text}

    Contract Text:
    {contract_text}

    Images:
    {images_section}

    Question:
    {question}
    """

# Function to encode PDF to base64 and create a downloadable/viewable link
def get_pdf_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
    return encoded_pdf

# --- Streamlit Interface ---
st.set_page_config(page_title="GenAI Claim Automatisation", layout="wide")
st.markdown('<h1 style="color:#6a0dad;">Automation of a Claim Process with GenAI</h1>', unsafe_allow_html=True)

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
    
    if selected_pdf:
        pdf_path = os.path.join(PDF_FOLDER_PATH, selected_pdf)
        encoded_pdf = get_pdf_base64(pdf_path)
        pdf_display = f'<a href="data:application/pdf;base64,{encoded_pdf}" target="_blank" style="color:#6a0dad;">View Raw PDF</a>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    if selected_pdf:
        pdf_data = database[selected_pdf]
        fnol_text = pdf_data["fnol_text"]
        contract_text = pdf_data["contract_text"]

        with col1:
            # Display FNOL Text
            st.markdown('<h3 style="color:#6a0dad;">FNOL Text</h3>', unsafe_allow_html=True)
            updated_fnol_text = st.text_area("", value=fnol_text, height=500)

        with col2:
            # Display contract text
            st.markdown('<h3 style="color:#6a0dad;">Contract Text</h3>', unsafe_allow_html=True)
            st.text_area("", value=contract_text, height=500, disabled=True)

        with col3:
            st.markdown('<h3 style="color:#6a0dad;">Incident Images</h3>', unsafe_allow_html=True)
            st.markdown("<br><br>", unsafe_allow_html=True) # Add space
            for img_path in pdf_data["images"]:
                st.image(img_path)
                description = describe_image_with_clip(img_path)
                st.write("Image Description using CLIP:")
                st.write(description)

        # Response Type
        st.markdown(f'<h3 style="color:#6a0dad;">{MODEL} Response</h3>', unsafe_allow_html=True)
        response_type = st.selectbox("Select Response Type:", [
            "Plausibility Check",
            "Coverage Insurance Matching"
        ], index=0)

        # Generate and display response
        predicted_category = describe_image_with_clip(img_path)
        
        if st.button("Generate Response"):
            question = f"Does the aircraft category mentioned in the FNOL {updated_fnol_text} match the detected vehicle type {predicted_category}? Respond with 'Yes' or 'No'. If 'No', briefly state the detected vehicle type. Do not consider insurance coverage. AIR is for airplane, GLI is for glider, and GYRO and HELI is for helicopter. (max 1 sentence)" \
                if response_type == "Plausibility Check" else \
                f"Does the incident align with the terms of the insurance contract based on the FNOL {updated_fnol_text} and contract text {contract_text} (If the cause of damage is covered by the contract by looking for similarities)? (max 1 sentence)"
            
            context = format_context(
                updated_fnol_text,
                contract_text,
                pdf_data["images"],
                question,
                predicted_category
            )
            
            start_time = time.time()
            response = model.invoke(context)
            end_time = time.time()
            response_time = end_time - start_time

            st.write(f"Response Time: {response_time:.2f} seconds")
            st.write(f"{MODEL}'s Response:", response)