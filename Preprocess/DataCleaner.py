import re
import os
from bs4 import BeautifulSoup
from underthesea import text_normalize, word_tokenize
from deep_translator import GoogleTranslator
from transformers import pipeline
import json
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")

# abbre_dict = {"lms": "learning management system"}
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
        self.cleaned_data_directory = os.path.join(self.project_directory, 'Data\cleaned_data')
        self.page_directory = os.path.join(self.project_directory, 'Data\pages')
        url_file = os.path.join(self.project_directory, r'Data\urls.json')
        with open(url_file, 'r') as file:
            self.urls = json.load(file)

    def remove_html_elements(self, text):
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all('a'):
            title = self.find_title(a['href'])
            if len(title) > 0:
                a.replace_with(f"{a.text} ({title})")
            else:
                a.replace_with(f"{a.text}")
        clean_text = soup.get_text()
        return clean_text

    def find_title(self, href):
        for url in self.urls:
            if href == url['url'] or href.replace('community.canvaslms.com:443', 'community.canvaslms.com') == url['url']:
                return url['title']
        return ''

    def clean_data(self, name):
        clean_file = os.path.join(self.page_directory, name)
        print(f'Cleaning file: {clean_file}')
        with open(clean_file, 'r', encoding='utf-8') as file:
            text = file.read()

        text = self.remove_html_elements(text)
        lines = text.split('\n')
        lines = [line for line in lines if len(line.strip()) > 0]
        text = '\n'.join(lines)
        # pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in abbre_dict.keys()) + r')\b', re.IGNORECASE)

        # text = pattern.sub(lambda x: abbre_dict[x.group().lower()], text)

        # sents = text.split('-')
        # sents = [sent.strip() for sent in sents if len(sent.strip()) > 0]
        #
        # corrector = pipeline("text2text-generation", model="bmd1905/vietnamese-correction")
        #
        # predictions = corrector(sents, max_length=MAX_LENGTH)
        # sents = [pred['generated_text'] for pred in predictions]
        #
        # reformed_sents = [sent.lstrip('-').strip() for sent in sents]

        # sents = [sent for sent in sents if not is_time_format(sent)]

        # text = '\n'.join(reformed_sents)

        print(text)

        name, ext = os.path.splitext(name)
        text = name + '\n' + text

        # chunks = []
        # curr_chunk = ''
        # lines = text.split('\n')
        # for line in lines:
        #     if len(line) + len(curr_chunk) < 5000:
        #         curr_chunk += line + "\n"
        #     else:
        #         chunks.append(curr_chunk)
        #         curr_chunk = line + "\n"
        #
        # chunks.append(curr_chunk)
        #
        # translator = GoogleTranslator(src='auto', target='vi')
        # chunks = [translator.translate(chunk) for chunk in chunks]
        # # text = translator.translate(text)
        # text = '\n'.join(chunks)
        # print(text)

        write_file = os.path.join(self.cleaned_data_directory, name + '.txt')
        with open(write_file, 'w', encoding='utf-8') as text_file:
            text_file.write(''.join(text))
        print(f'Done writing to file: {write_file}')

    def clean_all_files(self):
        for name in os.listdir(self.page_directory):
            self.clean_data(name)

    def run(self, name):
        name = name + '.txt'
        self.clean_data(name)
        return name

    def run_all_files(self):
        self.clean_all_files()
        return
