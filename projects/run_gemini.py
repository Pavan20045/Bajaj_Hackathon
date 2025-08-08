import sys
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_gemini.py <query>")
        sys.exit(1)

    query = sys.argv[1]

    # Step 1: Load FAISS index
    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        sys.exit(1)

    # Step 2: Set up QA chain
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    prompt_template = """
    You are an AI assistant. Use the following context to answer the question accurately.

    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    # Step 3: Run the query
    try:
        result = qa_chain({"query": query})
        print("Answer:", result["result"])
        print("\nSources:")
        for doc in result["source_documents"]:
            print("-", doc.metadata)
    except Exception as e:
        print(f"Error running QA chain: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
