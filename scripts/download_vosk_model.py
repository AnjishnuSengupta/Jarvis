import os
import urllib.request
import zipfile

def download_vosk_model():
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_name = "vosk-model-small-en-us-0.15"
    model_path = os.path.join(model_dir, model_name)
    
    if os.path.exists(model_path):
        print(f"Vosk model already exists at {model_path}")
        return
        
    url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
    zip_path = os.path.join(model_dir, f"{model_name}.zip")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    print(f"Downloading Vosk model from {url}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        print("Download complete. Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)
        print("Extraction complete.")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == "__main__":
    download_vosk_model()
