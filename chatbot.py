from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings, GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import OpenAI, CTransformers
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from dotenv import load_dotenv
import os

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")
data_directory = os.path.join(project_directory, r"Data\cleaned_data")

model_file = os.path.join(project_directory, r'Models\llama-2-7b-chat.Q8_0.gguf')
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API")
persist_directory = 'Data/vector_db'

class QABot:

    def __init__(self):
        self.llm = None
        self.retriever = None
        self.qa_chain = None

    def load_llm(self):
        self.llm = CTransformers(
            model=model_file,
            model_type='llama',
            max_new_tokens=1024,
            temperature=0.01
        )

        return self.llm
    
    def read_vector_db(self):
        embedding = GPT4AllEmbeddings(model_name='all-MiniLM-L6-v2.gguf2.f16.gguf', device="cpu")
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
        self.retriever = vectordb.as_retriever(search_kwargs={"k": 2})

    def create_qa_chain(self):
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,
                                  chain_type="stuff",
                                  retriever=self.retriever,
                                  return_source_documents=True)
        return self.qa_chain

    def process_llm_response(self, llm_response):
        print(llm_response['result'])
        print('\n\nSources:')
        for source in llm_response["source_documents"]:
            print(source.metadata['source'])

    def run(self):
        self.load_llm()
        self.read_vector_db()
        self.create_qa_chain()

    def __call__(self, query):
        llm_response = self.qa_chain(query)
        self.process_llm_response(llm_response)


qabot = QABot()
qabot.run()

question = input("Nhập câu hỏi của bạn, nhập End chat. nếu muốn kết thúc: ")
while question.strip() != "End chat.":
    qabot(question)
    question = input("Nhập câu hỏi của bạn, nhập End chat. nếu muốn kết thúc: ")