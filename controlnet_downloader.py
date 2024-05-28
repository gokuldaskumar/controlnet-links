import os
import urllib.parse
import requests

def download_models(selected_models, target_directory):
    for model_name, model_files in selected_models.items():
        for url in model_files:
            if isinstance(url, list):
                url, filename = url
            else:
                filename = urllib.parse.unquote(url.split('/')[-1])  # Decode the filename
            filepath = os.path.join(os.path.expanduser(target_directory), filename)
            
            # Check if the file already exists
            if not os.path.isfile(filepath):
                # If the file does not exist, download it with the desired filename
                os.system(f"wget {url} -O {filepath}")
            else:
                print(f"File {filename} already exists. Skipping download.")

def main():
    # Fetch the JSON file from the GitHub repository
    json_url = "https://raw.githubusercontent.com/gokuldaskumar/controlnet-links/main/controlnet_models.json"
    response = requests.get(json_url)
    models_data = response.json()

    sd15_models = models_data["sd15_models"]
    xl_models = models_data["xl_models"]

    # Prompt the user to select the model type
    model_type = input("Enter the model type (sd15 or xl): ")

    if model_type == 'sd15':
        selected_models = sd15_models
    elif model_type == 'xl':
        selected_models = xl_models
    else:
        print("Invalid model type.")
        return

    # Prompt the user to enter the target directory
    target_directory = input("Enter the target directory: ")

    download_models(selected_models, target_directory)

if __name__ == "__main__":
    main()
