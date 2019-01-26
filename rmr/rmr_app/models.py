from django.db import models

class UploadFile(models.Model):
    image = models.ImageField(upload_to='upload')

class OCRTask(models.Model):
    file = models.ForeignKey(to=UploadFile, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    inprogress = models.BooleanField(default=False)

class OCRBox(models.Model):
    file = models.ForeignKey(to=UploadFile, on_delete=models.CASCADE)
    parentBox = models.ForeignKey(to='OCRBox', null=True, blank=True,  on_delete=models.CASCADE)
    task = models.ForeignKey(to='OCRTask', on_delete=models.CASCADE, null=True)

    startPointX = models.IntegerField()
    startPointY = models.IntegerField()
    endPointX = models.IntegerField()
    endPointY = models.IntegerField()
    content = models.TextField(blank=True)

