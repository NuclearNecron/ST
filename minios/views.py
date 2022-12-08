from django.shortcuts import render, redirect
from minios.models import Document, MyDocument
from minios.forms import DocumentForm, MyDocumentForm
from minio import Minio
import os
import time
import glob
import django.conf as conf
import pytz
import datetime
import pyautogui as pag
from django.http import JsonResponse
from pytz import timezone
from Imagecontainer.settings import MEDIA_ROOT
from django.http import HttpResponse

GlobalData = {
    'last_date': 0
}
GD=0


def global_data_update(request):
    global GD
    body=str(request.body)
    body=(body.replace(' ', ''))[2:-1]
    rawdate=int(body)
    print( datetime.datetime.fromtimestamp(rawdate / 1e3))
    GD=rawdate
    print(GD)

    return JsonResponse({})


def download(request, file_name):
  file_path = MEDIA_ROOT + '/' + file_name
  response = HttpResponse(open(file_path, 'rb').read())
  response['X-Sendfile'] = file_path
  response['Content-Length'] = os.stat(file_path).st_size
  response['Content-Disposition'] = 'attachment; filename='+file_name
  response['Content-Type'] = 'image/*'

  return response

def home(request):
    return render(request, 'home.html')


def store(request):
    clean_static()
    if request.method == 'POST':
        request.session['access'] = request.POST['access']
        request.session['secret'] = request.POST['secret']
    access = request.session.get('access')
    secret = request.session.get('secret')
    conf.settings.AWS_STORAGE_BUCKET_NAME = access
    client = Minio(endpoint="localhost:9000", access_key=access, secret_key=secret, secure=False)

    objects = client.list_objects(access)

    return render(request, 'store.html', {'objects': objects})


def object(request, name):
    access = request.session.get('access')
    secret = request.session.get('secret')
    client = Minio(endpoint="localhost:9000", access_key=access, secret_key=secret, secure=False)

    filepath = "minios/static/image/" + name
    getobject = client.fget_object(access, name, filepath)

    object_info = client.stat_object(access, name)

    if request.method == 'POST':
        client.remove_object(access, name)
        return redirect('deleted')

    return render(request, 'object.html', {'object_name': name, 'object_info': object_info, 'client': client, 'access': access, 'object': getobject})


def delete(request, file_name):
    access = request.session.get('access')
    secret = request.session.get('secret')
    client = Minio(endpoint="localhost:9000", access_key=access, secret_key=secret, secure=False)

    if request.method == 'POST':
        client.remove_object(access, file_name)
        pag.alert(text="Файл был удален", title="Результат", button="Ок")
    return redirect('store')


def model_form_upload(request):
    clean_static()
    form = MyDocumentForm()
    if request.method == 'POST':
        global GD
        form = MyDocumentForm(request.POST, request.FILES)
        access = request.session.get('access')
        secret = request.session.get('secret')
        if (request.FILES):
            print(request.FILES['fileList'])
            newdoc = MyDocument(doc=request.FILES['fileList'])
            newdoc.save()
            for filename, file in request.FILES.items():
                name = request.FILES[filename].name
            request.session['filename'] = name

            client = Minio(endpoint="localhost:9000", access_key=access, secret_key=secret, secure=False)
            filepath = "minios/static/image/" + name
            try:
                object_info = client.stat_object(access, name)
                print(object_info)
                utc = pytz.UTC
                last_date_modified = object_info.last_modified
                print(last_date_modified)
                last_date_modified = last_date_modified + datetime.timedelta(hours=3, minutes=0, seconds=0)
                new_date_modified = utc.localize(datetime.datetime.fromtimestamp(GD / 1e3))
                print(last_date_modified)
                print(new_date_modified)
                if (last_date_modified < new_date_modified):
                    client.fput_object(access, name, filepath)
                    pag.alert(text="Файл был заменен", title="Результат", button="Ок")
                else:
                    pag.alert(text="Файл устарел, хранилище не было обновлено", title="Результат", button="Ок")
                return redirect('store')
            except:
                client.fput_object(access, name, filepath)
                pag.alert(text="Файл был загружен", title="Результат", button="Ок")

            return redirect('store')
    return render(request, 'model_form_upload.html', {'form': form},)

def clean_static():
    files = glob.glob('minios/static/image/*')
    for f in files:
        os.remove(f)
    return


def model_form_edit(request, file_name):
    clean_static()
    if request.method == 'POST':
        global GD
        form = MyDocumentForm(request.POST, request.FILES)
        access = request.session.get('access')
        secret = request.session.get('secret')
        if(request.FILES):
            print(request.FILES['fileList'])
            newdoc = MyDocument(doc=request.FILES['fileList'])
            newdoc.save()
            for filename, file in request.FILES.items():
                name = request.FILES[filename].name
            request.session['filename'] = name

            client = Minio(endpoint="localhost:9000", access_key=access, secret_key=secret, secure=False)
            filepath = "minios/static/image/" + name
            object_info = client.stat_object(access, file_name)
            utc = pytz.UTC
            last_date_modified=object_info.last_modified
            print(last_date_modified)
            last_date_modified = last_date_modified+datetime.timedelta(hours=3, minutes=0, seconds=0)
            new_date_modified= utc.localize(datetime.datetime.fromtimestamp(GD/ 1e3))
            print(last_date_modified)
            print(new_date_modified)
            if(last_date_modified<new_date_modified):
                client.fput_object(access, file_name, filepath)
                pag.alert(text="Файл был заменён", title="Результат", button="Ок")
            else:
                pag.alert(text="Файл устарел, хранилище не было обновлено", title="Результат", button="Ок")
            return redirect('store')

    return render(request, 'model_form_edit.html', {'form': form, 'name': file_name}, )
