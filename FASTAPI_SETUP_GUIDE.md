# 🚀 FastAPI Python Project – Full Setup Guide (Copy-Paste Ready)

## 0️⃣ System prerequisites (run once)
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python-is-python3
```

Verify:
```bash
python --version
```

## 1️⃣ Create project directory
```bash
mkdir fastapi-project
cd fastapi-project
```

## 2️⃣ Create virtual environment (once per project)
```bash
python -m venv .venv
```

## 3️⃣ Activate virtual environment (every time you work)
```bash
source .venv/bin/activate
```

You should see:
```
(.venv) user@machine:~/fastapi-project$
```

## 4️⃣ Upgrade pip (recommended)
```bash
python -m pip install --upgrade pip
```

## 5️⃣ Install project dependencies
```bash
python -m pip install fastapi uvicorn python-dotenv
```

For file upload, PDF, embeddings, DB:
```bash
python -m pip install python-multipart pypdf sentence-transformers pymongo
```

## 6️⃣ Save dependencies
```bash
python -m pip freeze > requirements.txt
```

## 7️⃣ Create project structure
```bash
mkdir app
touch app/main.py app/config.py .env .gitignore
```

## 8️⃣ Add .gitignore
```bash
echo ".venv" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__" >> .gitignore
```

## 9️⃣ Add .env file
```bash
cat <<EOF > .env
APP_NAME=FastAPI Starter
EOF
```

## 🔟 Add FastAPI app

**app/config.py**
```python
from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "FastAPI App")
```

**app/main.py**
```python
from fastapi import FastAPI
from app.config import APP_NAME

app = FastAPI(title=APP_NAME)

@app.get("/")
def root():
    return {"message": f"Hello from {APP_NAME} 🚀"}
```

## 1️⃣1️⃣ Run the FastAPI server
```bash
python -m uvicorn app.main:app --reload
```

## 1️⃣2️⃣ Open in browser

API:
```
http://127.0.0.1:8000
```

Interactive Docs (Swagger):
```
http://127.0.0.1:8000/docs
```

## 1️⃣3️⃣ Stop server
```
CTRL + C
```

## 1️⃣4️⃣ Deactivate virtual environment (optional)
```bash
deactivate
```

## 1️⃣5️⃣ Restart project later
```bash
cd fastapi-project
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

## ✅ Summary (Mental Model)
```
Create project → create venv → activate venv
→ install packages → freeze requirements
→ write FastAPI app → run uvicorn
```
