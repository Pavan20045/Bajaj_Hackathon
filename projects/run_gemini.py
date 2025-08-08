import sys
import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

load_dotenv()

def load_faiss_index():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return FAISS.load_local("projects/faiss_index", embeddings, allow_dangerous_deserialization=True)

def answer_question(query):
    db = load_faiss_index()
    retriever = db.as_retriever(search_kwargs={"k": 3})

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever)

    response = qa_chain({"question": query, "chat_history": []})
    return response["answer"]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_gemini.py <question>")
        sys.exit(1)

    question = sys.argv[1]
    print(answer_question(question))
