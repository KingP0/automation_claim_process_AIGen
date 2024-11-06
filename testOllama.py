from langchain_community.llms.ollama import Ollama

# Initialiser le modèle
MODEL = "phi3"
model = Ollama(model=MODEL, temperature=0)

# Exemple de test d'extraction d'entités sur le texte FNOL
response = model.invoke(f"Extract entities from this text: {fnol_text}")
print("Entities:", response)
