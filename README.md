# ReadMyReceipt
 
###### *(...or Receipe, since I'm a derp and can't write english good.)*
```¯\_(ツ)_/¯```

## Install / Usage / Start
```bash
pip install -e < requirements.txt
rmr/manage.py runserver
```
Then open your browser and go to http://localhost:8000

## Endpoints
- ```/``` - DropZone.JS Image Upload Zone
- ```/overlay/<id>``` - overlay OCR results
- ```/admin``` - Django Admin Interface

## Job(s)
To create OCR readings from the image(s) you need OCRTask(s). 
If you upload a file via dropzone.js you automatically get a OCR Task for this image.
To execute the task run the following command:
```bash
rmr/manage.py doOCR
```

After you receive the message ```Done!``` you can check the ```/overlay/id``` page.

