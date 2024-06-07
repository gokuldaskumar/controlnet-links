# controlnet_models_downloader.py
import os
import urllib.parse
import ipywidgets as widgets
from IPython.display import display
import requests
from tqdm import tqdm

# Fetch the JSON file from the GitHub repository
json_url = "https://raw.githubusercontent.com/gokuldaskumar/controlnet-links/main/controlnet_models.json"
response = requests.get(json_url)
models_data = response.json()

sd15_models = models_data["sd15_models"]
xl_models = models_data["xl_models"]
ic_light_models = models_data["ic_light_models"]

# Create checkboxes for each model
sd15_checkboxes = [widgets.Checkbox(value=False, description=key) for key in sd15_models.keys()]
xl_checkboxes = [widgets.Checkbox(value=False, description=key) for key in xl_models.keys()]
ic_light_checkboxes = [widgets.Checkbox(value=False, description=key) for key in ic_light_models.keys()]

# "Select All" checkboxes
select_all_sd15 = widgets.Checkbox(description="Select All SD15", value=False)
select_all_xl = widgets.Checkbox(description="Select All XL", value=False)
select_all_ic_light = widgets.Checkbox(description="Select All IC Light", value=False)

# Function to update the selection state of all checkboxes based on "Select All" state
def update_selection(checkboxes, select_all_checkbox):
    for cb in checkboxes:
        cb.value = select_all_checkbox.value

# Attach the update_selection function to the "Select All" checkboxes
def attach_select_all(select_all_checkbox, checkboxes):
    def on_select_all_change(change):
        update_selection(checkboxes, select_all_checkbox)
    select_all_checkbox.observe(on_select_all_change, names='value')

attach_select_all(select_all_sd15, sd15_checkboxes)
attach_select_all(select_all_xl, xl_checkboxes)
attach_select_all(select_all_ic_light, ic_light_checkboxes)

# Function to display checkboxes for selected model type
checkbox_container = widgets.VBox(children=[])
def display_checkboxes(model_type):
    if model_type == 'sd15':
        checkbox_container.children = [select_all_sd15] + sd15_checkboxes
    elif model_type == 'xl':
        checkbox_container.children = [select_all_xl] + xl_checkboxes
    elif model_type == 'ic_light':
        checkbox_container.children = [select_all_ic_light] + ic_light_checkboxes

# Create buttons for selecting model type
sd15_button = widgets.Button(description="SD15 Models")
xl_button = widgets.Button(description="XL Models")
ic_light_button = widgets.Button(description="IC Light Models")

# Button click events
sd15_button.on_click(lambda b: display_checkboxes('sd15'))
xl_button.on_click(lambda b: display_checkboxes('xl'))
ic_light_button.on_click(lambda b: display_checkboxes('ic_light'))

# Display buttons
buttons_container = widgets.HBox(children=[sd15_button, xl_button, ic_light_button])
display(buttons_container)

# Initially empty container for checkboxes
display(checkbox_container)

# Function to download a file with progress bar
def download_file(url, filepath):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    chunk_size = 8192
    with open(filepath, 'wb') as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc=os.path.basename(filepath),
        initial=0,
        miniters=1
    ) as pbar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(len(chunk))

# Function to download selected models
def download_models(b):
    primary_directory = os.path.expanduser("~/stable-diffusion-webui-forge/models/ControlNet")
    secondary_directory = os.path.expanduser("~/stable-diffusion-webui/extensions/sd-webui-controlnet/models")
    unet_primary_directory = os.path.expanduser("~/stable-diffusion-webui-forge/models/ic-light")
    unet_secondary_directory = os.path.expanduser("~/stable-diffusion-webui/models/ic-light")

    # Check for primary directory first
    if os.path.isdir(primary_directory):
        target_directory = primary_directory
    else:
        target_directory = secondary_directory

    # Check for primary unet directory first
    if os.path.isdir(unet_primary_directory):
        unet_target_directory = unet_primary_directory
    else:
        unet_target_directory = unet_secondary_directory

    os.makedirs(target_directory, exist_ok=True)
    os.makedirs(unet_target_directory, exist_ok=True)
    downloaded_files = []

    for checkbox in checkbox_container.children[1:]:  # Skip the "Select All" checkbox
        if checkbox.value:  # If the checkbox is checked
            model_name = checkbox.description
            model_files = sd15_models.get(model_name) or xl_models.get(model_name) or ic_light_models.get(model_name)
            for url in model_files:
                if isinstance(url, list):
                    url, filename = url
                else:
                    filename = urllib.parse.unquote(url.split('/')[-1])  # Decode the filename
                filepath = os.path.join(target_directory if model_name not in ic_light_models else unet_target_directory, filename)
                
                # Check if the file already exists
                if not os.path.isfile(filepath):
                    print(f"Downloading {filename} into {target_directory if model_name not in ic_light_models else unet_target_directory}...")
                    download_file(url, filepath)
                    downloaded_files.append(filename)
                else:
                    print(f"File {filename} already exists in {target_directory if model_name not in ic_light_models else unet_target_directory}. Skipping download.")

    if downloaded_files:
        print(f"\nDownload Complete. Models downloaded: {', '.join(downloaded_files)}")
    else:
        print("\nNo new models were downloaded.")

# Create a button to start the download
download_button = widgets.Button(description="Download Selected Models")
download_button.on_click(download_models)
display(download_button)
