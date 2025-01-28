import customtkinter as ctk
from PIL import Image
from pathlib import Path
import subprocess
import os
import requests
import zipfile
import json
current_dir = Path(__file__).parent
installed_versions = os.listdir(f'{current_dir}/PyCraft/Versions')
GITHUB_API_URL = "https://api.github.com/repos/mabindy/PyCraft/releases/latest"

def get_local_version(json_file_path):
    try:
        # Read the installed version from the JSON file
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as json_file:
                version_data = json.load(json_file)
                return version_data.get("local_version", "Unknown")
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error reading version file: {e}")
        return "Unknown"

LOCAL_VERSION = get_local_version(f"{current_dir}/PyCraft/launcher/localversion.json")

def check_for_updates():
    try:
        LOCAL_VERSION = get_local_version(f"{current_dir}/PyCraft/launcher/localversion.json")
        update_check_button.configure(text="...")
        # Fetch latest tags info from GitHub
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        release_info = response.json()  # This is a list of tags
        # Ensure the response is not empty
        if not release_info:
            print("No releases found on GitHub.")
            return

        # Extract the latest version from the first tag
        latest_version = release_info["tag_name"]  # The "name" key contains the version tag
        assets = release_info.get("assets", [])
        download_url = assets[0]["browser_download_url"]

        # Compare versions
        if latest_version > LOCAL_VERSION:
            update_message = f"New version available: {latest_version}\nLatest installed version: {LOCAL_VERSION}"
            update_check_button.configure(text="Update Found")
            download_release(download_url, latest_version)
            print(update_message)
        else:
            print("You are already up to date!")
            update_check_button.configure(text="Up to Date!")
            root.after(3000, reset_update_checker)
    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: {e}")
    except (KeyError, IndexError) as e:
        print(f"Error processing release info: {e}")

def update_version_file(version):
    try:
        version_data = {"local_version": version}

        with open(f"{current_dir}/PyCraft/launcher/localversion.json", "w") as json_file:
            json.dump(version_data, json_file, indent=4)

        print(f"Updated version file")
    except Exception as e:
        print(f"Error updating version file: {e}")

def download_release(download_url, version):
    try:
        print("Downloading new release...")
        update_check_button.configure(text=f"Installing {version}")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()


        output_file = f"{current_dir}/PyCraft/Versions/PyCraft_{version}.zip"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        update_check_button.configure(text=f"Install complete!")
        root.after(3000, reset_update_checker)
        print(f"Download complete! File saved to: {output_file}")
        update_version_file(version)
        extract_to = f"{current_dir}/PyCraft/Versions"
        unzip_file(output_file, extract_to)
        installed_versions = os.listdir(f'{current_dir}/PyCraft/Versions')
        version_dropdown.configure(values=sorted([ver for ver in installed_versions]))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading release: {e}")

def unzip_file(zip_path, extract_to):
    try:
        os.makedirs(extract_to, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        os.remove(zip_path)
    except zipfile.BadZipFile as e:
        print("Bad Zip")
    except Exception as e:
        print(f"Error unzipping file: {e}")

def reset_update_checker():
    update_check_button.configure(text=f"Check For Updates")
def launch_game():
    try:
        subprocess.Popen(['python', f'{current_dir}/PyCraft/Versions/{version_dropdown.get()}/pycraft.py'])
        root.quit()
    except Exception as e:
        ctk.CTkMessagebox(title="Error", message=f"Could not launch PyCraft: {e}")

def show_settings():
    settings_window = ctk.CTkToplevel()
    settings_window.title("Settings")
    settings_window.geometry("300x200")

    resolution_label = ctk.CTkLabel(settings_window, text="Resolution:")
    resolution_label.pack(pady=10)

    resolution_option = ctk.CTkOptionMenu(settings_window, values=["1920x1080", "1280x720", "800x600"])
    resolution_option.pack(pady=10)

    save_button = ctk.CTkButton(settings_window, text="Save", command=lambda: save_settings(resolution_option.get()))
    save_button.pack(pady=20)

def save_settings(resolution):
    print(f"Resolution set to: {resolution}")

def open_versions_folder():
    try:
        if not os.path.exists(f'{current_dir}/PyCraft/Versions'):
            print("Versions folder does not exist.")
            return

        os.startfile(f'{current_dir}/PyCraft/Versions')
    except Exception as e:
        print(f"Error opening versions folder: {e}")

# Main launcher window
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

root = ctk.CTk()
root.title("PyCraft Launcher")
root.geometry("800x500")
root.minsize(800,500)
root.maxsize(800,500)



title_label = ctk.CTkLabel(root, text="PyCraft Launcher", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=20)

game_image = ctk.CTkImage(Image.open(f"{current_dir}/PyCraft/launcher/launcherimage.png"), size=(600,350))
bg_image = ctk.CTkLabel(root, image=game_image, text="")
bg_image.place(relx=0.125, rely=0.15)
version_dropdown_values = sorted([ver for ver in installed_versions], reverse=True)
version_dropdown = ctk.CTkOptionMenu(root, values=version_dropdown_values)
version_dropdown.place(x=50, y=450)
if version_dropdown_values == []:
    version_dropdown.set("No Installed Versions")
play_button = ctk.CTkButton(root, text="Play", font=ctk.CTkFont(size=18), command=launch_game, fg_color="#24ab26", hover_color="#1b801c")
play_button.place(x=325, y=450)
settings_gear = ctk.CTkImage(Image.open(f"{current_dir}/PyCraft/launcher/settingsgear.png"), size=(20,20))
file_icon = ctk.CTkImage(Image.open(f"{current_dir}/PyCraft/launcher/fileicon.png"), size=(20,20))
settings_button = ctk.CTkButton(root, text="", image=settings_gear, font=ctk.CTkFont(size=18), width=20, height=25, command=show_settings, fg_color="#6b6b6b", hover_color="#4d4d4d")
settings_button.place(x=10, y=10)
file_button = ctk.CTkButton(root, text="", image=file_icon, font=ctk.CTkFont(size=18), width=15, height=25, command=open_versions_folder, fg_color="#6b6b6b", hover_color="#4d4d4d")
file_button.place(x=10, y=450)
update_check_button = ctk.CTkButton(root, text="Check For Updates",  font=ctk.CTkFont(size=18), width=170, command=check_for_updates, fg_color="#6b6b6b", hover_color="#4d4d4d")
update_check_button.place(x=625, y=10)

quit_button = ctk.CTkButton(root, text="Quit", font=ctk.CTkFont(size=18), command=root.quit)
quit_button.place(x=600, y=450)

version_label = ctk.CTkLabel(root, text="Created by Mabindy", font=ctk.CTkFont(size=12))
version_label.place(x=340, y=480)

root.mainloop()
