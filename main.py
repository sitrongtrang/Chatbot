from langchain_community.llms import CTransformers
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")

model_file = os.path.join(project_directory, r'Models\vinallama-2.7b-chat_q5_0.gguf')

class QABot:

    def __init__(self, model_file):
        self.model_file = model_file
        self.vector_db_path = os.path.join(project_directory, r'Data\vector_db\db_faiss')
        self.llm = None
        self.db = None

    def load_llm(self):
        self.llm = CTransformers(
            model=self.model_file,
            model_type='llama',
            max_new_tokens=1024,
            temperature=0.01
        )

        return self.llm

    def create_prompt(self, template):
        prompt = PromptTemplate(template=template, input_variables=['question'])
        return prompt

    def create_qa_chain(self, prompt):
        llm_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type='stuff',
            retriever=self.db.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=False
            #main_type_kwargs={'prompt': prompt}
        )
        return llm_chain

    def read_vectors_db(self):
        embedding = GPT4AllEmbeddings(model_name='all-MiniLM-L6-v2.gguf2.f16.gguf')
        self.db = FAISS.load_local(self.vector_db_path, embedding, allow_dangerous_deserialization=True)
        return self.db

    def run(self):
        self.load_llm()
        self.read_vectors_db()
        question = input("Nhập câu hỏi của bạn, nhập End chat. nếu muốn kết thúc: ")
        while question.strip() != "End chat.":
            template = """<|im_start|>system
            Sử dụng thông tin từ dữ liệu của bạn để trả lời bằng tiếng Việt. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời.
            <|im_end|>
            <|im_start|>user
            Giúp tôi với vấn đề này {question}.<|im_end|>
            <|im_start|>assistant
            """
            prompt = self.create_prompt(template)
            llm_chain = self.create_qa_chain(prompt)
            response = llm_chain.invoke({'query': question})
            print(response['result'])
            question = input("Nhập câu hỏi của bạn, nhập End chat. nếu muốn kết thúc: ")

qabot = QABot(model_file)
qabot.run()


