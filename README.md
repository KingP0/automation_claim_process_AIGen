# Automation of a Claims Process with Generative AI

Retrieve data from GitHub : https://github.com/atracordis/lemans-courses-share

Install libraries :

- PDF and Image handling
  ```
  pip install pymupdf  # For working with PDFs (PyMuPDF library)
  ```
- Streamlit for web-based interface
  ```
  pip install streamlit  # For building interactive interfaces
  ```
- LangChain and Ollama model integration
  ```
  pip install langchain  # LangChain for LLM integration
  pip install langchain_community  # Community-contributed integrations for LangChain
  ```
- Optional: install pillow if image handling or display issues occur
  ```
  pip install pillow  -- For image processing (used implicitly by some functions in PyMuPDF)
  ```

Launch Ollama chatbot :

- Install and start Ollama phi3 : Usefull for text handling but not for images
  ```
  ollama serve & ollama pull phi3
  ollama serve & ollama run phi3
  ```
- Install and start Ollama llava-phi3 : Can analyse images unlike phi3
  ```
  ollama serve & ollama pull llava-phi3
  ollama serve & ollama run llava-phi3
  ```
- Start chatbot interface :
  ```
  streamlit run automation_claim_process_AIGen/chatbot_interface.py
  ```
