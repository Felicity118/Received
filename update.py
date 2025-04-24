import sys
import os
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import firebase_admin
from firebase_admin import credentials,firestore
from basic_email import right_path
import json
import psutil

def check_version(db):
    try:
        with open(right_path("version.json"), "r") as file:
            data = json.load(file)
        current_version = float(data['version'])
    except:
        return 1,1,True
    versions = db.collection('versions').list_documents()
    version_names_one = [v for v in versions]
    version_names=[v.id for v in version_names_one]
    one=version_names_one[-1]
    two=one.get().to_dict()
    file_id=two['file_id']
    version_numbers = [float(name.split(' ')[1]) for name in version_names]
    if current_version>=max(version_numbers):
        return file_id,current_version,True
    else:
        return file_id,max(version_numbers),False



from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload



def upload_file(file_path, file_name):
    """Uploads a file to Google Drive with a custom chunk size"""
    file_metadata = {'name': file_name}


    media = MediaFileUpload(file_path, mimetype='application/octet-stream', chunksize=10 * 1024 * 1024, resumable=True)


    request = service_drive.files().create(body=file_metadata, media_body=media, fields='id')


    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f'File uploaded with ID: {response.get("id")}')
    return response.get('id')


import io
import sys
import os
from googleapiclient.http import MediaIoBaseDownload
scope = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive.file']
credentials_doc = ServiceAccountCredentials.from_json_keyfile_name(right_path('docKey.json'), scope)
service_drive = build('drive', 'v3', credentials=credentials_doc)

def download_file(file_id, destination_path):
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    request = service_drive.files().get_media(fileId=file_id)
    with io.FileIO(destination_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    print(f"File downloaded to: {destination_path}")
import time
import subprocess
def save_path(path,filename='path.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(path)
def get_path(filename='path.txt'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        os.remove(filename)
        return True,content
    else:
        return False,''
def kill_process_using_file(file_path):

    for proc in psutil.process_iter(['pid', 'name']):
        try:

            for file in proc.open_files():
                if file.path == file_path:
                    proc.terminate()
                    proc.wait()
                    print(f"Process {proc.name()} (PID {proc.pid}) terminated.")
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
def delete_old_version():
    bol,path=get_path()
    if bol:
        try:
            os.remove(path)
        except:
            kill_process_using_file(path)
            os.remove(path)

def update_version(version):
    with open(right_path("version.json"), "w") as file:
        json.dump({"version":version},file)
def run_updater(new_exe_path, current_exe_path,version):

    save_path(current_exe_path)
    update_version(version)
    subprocess.Popen([new_exe_path])

def install_new_version(new_file_name,version):
    new_exe = os.path.join(os.getcwd(), new_file_name)
    current_exe = sys.executable

    run_updater(new_exe, current_exe,version)
def download_update(file_id,version):
    new_file_name = f'Received {version}.exe'
    destination_path = os.path.join(os.getcwd(), new_file_name)
    download_file(file_id,destination_path)
    install_new_version(new_file_name,version)

