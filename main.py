import os, re
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint   
from langchain.indexes import VectorstoreIndexCreator
from datetime import datetime
from huggingface_hub.utils._errors import HfHubHTTPError
from constants import OPENAI_API_KEY, HUGGINGFACEHUB_API_TOKEN
# loader = TextLoader("./index.md")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN


def read_vtt_file(file_path, title):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            vtt_contents = f"{title} === {f.read()}"
        return clean_spacing(remove_timestamps(vtt_contents))
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")


def list_and_read_vtt_files(directory):
    try:
        files: list[str] = os.listdir(directory)
        vtt_files = [f.strip() for f in files if f.endswith(".vtt")]
        print(vtt_files)
        output = []
        for vtt_file in vtt_files:
            file_path = os.path.join(directory, vtt_file)
            vtt_content = read_vtt_file(file_path, vtt_file)
            output.append(vtt_content)
        return " ".join(output)
    except Exception as e:
        print(f"Error listing or reading files: {e}")




def clean_spacing(text):
    # Define the regex pattern to match multiple consecutive whitespace characters
    pattern = r"\s+"

    # Use re.sub to replace multiple whitespace characters with a single space
    cleaned_text = re.sub(pattern, " ", text)

    return cleaned_text.strip()


def remove_timestamps(vtt_content):
    # Define the regex pattern to match the time numbers
    pattern = r"\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}\.\d{3}"

    # Use re.sub to replace matched patterns with empty string
    cleaned_content = re.sub(pattern, "", vtt_content)

    return cleaned_content

def list_folders_in_data_subfolder():
    data_folder = os.path.join(os.getcwd(), "data")
    print(data_folder)
    if not os.path.isdir(data_folder):
        print(f"Error: '{data_folder}' is not a valid directory.")
        return []
    
    folders = [folder for folder in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, folder))]
    return folders

def save_xlsx():
    title_ = input("what is your sheet title, 0 to default (output) : ")
    title_ = title_ if title_ != "0" else "output"

    df = pd.DataFrame(datas)
    df.to_excel(f"{title_}-{datetime.now().strftime("%d-%m-%Y")}.xlsx", index=False)

if __name__ == "__main__":
    #llm = HuggingFaceEndpoint(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1")
    folders = list_folders_in_data_subfolder()
    folder_input = int(input("with ID, what lecture you want to know : ")) - 1
# Example usage:
    directory_path = f"{os.getcwd()}/data/{folders[folder_input]}"
    output = list_and_read_vtt_files(directory_path)

    with open("output.txt", "w") as file:
        file.writelines(output)

    loader = TextLoader("output.txt")
    index = VectorstoreIndexCreator().from_loaders([loader])
    datas = []
    try:
        while True:
            prompt_ = input("Question : ")
            exit() if prompt_ == "-" else None
            if prompt_ == "0":
                break
            output = index.query(prompt_) #llm= llm)
            print(output)
            datas.append({"idea": prompt_, "answer": output})
    except HfHubHTTPError:
        print("502 Server Error, bad gateway, changing to save xlsx")
        save_xlsx()
        pass
    
    save_xlsx()

