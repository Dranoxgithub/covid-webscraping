import csv
import os
import pdfplumber
import nltk
from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_path 


threshold = 0.3 # for english word percentage from pdf, if less then try ocr
english_words = set(nltk.corpus.words.words())
initial_date = "2020-07-17"
end_date = "2020-07-21"

'''
Read a PDF using OCR.
Returns text and english success rate.
'''
def ocrReadPDF(path):
    head, tail = os.path.split(path)
    if not os.path.isdir(head + "/img"):
        os.mkdir(head + "/img") # make image directory

    pages = convert_from_path(path, 500)
    image_counter = 1
    for page in pages: # convert each page to jpg
        fileName = head + "/img/" + tail[:-4] + "_page_" + str(image_counter) + ".jpg" 
        page.save(fileName, 'JPEG') 
        image_counter += 1

    ret_text = ""
    english_count = 0
    total_words = 0
    for i in range(1, image_counter):
        fileName = head + "/img/" + tail[:-4] + "_page_" + str(i) + ".jpg"
        text = str(pytesseract.image_to_string(Image.open(fileName)))
        if text:
            text = text.replace('-\n', '')
            ret_text += text
            words = text.split(' ')
            total_words += len(words)
            for word in words:
                if word in english_words:
                    english_count += 1
    
    if total_words == 0:
        total_words = 1
    success_rate = english_count / total_words
    return ret_text, success_rate    

'''
Read a PDF normally.
Returns text and english success rate.
'''
def readPDF(path):
    english_count = 0

    ret_text = ""
    total_words = 0

    with pdfplumber.open(path) as f:
        for page in f.pages:
            text = page.extract_text()
            if text:
                ret_text += text
                words = page.extract_words()
                total_words += len(words)
                for word in words:
                    if word['text'] in english_words:
                        english_count += 1
        
    if total_words == 0:
        total_words = 1
    success_rate = english_count / total_words
    return ret_text, success_rate


def writePDFtext(path, state):
    print("scraping text from new PDF", path)
    try:
        text, rate = readPDF(path)
    except:
        print("failed to read PDF")
    else:
        print("successfully reading PDF")
        if rate < threshold:
            try:
                ocrText, ocrRate = ocrReadPDF(path)
            except:
                print("failed to OCR read PDF")
            else:
                if ocrRate > rate:
                    text = ocrText
                    rate = ocrRate

        head, _ = os.path.split(path)
        write_destination = head + "/pdf_diff_" + initial_date + ".txt"

        _, full_county = os.path.split(head)
        county = full_county[:-4]
        
        text = ' '.join(text.split())
        #text = text.replace('\n \n', '^^').replace('\n', '').replace('^^', '\n\n')
        
        with open(write_destination, "a") as f:
            f.write(text)

        #lines = text.split('\n\n')
        
        with open('pdf_diff_data.csv', 'a', newline='') as csvfile:
            fieldnames = ['category', 'diff_line', 'county', 'state']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for sentence in nltk.tokenize.sent_tokenize(text):
                writer.writerow({'diff_line' : sentence, 'county' : county, 'state' : state})
            
'''
Writes the PDF text data for all new PDFs for a given county (initial_path and end_path are paths to county-PDF directories)
'''
def writeNewCountyPDFs(initial_path, end_path, state):
    initial_files = os.listdir(initial_path)
    with open(end_path + "/pdf_diff_" + initial_date + ".txt", "w") as f: # clear .txt file (in case this is run multiple times, don't want duplicates, since we append otherwise)
        f.write("")
    f.close()
    for file_name in os.listdir(end_path):
        if file_name not in initial_files and file_name[-4:] == '.pdf': # new (diff) PDF data
            writePDFtext(end_path + "/" + file_name, state)
            
with open('pdf_diff_data.csv', 'w', newline='') as csvfile: # clear file
    fieldnames = ['category', 'diff_line', 'county', 'state']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

states = ['Washington', 'North Carolina', 'Louisiana', 'Massachusetts', 'Iowa', 'Michigan', 'Colorado']


# assumes that PDF directories are same within each date

for state in states:
    initial_path = state + "/data/" + initial_date + "/" 
    end_path = state + "/data/" + end_date + "/" 

    if not os.path.isdir(initial_path):
        print("no path for " + state + " for " + initial_date)
        continue

    if not os.path.isdir(end_path):
        print("no path for " + state + " for " + end_date)
        continue

    for directory in os.listdir(initial_path):
        if directory[-4:] == '-PDF':
            writeNewCountyPDFs(initial_path + directory, end_path + directory, state)
