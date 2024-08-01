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

text_loader_kwargs = {'encoding': 'utf-8'}
loader = DirectoryLoader(data_directory, glob="./*.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

persist_directory = 'Data/vector_db'

embedding = GPT4AllEmbeddings(model_name='all-MiniLM-L6-v2.gguf2.f16.gguf', device="cpu")
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)


batch_size = 100

for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    print("Start batch\n", batch)
    vectordb.add_documents(documents=batch)
    print("Finish batch\n", batch)
    vectordb.persist()

vectordb.persist()

# vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
# retriever = vectordb.as_retriever(search_kwargs={"k": 2})
#
# llm = CTransformers(
#         model=model_file,
#         model_type='llama',
#         max_new_tokens=1024,
#         temperature=0.01
#     )
#
# qa_chain = RetrievalQA.from_chain_type(llm=llm,
#                                   chain_type="stuff",
#                                   retriever=retriever,
#                                   return_source_documents=True)
#
# def process_llm_response(llm_response):
#     print(llm_response['result'])
#     print('\n\nSources:')
#     for source in llm_response["source_documents"]:
#         print(source.metadata['source'])
#
# query = "Can students view unpublished assignments?"
# llm_response = qa_chain(query)
# process_llm_response(llm_response)
