import os
import time
import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

class TextExtractor:

    def __init__(self):
        self.project_directory = project_directory
        self.image_directory = os.path.join(self.project_directory, 'Data\images')
        self.text_directory = os.path.join(self.project_directory, 'Data\extracted_texts')
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")

    def preprocess_image(self, image):
        # return image
        grayscale_img = image.convert('L')


        threshold = 150
        binary_img = grayscale_img.point(lambda p: p > threshold and 255)

        filtered_img = binary_img.filter(ImageFilter.GaussianBlur(radius=2))

        enhanced_img = ImageEnhance.Contrast(filtered_img).enhance(2.0)
        return enhanced_img

    def extract_text_from_image(self, name):
        extract_file = os.path.join(self.image_directory, name)
        print(f'Extracting file: {extract_file}')

        image = Image.open(extract_file)
        # image = self.preprocess_image(image)
        # image.show()
#         prompt = f'''Trích xuất văn bản từ hình ảnh này, theo dạng sau đây:
# Nội dung:
# Nội dung tin nhắn:
#     Các tin nhắn trong cuộc trò chuyện, mỗi tin nhắn là một dòng bắt đầu bằng dấu -
# Phân tích:
# Lưu ý:
# Kết luận:
# '''
        prompt = f'''Trích xuất các tin nhắn từ hình ảnh sau đây, mỗi tin nhắn là một dòng, bắt đầu bằng dấu -. Nếu không có tin nhắn thì trả lời bằng một dòng rỗng bắt đầu bằng -.'''
        # prompt = f'''Trích xuất văn bản từ hình ảnh sau đây'''

        response = self.model.generate_content([image, prompt])
        extracted_text = response.text

        print(extracted_text)
        name, ext = os.path.splitext(name)
        write_file = os.path.join(self.text_directory, name + '.txt')
        with open(write_file, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        print(f'Done writing to file: {write_file}')

    def extract_all_files(self):
        for name in os.listdir(self.image_directory):
            while True:
                try:
                    self.extract_text_from_image(name)
                    break
                except:
                    time.sleep(1*60)

    def run(self, name):
        self.extract_text_from_image(name)
        return name

    def run_all_files(self):
        self.extract_all_files()
        return



