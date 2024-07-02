import re
import os
from bs4 import BeautifulSoup
from underthesea import text_normalize, word_tokenize
from deep_translator import GoogleTranslator
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")

abbre_dict = {"lms": "hệ thống quản lý học tập",
              "csdl": "cơ sở dữ liệu",
              "ko": "không",
              "r": "rồi",
              "hs": "học sinh",
              "k": "không",
              "c": "chị",
              "a": "anh",
              "e": "em",
              "gv": "giáo viên",
              "đc": "được",
              "dc": "được",
              "thpt": "trung học phổ thông",
              "trc": "trước",
              "bt": "bình thường",
              "tk": "tài khoản",
              "đhqg": "đại học quốc gia"}
MAX_LENGTH = 512
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def join_tokens(tokens):
    sentence = ""

    for token in tokens:

        if token in [',', '.', '?', ':', '!', ';', '..', '...']:
            sentence += token
        else:
            if sentence and sentence[-1] != ' ':
                sentence += ' '
            sentence += token

    return sentence

class DataCleaner:

    def __init__(self):
        self.project_directory = project_directory
        self.text_directory = os.path.join(self.project_directory, 'Data\extracted_texts')
        self.cleaned_data_directory = os.path.join(self.project_directory, 'Data\cleaned_data')

    def remove_html_elements(self, text):
        soup = BeautifulSoup(text, "html.parser")
        for element in soup.find_all(True):
            element.decompose()
        return str(soup)

    def clean_data(self, name):
        clean_file = os.path.join(self.text_directory, name)
        print(f'Cleaning file: {clean_file}')
        with open(clean_file, 'r', encoding='utf-8') as file:
            text = file.read()

        self.remove_html_elements(text)
        pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in abbre_dict.keys()) + r')\b',
                             re.IGNORECASE)

        text = pattern.sub(lambda x: abbre_dict[x.group().lower()], text)

        sents = text.split('-')
        sents = [sent.strip() for sent in sents if len(sent.strip()) > 0]

        corrector = pipeline("text2text-generation", model="bmd1905/vietnamese-correction")

        predictions = corrector(sents, max_length=MAX_LENGTH)
        sents = [pred['generated_text'] for pred in predictions]

        reformed_sents = [sent.lstrip('-').strip() for sent in sents]

        # translator = GoogleTranslator(src='auto', target='vi')
        # for i, sent in enumerate(reformed_sents):
        #     tokens = word_tokenize(sent)
        #     for j, token in enumerate(tokens):
        #         try:
        #             res = translator.translate(token)
        #             if res is not None:
        #                 tokens[j] = res
        #             else:
        #                 tokens[j] = token
        #         except:
        #             tokens[j] = token
        #
        #     reformed_sents[i] = join_tokens(tokens)


        #sents = [sent for sent in sents if not is_time_format(sent)]

        text = '\n'.join(reformed_sents)

        print(text)

        name, ext = os.path.splitext(name)
        write_file = os.path.join(self.cleaned_data_directory, name + '.txt')
        with open(write_file, 'w', encoding='utf-8') as text_file:
            text_file.write(''.join(text))
        print(f'Done writing to file: {write_file}')

    def clean_all_files(self):
        for name in os.listdir(self.text_directory):
            self.clean_data(name)

    def run(self, name):
        name = name + '.txt'
        self.clean_data(name)
        return name

    def run_all_files(self):
        self.clean_all_files()
        return
