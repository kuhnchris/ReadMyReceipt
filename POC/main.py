from PIL import Image
import sys

import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
print("Will use lang '%s'" % (lang))

line_and_word_boxes = tool.image_to_string(
    Image.open('ReceiptSwiss.jpg'),
    builder=pyocr.builders.LineBoxBuilder()
)

# list of line objects. For each line object:
#   line.word_boxes is a list of word boxes (the individual words in the line)
#   line.content is the whole text of the line
#   line.position is the position of the whole line on the page (in pixels)
#
# Each word box object has an attribute 'confidence' giving the confidence
# score provided by the OCR tool. Confidence score depends entirely on
# the OCR tool. Only supported with Tesseract and Libtesseract (always 0
# with Cuneiform).
#
# Beware that some OCR tools (Tesseract for instance) may return boxes
# with an empty content.
for lawb in line_and_word_boxes:
    print(f'{lawb.word_boxes} {lawb.position} {lawb.content}')

if tool.can_detect_orientation():
    try:
        orientation = tool.detect_orientation(
            Image.open('ReceiptSwiss.jpg')
        )
    except pyocr.PyocrException as exc:
        print("Orientation detection failed: {}".format(exc))

    print("Orientation: {}".format(orientation))

