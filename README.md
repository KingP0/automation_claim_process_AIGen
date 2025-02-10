# Automation of a Claims Process with Generative AI

Retrieve data from GitHub : 
```
git clone https://github.com/atracordis/lemans-courses-share.git
```
Clone this repository :
```
git clone https://github.com/KingP0/automation_claim_process_AIGen.git
```

Install libraries :
  ```
  python -m venv venv
  source venv/bin/activate  # Sur Mac/Linux
  venv\Scripts\activate  # Sur Windows
  pip install -r automation_claim_process_AIGen/requirements.txt
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
