import shutil
from django.shortcuts import redirect, render
from .models import ImageFile
from .forms import ImageForm
from django.contrib import messages

import os
import glob
import cv2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import platform
from tempfile import TemporaryDirectory
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\sai05\AppData\Local\Tesseract-OCR\tesseract.exe'
path_to_poppler_exe = r'C:\Program Files\poppler-0.68.0\bin'
Image.MAX_IMAGE_PIXELS = 1000000000


def home(request):
    return render(request, 'home.html')


def upload(request):
    if request.method == "POST":
        messages.success(
            request, 'File Uploaded Successfully')
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return render(request, "upload.html", {'form': form})
    else:
        form = ImageForm()
        return render(request, "upload.html", {'form': form})


def search(request):
    if request.method == "POST":
        searchKeyword = request.POST['keyword']
        fileResultfound = []
        fileResultNotfound = []
        file_path = os.getcwd() + "/media/Files/*"

        for file in glob.glob(file_path, recursive=True):
            if file.split('\\')[-1].find('.pdf') < 0 and file.split('\\')[-1].find('.txt') < 0:
                result = pytesseract.image_to_string(
                    cv2.imread(file), lang='eng')
                if len(searchKeyword) > 1:
                    resultfilename = file.split('\\')[-1]
                    if searchKeyword.lower() in result:
                        fileResultfound.append(
                            f'{searchKeyword}  is in file name : {resultfilename}')
                        print(f'200 Found  - {fileResultfound}  - {result}')
                    else:
                        fileResultNotfound.append(
                            f'{searchKeyword} is not in the {resultfilename}')
                        print(
                            f'404 Not found  - {fileResultNotfound} - {result}')

            elif file.split('\\')[-1].find('.pdf') > 0:
                path = Path(os.getcwd() + "\\media\\Files\\" +
                            file.split('\\')[-1].split('.')[0]+'.txt')
                if path.is_file():
                    print(f'file already processed {path}')
                    with open(path) as f:
                        text = f.read()
                    if len(searchKeyword) > 1:
                        resultfilename = file.split('\\')[-1]
                        if searchKeyword.lower() in text:
                            fileResultfound.append(
                                f'{searchKeyword}  is in file name : {resultfilename}')
                            print(f'200 Found  - {fileResultfound} - {text}')
                        else:
                            fileResultNotfound.append(
                                f'{searchKeyword} is not in the {resultfilename}')
                            print(
                                f'404 Not found  - {fileResultNotfound} - {text}')
                else:
                    print(f'file not processed {path}')
                    img_path = Path(os.getcwd() + "\\media\\Files\\")
                    image_list = []
                    result = ''
                    text_file = Path(os.getcwd() + "\\media\\Files\\"+file.split('\\')
                                     [-1].split('.')[0]+'.txt')
                    file_pages = convert_from_path(
                        file, 500, poppler_path=path_to_poppler_exe)
                    for page_enum, page in enumerate(file_pages, start=1):
                        filename = f'{img_path}\page_{page_enum:03}.jpg'
                        page.save(filename, 'JPEG')
                        image_list.append(filename)

                    with open(text_file, 'a') as output_file:
                        for image_file in image_list:
                            text = pytesseract.image_to_string(
                                cv2.imread(image_file), lang='eng')
                            text = text.replace('-\n', "")
                            result += text
                            output_file.write(text.lower())
                    removeprocessedimgpath = os.getcwd()+"\media\Files"
                    for fname in os.listdir(removeprocessedimgpath):
                        if fname.startswith('page_'):
                            os.remove(os.path.join(
                                removeprocessedimgpath, fname))
                    if len(searchKeyword) > 1:
                        resultfilename = file.split('\\')[-1]
                        if searchKeyword.lower() in result.lower():
                            fileResultfound.append(
                                f'{searchKeyword}  is in file name : {resultfilename}')
                            print(f'200 Found  - {fileResultfound}- {result}')
                        else:
                            fileResultNotfound.append(
                                f'{searchKeyword} is not in the {resultfilename}')
                            print(
                                f'404 Not found  - {fileResultNotfound}- {result}')

        return render(request, "search.html", {'fileResultfound': fileResultfound, 'fileResultNotfound': fileResultNotfound})
    else:
        return render(request, "search.html")


def clearUploads(request):
    path = os.getcwd() + "\\media\\Files\\"
    de = ImageFile.objects.all().delete()
    if de[0] > 0:
        shutil.rmtree(path)
        print(path, 'cleared', de[0])
    messages.success(
        request, 'Previously Uploaded files are Cleared in the DataBase, Please Upload New Files to Process')
    return redirect("upload")
