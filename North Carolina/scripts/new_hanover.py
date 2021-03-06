from bs4 import BeautifulSoup
import requests
import os 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

def getFilePath(path):
    fileDir = os.path.dirname(__file__)
    filePath = os.path.join(fileDir, path)
    filePath = os.path.abspath(os.path.realpath(filePath))
    return filePath

def scraping(url):
    print("Scraping from " + url)
    f.write("\n\n\n")
    f.write("Scraping from " + url + "\n\n\n") 
    driver.get(url)
    time.sleep(1)
    result = driver.execute_script("return document.documentElement.outerHTML")
    return BeautifulSoup(result, 'html.parser')

def getPDF(file_url, county):
    title = file_url.split('/').pop()
    fileName = title 
    filePath = getFilePath("../data/" + county + "-PDF")
    r = requests.get(file_url, stream = True)
    with open(os.path.join(filePath,fileName), "wb") as pdf:
        for chunk in r.iter_content(chunk_size=1024):
         if chunk:
             pdf.write(chunk)
    return "data/" + title
    
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)

COUNTY = "new_hanover"

'''
#create PDF folder for PDF files
try:
    filePath = getFilePath("../data/" + COUNTY + "-PDF")
    os.mkdir(filePath) 
except:
    print('PDF folder already exists!')
'''
textFilePath = '../data/' + COUNTY + '.txt'
f = open(getFilePath(textFilePath), 'w')


#Scrape all news updates from main website
url = 'https://health.nhcgov.com/your-environment/public-health/coronavirus/nhc-coronavirus-news/'
soup = scraping(url)
sections = soup.select('.panel-body')

for section in sections:
    data = section.find_all('li')
    for item in data:
        f.write(item.find('a').get_text() + '\n')
        currSoup = scraping(item.find('a').get('href'))
        f.write(currSoup.select('#main')[0].get_text())


#Scrape county-level Covid resources
links = [
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/screening-testing/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/stay-at-home-order-faqs/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/reducerisk/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/symptoms/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/resources-assistance/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/business-resources/',
    'https://health.nhcgov.com/your-environment/public-health/coronavirus/county-operations/'
]

for link in links:
    soup = scraping(link)
    f.write(soup.select('#main')[0].get_text())

f.close()
