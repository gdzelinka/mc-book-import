from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os
from pynput.mouse import Button, Controller
import pyperclip
import keyboard
import time
import json
import argparse

LINE_LENGTH = 114
LINES_PER_PAGE = 14

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def write_page(page: str, mouse):
    pyperclip.copy(page)
    mouse.position = (730, 349)
    mouse.press(Button.left)
    mouse.release(Button.left)
    time.sleep(.25)
    keyboard.send("ctrl+v")
    time.sleep(.25)
    mouse.position = (873, 554)
    mouse.press(Button.left)
    mouse.release(Button.left)

def txt_to_book(text: str, mouse):
    with open(os.path.join(os.getcwd(),'char_length.json'), 'r') as f:
        char_table = json.load(f)
    end_of_book = len(text)
    current_position = 0

    current_page = ''
    current_page_length = 0
    current_line = ''
    current_line_length = 0
    current_word = ''
    current_word_length = 0

    for character in text:
        if character != " ":
            current_word += character
            if character in char_table:
                current_word_length+= char_table[character]
            else:
                current_word_length += 6
            current_position += 1
        else:
            #character is a space
            current_word += character
            current_word_length += char_table[character]
            current_position += 1

            if current_word_length + current_line_length > LINE_LENGTH:
                current_page += current_line
                current_page_length += 1
                current_line = current_word
                current_line_length = current_word_length
                current_word = ''
                current_word_length = 0
            else:
                current_line += current_word
                current_line_length += current_word_length
                current_word = ''
                current_word_length = 0

            if current_page_length == LINES_PER_PAGE:
                write_page(current_page, mouse)
                current_page = ''
                current_page_length = 0

    current_page += current_line
    current_page += current_word
    write_page(current_page, mouse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import book into minecraft")
    parser.add_argument('--path', type= str, help= 'path to the pdf or txt file to import')

    args = parser.parse_args()

    book = args.path
    mouse = Controller()
    if book.endswith('.pdf'):
        text = convert_pdf_to_txt(book)
        with open('bookpdf.txt', 'w', encoding='utf8') as f:
            f.write(text)
    
    elif book.endswith('.txt'):
        with open(book, 'r', encoding='utf8') as f:
            text = f.read()
    else:
        raise Exception("Book is neither a pdf nor a txt file")

    text = text.replace('\n', ' ')
    text = text.replace('  ', ' ')
    mouse.position = (730, 349)
    mouse.press(Button.left)
    mouse.release(Button.left)
    txt_to_book(text, mouse)
