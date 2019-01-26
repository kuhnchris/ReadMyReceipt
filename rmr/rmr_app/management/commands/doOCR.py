import sys
import pyocr
import pyocr.builders

from PIL import Image
from django.core.management.base import BaseCommand, CommandError
from rmr_app.models import UploadFile, OCRBox, OCRTask

class Command(BaseCommand):
    help = 'Executes an OCR job on the oldest database entry'

    def prepareOCR(self):
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        # The tools are returned in the recommended order of usage
        self.tool = tools[0]
        print("Will use tool '%s'" % (self.tool.get_name()))
        # Ex: Will use tool 'libtesseract'

        langs = self.tool.get_available_languages()
        print("Available languages: %s" % ", ".join(langs))
        self.lang = langs[0]
        # print("Will use lang '%s'" % (self.lang))

    def parseBox(self, sourceFile, MyBox, ParentBox, entry):
        print(f'found box - {MyBox.content}')
        boxObj = OCRBox.objects.create(file=sourceFile,
                                       task=entry,
                                       parentBox=ParentBox,
                                       startPointX = MyBox.position[0][0],
                                       startPointY=MyBox.position[0][1],
                                       endPointX=MyBox.position[1][0],
                                       endPointY=MyBox.position[1][1],
                                       content=MyBox.content
                                      )

        if hasattr(MyBox,'word_boxes'):
            for box in MyBox.word_boxes:
                self.parseBox(sourceFile, box, boxObj, entry)


    def handle(self, *args, **options):
        entry = OCRTask.objects.filter(finished=False,inprogress=False).first()
        if not entry:
            return "no entries to process"

        print("found pending task, set to inProgress...")
        entry.inprogress = True
        entry.save()

        print("preparing OCR tool")
        self.prepareOCR()
        if not self.tool:
            return "error preparing OCR tool"

        print("OCRing...")
        line_and_word_boxes = self.tool.image_to_string(
            Image.open(entry.file.image.path),
            builder=pyocr.builders.LineBoxBuilder(),
            lang='deu'
        )

        print("parsing and writing to database...")
        for box in line_and_word_boxes:
            self.parseBox(entry.file,box,None, entry)

        print("finishing task.")
        entry.inprogress = False
        entry.finished = True
        entry.save()

        return "Done!"