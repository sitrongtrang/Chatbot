from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")

class VectorPreparer:

    def __init__(self):
        self.project_directory = project_directory
        self.data_directory = os.path.join(self.project_directory, 'Data\cleaned_data')
        self.vector_db_directory = os.path.join(self.project_directory, r'Data\vector_db')
        self.embedding = GPT4AllEmbeddings(model_name='all-MiniLM-L6-v2.gguf2.f16.gguf')

    def create_db(self, name):
        data_file = os.path.join(self.data_directory, name)
        print(f'Preparing vector db from file: {data_file}')
        with open(data_file, 'r', encoding='utf-8') as file:
            text = file.read()

        if len(text.strip()) == 0:
            return

        text_splitter = CharacterTextSplitter(
            separator='\n',
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )

        chunks = text_splitter.split_text(text)

        db = FAISS.from_texts(texts=chunks, embedding=self.embedding)

        name, ext = os.path.splitext(name)
        vector_db_file = os.path.join(self.vector_db_directory, name)
        db.save_local(vector_db_file)
        return db

    def create_db_all_files(self):
        prev_db = None
        for name in os.listdir(self.data_directory):
            curr_db = self.create_db(name)
            if prev_db is not None:
                if curr_db is not None:
                    prev_db.merge_from(curr_db)
            else:
                prev_db = curr_db

        vector_db_file = os.path.join(self.vector_db_directory, r'db_faiss')
        prev_db.save_local(vector_db_file)
        return prev_db


    def run(self, name):
        name = name + '.txt'
        self.create_db(name)
        return name

    def run_all_files(self):
        self.create_db_all_files()
        return


