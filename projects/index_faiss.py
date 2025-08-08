import sys
import os
from supabase import create_client
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def download_pdf(file_name):
    """Download the uploaded PDF from Supabase Storage."""
    response = supabase.storage.from_(SUPABASE_BUCKET).download(file_name)
    if isinstance(response, bytes):
        temp_path = os.path.join(tempfile.gettempdir(), file_name)
        with open(temp_path, "wb") as f:
            f.write(response)
        return temp_path
    else:
        raise Exception(f"Failed to download {file_name}: {response}")

def build_faiss_index(pdf_path):
    """Load PDF, split text, and store FAISS index."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = FAISS.from_documents(texts, embeddings)

    db.save_local("projects/faiss_index")
    print("FAISS index saved successfully")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python index_faiss.py <file_name_in_supabase>")
        sys.exit(1)

    file_name = sys.argv[1]
    pdf_path = download_pdf(file_name)
    build_faiss_index(pdf_path)
