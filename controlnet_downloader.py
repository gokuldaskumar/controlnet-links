import os
import urllib.parse
import ipywidgets as widgets
from IPython.display import display
import requests
from tqdm.notebook import tqdm  # Import tqdm for progress bars

def download_models(models_data, checkbox_container, target_directory):
    for checkbox in tqdm(checkbox_container.children[1:], desc="Downloading Models"):  # Skip "Select All" & add progress bar
        if checkbox.value:
            model_name = checkbox.description
            model_files = models_data["sd15_models"].get(model_name) or models_data["xl_models"].get(model_name)
            for url in model_files:
                if isinstance(url, list):
                    url, filename = url
                else:
                    filename = urllib.parse.unquote(url.split('/')[-1])
                filepath = os.path.join(os.path.expanduser(target_directory), filename)
                
                if not os.path.isfile(filepath):
                    # Use requests for better download control
                    with requests.get(url, stream=True) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        with open(filepath, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f"Downloading {filename}", leave=False) as pbar:
                            for chunk in r.iter_content(chunk_size=8192): 
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    print(f"File {filename} already exists. Skipping download.")

def main():
    # Fetch the JSON file from the GitHub repository
    json_url = "https://raw.githubusercontent.com/gokuldaskumar/controlnet-links/main/controlnet_models.json"
    response = requests.get(json_url)
    models_data = response.json()

    sd15_models = models_data["sd15_models"]
    xl_models = models_data["xl_models"]

    # Create checkboxes for each model
    sd15_checkboxes = [widgets.Checkbox(value=False, description=key) for key in sd15_models.keys()]
    xl_checkboxes = [widgets.Checkbox(value=False, description=key) for key in xl_models.keys()]

    # "Select All" checkboxes
    select_all_sd15 = widgets.Checkbox(description="Select All SD15", value=False)
    select_all_xl = widgets.Checkbox(description="Select All XL", value=False)

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

    # Function to display checkboxes for selected model type
    checkbox_container = widgets.VBox(children=[])
    def display_checkboxes(model_type):
        if model_type == 'sd15':
            checkbox_container.children = [select_all_sd15] + sd15_checkboxes
        elif model_type == 'xl':
            checkbox_container.children = [select_all_xl] + xl_checkboxes

    # Create buttons for selecting model type
    sd15_button = widgets.Button(description="SD15 Models")
    xl_button = widgets.Button(description="XL Models")

    # Button click events
    sd15_button.on_click(lambda b: display_checkboxes('sd15'))
    xl_button.on_click(lambda b: display_checkboxes('xl'))

    # Display buttons
    buttons_container = widgets.HBox(children=[sd15_button, xl_button])
    display(buttons_container)

    # Initially empty container for checkboxes
    display(checkbox_container)

    # Function to download selected models
    def download_models_callback(b):
        target_directory = "~/stable-diffusion-webui/extensions/sd-webui-controlnet/models"
        download_models(models_data, checkbox_container, target_directory)

    # Create a button to start the download
    download_button = widgets.Button(description="Download Selected Models")
    download_button.on_click(download_models_callback)
    display(download_button)
