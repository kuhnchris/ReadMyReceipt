from django.contrib import admin
from .models import UploadFile, OCRBox, OCRTask
# Register your models here.
admin.site.register(OCRBox)
admin.site.register(OCRTask)
admin.site.register(UploadFile)
