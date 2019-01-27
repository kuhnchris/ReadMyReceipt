import sys
import pyocr
import pyocr.builders

import rmr_app.utils as util
from PIL import Image
from django.core.management.base import BaseCommand, CommandError
from rmr_app.models import UploadFile, OCRBox, OCRTask

class Command(BaseCommand):
    help = 'Executes an OCR job on the oldest database entry'

    def parseBox(self, sourceFile, MyBox, ParentBox, entry):
        print(f'found box @ {MyBox.position} content: {MyBox.content}')
        if MyBox.content == "":
            print(f'ignore empty box.')
            return

        boxObj = OCRBox.objects.create(file=sourceFile,
                                       task=entry,
                                       parentBox=ParentBox,
                                       startPointX = MyBox.position[0][0],
                                       startPointY=MyBox.position[0][1],
                                       endPointX=MyBox.position[1][0],
                                       endPointY=MyBox.position[1][1],
                                       content=MyBox.content
                                      )

        if hasattr(MyBox,'word_boxes') and entry.extended_resolve is True:
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
        self.tool, self.lang = util.prepareOCR()
        if not self.tool:
            return "error preparing OCR tool"

        if entry.advanced_OCR:
            print("(advanced) OCRing...")
            line_and_word_boxes = util.cleanAndParseImage(self.tool, entry.file.image.path)
        else:
            print("(simple) OCRing...")
            line_and_word_boxes = util.simpleOCR(self.tool,entry)


        print("parsing and writing to database...")
        for box in line_and_word_boxes:
            self.parseBox(entry.file,box,None, entry)

        print("finishing task.")
        entry.inprogress = False
        entry.finished = True
        entry.save()

        return "Done!"