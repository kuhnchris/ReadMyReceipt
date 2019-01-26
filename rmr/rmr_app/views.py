from django.shortcuts import render
from django.http.response import JsonResponse, Http404
#import json
from .models import UploadFile, OCRBox, OCRTask

def enter_view(request):
    return render(request, "rmr_app/enter.html")

def images_view(request):
    x = { 'images': UploadFile.objects.all() }
    return render(request,"rmr_app/images.html")

def upload_view(request):
    x = {}
    x['POST'] = request.POST
    x['postField'] = request.POST.get('file', None)
    x['FILES'] = request.FILES['file'].size
    iFile = request.FILES['file']
    ufile = UploadFile.objects.create(image=iFile)
    OCRTask.objects.create(file=ufile)
    return JsonResponse(x)

def show_image_overlay(request, id):
    if not id:
        raise Http404()

    imgobj = UploadFile.objects.filter(pk=id).first()
    if not imgobj:
        raise Http404()

    boxes = OCRBox.objects.filter(file=imgobj,parentBox__isnull=False).all()
    print(boxes)

    return render(request,'rmr_app/overlay.html', {'boxes': boxes, 'imgobj': imgobj})
