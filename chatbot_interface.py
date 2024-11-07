import os
import fitz  # PyMuPDF
import streamlit as st
from langchain_community.llms.ollama import Ollama

# Init Ollama model
MODEL = "llava-phi3"  # LLaVA for text and image analysis
model = Ollama(model=MODEL, temperature=0)

# PDF folder path
pdf_folder_path = "lemans-courses-share/claims/"

# Extract data from PDF
def extract_and_load_data():
    data = {}
    for file_name in os.listdir(pdf_folder_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder_path, file_name)
            doc = fitz.open(pdf_path)
            fnol_text = doc[0].get_text() if doc.page_count > 0 else ""
            contract_text = doc[2].get_text() if doc.page_count > 2 else ""

            images = []
            if doc.page_count > 1:
                for img_index, img in enumerate(doc[1].get_images(full=True)):
                    image_name = f"{os.path.basename(pdf_path).split('.')[0]}_sinistre_image_{img_index}.png"
                    image_path = f"images/{image_name}"
                    if not os.path.exists(image_path):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                    images.append(image_path)

            data[file_name] = {
                "fnol_text": fnol_text,
                "contract_text": contract_text,
                "images": images
            }
    return data

# Load data
database = extract_and_load_data()

# Streamlit interface
st.title("Ollama Sinistre Verification Chatbot")

# Select PDF
selected_pdf = st.selectbox("Select a PDF file to analyze:", list(database.keys()))

# Subheader
st.subheader("Chat with Ollama")

# Context for ollama
context = """
You are an assistant specialized in assessing insurance claims based on textual and visual evidence.
Your task is to verify the plausibility of the claim by comparing the reported incident details (FNOL text) and the insurance contract
with the images provided. Look for inconsistencies or missing information in relation to the incident's description.
Provide concise, direct answers with short explanations on analysis limitations.
"""

# Input chatbot
user_input = st.text_input("Ask Ollama about the claim :")

if user_input:
    full_text = f"{context}\n\nIncident Text: {database[selected_pdf]['fnol_text']}\n\nContract Text: {database[selected_pdf]['contract_text']}\n\nQuestion: {user_input}"
    response = model.invoke(full_text)
    st.write("Ollama's Response:", response)
    
# Show content
if selected_pdf:
    st.subheader("FNOL Text")
    st.write(database[selected_pdf]["fnol_text"])
    
    st.subheader("Contract Text")
    st.write(database[selected_pdf]["contract_text"])
    
    st.subheader("Incident Images")
    for img_path in database[selected_pdf]["images"]:
        st.image(img_path)
