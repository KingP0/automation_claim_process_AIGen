# Automation of a Claims Process with Generative AI

Retrieve data from GitHub : 
```
git clone https://github.com/atracordis/lemans-courses-share
```

Install libraries :

- PDF and Image handling
  ```
  pip install pymupdf
  ```
- Streamlit for web-based interface
  ```
  pip install streamlit
  ```
- LangChain and Ollama model integration
  ```
  pip install langchain
  pip install langchain_community
  ```
- Optional: install pillow if image handling or display issues occur
  ```
  pip install pillow
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
