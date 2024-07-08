from TextExtractor import TextExtractor
from DataCleaner import DataCleaner
from EventHandler import EventHandler
from VectorPreparer import VectorPreparer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
from dotenv import load_dotenv

load_dotenv()

project_directory = os.getenv("PROJECT_DIR")

class Preprocessor:

    def __init__(self):
        self.text_extractor = TextExtractor()
        self.data_cleaner = DataCleaner()
        self.vector_preparer = VectorPreparer()
        self.preprocessors = [self.text_extractor, self.data_cleaner, self.vector_preparer]
        self.project_directory = project_directory
        self.image_directory = os.path.join(self.project_directory, 'Data\images')

    def preprocess(self, name):
        for preprocessor in self.preprocessors:
            name = preprocessor.run(name)
            name, ext = os.path.splitext(name)

    def preprocess_all_files(self):
        for preprocessor in self.preprocessors:
            preprocessor.run_all_files()

        # for name in os.listdir(self.image_directory):
        #     self.preprocess(name)

    def run(self):
        print("Preprocessor is running")
        event_handler = EventHandler(callback=self.preprocess)
        observer = Observer()
        observer.schedule(event_handler, self.image_directory, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

preprocessor = Preprocessor()
# preprocessor.preprocess_all_files()
# preprocessor.text_extractor.extract_all_files()
preprocessor.data_cleaner.clean_all_files()
# preprocessor.vector_preparer.create_db_all_files()
# preprocessor.text_extractor.extract_text_from_image("02E61744-9F9E-4CB6-B647-1A466FBFA2E7.png")
# preprocessor.data_cleaner.clean_data("02E61744-9F9E-4CB6-B647-1A466FBFA2E7.txt")
# preprocessor.vector_preparer.create_db("02E61744-9F9E-4CB6-B647-1A466FBFA2E7.txt")