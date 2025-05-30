from PyPDF2 import PdfReader

def load_file(file_path):
    reader = PdfReader(file_path)
    return [page.extract_text() or "" for page in reader.pages]
