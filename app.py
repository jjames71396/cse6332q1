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
path = "static/assignment1"
download_file_path = os.path.join(path, "q1c.csv")
container_client = blob_service_client.get_container_client(container= container_name) 
blob_list = container_client.list_blobs()

found = False
for blob in blob_list:
    if path == blob.name:
        found = True
if found:
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(path).readall())
        
df = pd.read_csv(download_file_path)

download_file_path = os.path.join(path, "md.jpg")
container_client = blob_service_client.get_container_client(container= container_name) 
blob_list = container_client.list_blobs()
found = False
for blob in blob_list:
    if path == blob.name:
        found = True
if found:
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(path).readall())


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
    print(name)
    for i,n in enumerate(df["name"]):
        if n == name:
           idx = i
           found = True
    if found:
        df.loc[idx] = ['','','','','']
        return render_template('delete.html', name = name+" deleted")
    else:
        return render_template('delete.html', name = name+" not in db")
                  
@app.route('/update', methods=['POST'])
def update():
    inp = request.form.get('name')
    args = inp.split(',')
    download_file_path = None
    if len(args) < 5 or len(df.keys()) != len(args):
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    elif args[3][-4:] != ".jpg":
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    else:
        found = False
        for i,n in enumerate(df["name"]):
            if n == args[0]:
               if args[1] != '':
                args[1] = float(args[1])
               df.loc[i] = args
               found = True
        if found:
            return render_template('update.html', name = args[0]+" updated")
        else:
            if args[1] != '':
                args[1] = float(args[1])
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
    seat = "all"
    v = []
    if args[0].isalpha():
        seat = args[0]
        for i,n in enumerate(df["seat"]):
            if str(n) == seat:
                im = str(df["pic"][i])
                print(im)
                ims.append(im)
                for j in df.loc[i]:
                 v.append(j)
    else:
        if len(args) < 3:
            seat = "all"
        else:
            seat = args[2]
        for i,n in enumerate(df["row"]):
            if type(n) is not str:
                if float(n) >= float(args[0]) and float(n) <= float(args[1]):
                   if seat == "all" or seat == df["seat"][i]:
                       im = str(df["pic"][i])
                       print(im)
                       ims.append(im)
                       for j in df.loc[i]:
                        v.append(j)
    imms = []
    for im in ims:
        if im is not None:
            download_file_path = os.path.join(path, im)
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
    
    
    return render_template('range.html', ims = imms, v = v)


@app.route('/hello', methods=['POST'])
def hello():
    found = False
    name = request.form.get('name')
    print(name)
    container_name = "store"
    im = None
    download_file_path = None
    v = []
    ims = []
    for i,n in enumerate(df["row"]):
        if type(n) is not str and n >= 0:
            if n == float(name):
               im = df["pic"][i]
               ims.append(im)
               for j in df.loc[i]:
                v.append(j)
    imms = []
    for im in ims:
        if im is not None:
            download_file_path = os.path.join(path, im)
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
    
    if v is not None:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = v, ims=imms)
    else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
