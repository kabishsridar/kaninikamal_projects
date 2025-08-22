from PyPDF2 import PdfReader

reader = PdfReader("data_store.pdf")
for page in reader.pages:
    print(page.extract_text())

with open("data_store.pdf", "rb") as f:
    print(f.read(200))  # first 200 bytes