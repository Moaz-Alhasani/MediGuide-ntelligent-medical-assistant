from flask import Flask, render_template, jsonify, request
from src.helper import download_embeddings
from langchain_community.vectorstores import FAISS
from google import genai
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


embeddings = download_embeddings()
faiss_index = FAISS.load_local("faiss_medical_index", embeddings, allow_dangerous_deserialization=True)
retriever = faiss_index.as_retriever(search_type="similarity", search_kwargs={"k": 3})

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


system_prompt = (
    "Your name is 'MediGuide', an intelligent medical assistant. "
    "Use **only** the information provided below to accurately and concisely answer the user's question.\n\n"
    "Question:\n{question}\n\n"
    "Available Information:\n{context_text}\n\n"
    "Answer:"
)

def generate_answer(question, retriever):
    print("User question:", question)
    context_docs = retriever.get_relevant_documents(question)
    print("Docs found:", len(context_docs))
    for i, doc in enumerate(context_docs):
        print(f"Doc {i} source:", doc.metadata.get("source"))

    context_text = "\n\n".join([doc.page_content for doc in context_docs]) if context_docs else "No context found."
    prompt = system_prompt.format(question=question, context_text=context_text)
    print("Prompt length:", len(prompt))

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,

    )
    print("Response received")
    return response.text.strip()


@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    answer = generate_answer(user_input, retriever)
    return jsonify({"answer": answer})


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000)
