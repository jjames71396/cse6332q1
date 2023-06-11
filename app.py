import math
import pandas as pd
import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.identity import DefaultAzureCredential
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)



account_url = "https://asmt1.blob.core.windows.net"
default_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=default_credential)

container_name = "store"

# Create a local directory to hold blob data
local_path = "static/assignment1"
download_file_path = os.path.join(local_path, "people.csv")
container_client = blob_service_client.get_container_client(container= container_name) 
df = pd.read_csv(download_file_path)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/delete', methods=['POST'])
def delete():
    global df
    name = request.form.get('name')
    found = False
    idx = None
    for i,n in enumerate(df["Name"]):
        if n == name:
           idx = i
           found = True
    if found:
        df = df.drop(df.index[idx])
        return render_template('delete.html', name = name+" deleted")
    else:
        return render_template('delete.html', name = name+" not in db")
                  
@app.route('/update', methods=['POST'])
def update():
    inp = request.form.get('name')
    args = inp.split(',')
    download_file_path = None
    if len(args) < 8 or len(df.keys()) != len(args):
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    elif args[6][-4:] != ".jpg":
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    else:
        found = False
        for i,n in enumerate(df["Name"]):
            if n == args[0]:
               im = df["Picture"][i]
               df.loc[i] = args
               found = True
        if found:
            return render_template('update.html', name = args[0]+" updated")
        else:
            df.loc[len(df.index)] = args
            return render_template('update.html', name = args[0]+" added")

@app.route('/range', methods=['POST'])
def range():
    found = False
    arg = request.form.get('name')
    args = arg.split('-')
    container_name = "store"
    im = None
    download_file_path = None
    ims = []
    if args[0] not in df.keys():
       return redirect(url_for('index'))
    for i,n in enumerate(df[args[0]]):
        if type(n) is str and n[0] != '-' and n != ' ':
            print(n)
            if int(n) >= int(args[1]) and int(n) <= int(args[2]):
               im = df["Picture"][i]
               ims.append(im)
    imms = []
    for im in ims:
        if im is not None:
            download_file_path = os.path.join(local_path, im)
            container_client = blob_service_client.get_container_client(container= container_name) 
            blob_list = container_client.list_blobs()
            found = False
            for blob in blob_list:
                if im == blob.name:
                    found = True
            print(im)
            if found:
                with open(file=download_file_path, mode="wb") as download_file:
                    download_file.write(container_client.download_blob(im).readall())
                imms.append(download_file_path)
    
    
    return render_template('range.html', ims = imms)


@app.route('/hello', methods=['POST'])
def hello():
    found = False
    name = request.form.get('name')
    print(name)
    container_name = "store"
    im = None
    download_file_path = None
    v = None
    for i,n in enumerate(df["Name"]):
        if n == name:
           im = df["Picture"][i]
           v = df.loc[i]
    if im is not None:
        local_file_name = im
        # Create a blob client using the local file name as the name for the blob
        #blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
        
        download_file_path = os.path.join(local_path, local_file_name)
        container_client = blob_service_client.get_container_client(container= container_name) 
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            if local_file_name == blob.name:
                found = True
                break
        
        if found:
            with open(file=download_file_path, mode="wb") as download_file:
                download_file.write(container_client.download_blob(local_file_name).readall())
    
    if v is not None:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = v, fname=download_file_path)
    else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
