import fitz  # PyMuPDF
from langchain_community.llms.ollama import Ollama

# Init model
MODEL = "phi3"
model = Ollama(model=MODEL, temperature=0)

pdf_path = "lemans-courses-share/claims/fnol_ANC23LA011.pdf"

# Extract text FNOL & Contract
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    fnol_text = doc[0].get_text() if doc.page_count > 0 else ""
    contract_text = doc[2].get_text() if doc.page_count > 2 else ""
    return fnol_text, contract_text

def main():
    
    fnol_text, contract_text = extract_text_from_pdf(pdf_path)

    print("\nFNOL Text :\n", fnol_text)
    print("\nContract Text :\n", contract_text)

    # Context
    context = """
    You are an assistant specialized in assessing insurance claims based on textual evidence.
    Your task is to verify the plausibility of the claim by comparing the reported incident details (FNOL text) and the insurance contract.
    Look for inconsistencies or missing information in relation to the incident's description.
    Provide concise, direct answers.
    """

    while True:
        user_input = input("\nPosez votre question sur le sinistre (ou tapez 'exit' pour quitter) : ")
        if user_input.lower() == "exit":
            print("Fin de l'analyse.")
            break

        full_text = f"{context}\n\nIncident Text: {fnol_text}\n\nContract Text: {contract_text}\n\nQuestion: {user_input}"
        response = model.invoke(full_text)
        print("\nAnalyse :", response)

if __name__ == "__main__":
    main()
