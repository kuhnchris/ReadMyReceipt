from django.db import models

class UploadFile(models.Model):
    image = models.ImageField(upload_to='upload')

    def __str__(self):
        return f'Upload/Image: {self.image.name} (pk: {self.pk})'

class OCRTask(models.Model):
    file = models.ForeignKey(to=UploadFile, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    inprogress = models.BooleanField(default=False)
    extended_resolve = models.BooleanField(default=False)
    simple_OCR = models.BooleanField(default=True)
    advanced_OCR = models.BooleanField(default=False)

    def __str__(self):
        taskStatus = ""
        if self.finished:
            taskStatus = "[DONE] "
        if self.inprogress:
            taskStatus = "[IN PROGRESS] "
        return f'{taskStatus}Task {self.pk} for {self.file}'

class OCRBox(models.Model):
    file = models.ForeignKey(to=UploadFile, on_delete=models.CASCADE)
    parentBox = models.ForeignKey(to='OCRBox', null=True, blank=True,  on_delete=models.CASCADE)
    task = models.ForeignKey(to='OCRTask', on_delete=models.CASCADE, null=True)

    startPointX = models.IntegerField()
    startPointY = models.IntegerField()
    endPointX = models.IntegerField()
    endPointY = models.IntegerField()
    content = models.TextField(blank=True)

    def __str__(self):
        return f'Box "{self.content}" (x: {self.startPointX}, y: {self.startPointY}->x: {self.endPointX}, y: {self.endPointY}) (task: {self.task}) (parent: {self.parentBox})'

