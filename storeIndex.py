from dotenv import load_dotenv
import os
from src.helper import load_pdf_files, filter_to_minimal_docs, text_split, download_embeddings
from langchain_community.vectorstores import FAISS


extracted_data= load_pdf_files(data='data/')
filter_data = filter_to_minimal_docs(extracted_data)
text_chunks=text_split(filter_data)

embeddings = download_embeddings()


faiss_index = FAISS.load_local("faiss_medical_index", embeddings, allow_dangerous_deserialization=True)
retriever = faiss_index.as_retriever(search_type="similarity", search_kwargs={"k": 3})
