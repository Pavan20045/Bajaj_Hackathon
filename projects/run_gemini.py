import os
import google.generativeai as genai

# Set your Gemini API key
GEMINI_API_KEY = "AIzaSyDwA8SD1aN9yFTHlbMbJiegk30YBCv96jE"
genai.configure(api_key=GEMINI_API_KEY)

def load_chunks(file_path="retrieved_chunks.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def query_gemini(question):
    chunks = load_chunks()
    context = "\n".join(chunks)
    
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Answer the question based on the following document:\n{context}\n\nQuestion: {question}"
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    question = "What is the summary of the document?"
    print(query_gemini(question))
