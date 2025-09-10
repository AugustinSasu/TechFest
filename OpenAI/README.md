# Installation

To install the required Python packages for the backend, run:

```powershell
pip install -r ..\backend\requirements.txt
```

Make sure you are using the correct Python environment.
# OpenAI Business Assistant - How to Run

## Backend (API)

1. Pornește backendul FastAPI (din folderul OpenAI):
   ```sh
   uvicorn api_secretary:app --reload --port 1919
   ```

## Frontend

### Chat UI (Recomandat)
- Deschide `frontend_secretary_chat.html` în browser (Chrome/Edge).
- Toate interacțiunile se fac ca într-un chat conversațional.

### UI Clasic (cu dropdown-uri)
- Deschide `frontend_secretary_full.html` în browser pentru interfața completă cu selectare clasică.

