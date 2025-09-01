from paddleocr import PaddleOCR
import os, questionary

def list_files(path="."):
    return [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and not f.startswith('.')      # ignore hidden files
        and f.lower() != "desktop.ini" # ignore Windows system file
    ]

if __name__ == "__main__":

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)

    base_path = input("Provide the Folder path: (Default is Downloads) ")

    if base_path == "":
        base_path = "C:\\Users\\uberdev\\Downloads\\" 

    files = list_files(base_path)
    print(files)

    choice = questionary.select(
        "Select a file:",
        choices=files
    ).ask()

    print("You picked:", choice)
    
    # Run OCR inference on a sample image 
    result = ocr.predict(input=choice)

    # Visualize the results and save the JSON results
    for res in result:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")