# 📄 PyraPDF.AI

**PyraPDF.AI** is an AI-powered assistant that allows users to upload and interact with PDF documents using advanced language models and vector-based search.

🔗 **Live App**: [https://prakhar-ai-pdf.vercel.app](https://prakhar-ai-pdf.vercel.app)
- [Watch the Demo Video](https://www.youtube.com/watch?v=n1R1FJVpmDs)
---

## 🧠 Features

- Upload and process PDF files
- Chat with PDF content using RAG (Retrieval-Augmented Generation)
- Isolation of PDF Chat with Pinecone Namespaces
- Vector search for relevant context
- Authentication using JWT and Google OAuth
- Realtime WebSocket interaction(used for [PyraPhone.ai](https://pyra-phone-ai.vercel.app) app transcription)

---

## 🏗️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, Pinecone , WebSockets
- **Frontend**: Next.js, Tailwind CSS
- **Auth**: JWT, Google OAuth
- **Deployment**: Vercel (Frontend), Render (Backend)

---

## 📁 Repository Structure
```Pyra.ai-pdf/
├── backend/   # Shared backend for both PyraPDF.AI and PyraPhone.AI
└── frontend/  # Frontend specific to PyraPDF.AI
```

---

## 🚀 Getting Started

1. **Clone the repository:**

```bash
git clone https://github.com/princeprakhar/Pyra.ai-pdf.git
```

2. **Backend Setup**
```
cd Pyra.ai-pdf/backend
# Create a .env file with required environment variables
# Install Python dependencies
pip install -r requirements.txt
uvicorn app.main:app --reload
```
3 . **Frontend Setup:**
```
cd ../frontend
npm install
npm run dev
```
## 📄 License
- Licensed under the MIT License.

