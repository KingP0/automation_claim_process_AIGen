import fitz  # PyMuPDF

# Chemin vers le dossier PDF
pdf_path = "lemans-courses-share/claims/fnol_ANC23LA011.pdf"

# Ouvrir le fichier PDF
doc = fitz.open(pdf_path)

# Extraire le texte de la première page (FNOL) et du contrat
fnol_text = doc[0].get_text()  # Première page (FNOL)
contract_text = doc[2].get_text()  # Troisième page (Contrat)

# Extraire et enregistrer les images de la deuxième page (photo du sinistre)
for img_index, img in enumerate(doc[1].get_images(full=True)):
    xref = img[0]
    base_image = doc.extract_image(xref)
    image_bytes = base_image["image"]
    with open(f"images/sinistre_image_{img_index}.png", "wb") as img_file:
        img_file.write(image_bytes)

print("FNOL:", fnol_text)
print("Contract:", contract_text)
