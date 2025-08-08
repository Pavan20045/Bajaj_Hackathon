import sys
import requests
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

def download_pdf(file_url, save_path):
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF downloaded successfully to {save_path}")
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        sys.exit(1)

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python index_faiss.py <pdf_url>")
        sys.exit(1)

    pdf_url = sys.argv[1]
    temp_pdf_path = "temp_download.pdf"

    # Step 1: Download PDF
    download_pdf(pdf_url, temp_pdf_path)

    # Step 2: Extract text
    text = extract_text_from_pdf(temp_pdf_path)

    if not text.strip():
        print("No text found in PDF.")
        sys.exit(1)

    # Step 3: Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([text])

    # Step 4: Create embeddings and FAISS index
    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local("faiss_index")
        print("FAISS index created and saved successfully.")
    except Exception as e:
        print(f"Error creating FAISS index: {e}")
        sys.exit(1)

    # Step 5: Clean up temp file
    if os.path.exists(temp_pdf_path):
        os.remove(temp_pdf_path)

if __name__ == "__main__":
    main()
