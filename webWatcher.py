#!/usr/bin/env python

#Bug in the first function to run. It catches an error when there's nothing wrong with 

import requests
import re
import csv
import sys
import smtplib
from bs4 import BeautifulSoup
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from datetime import datetime

initTime = datetime.now()

def send_email(parseToEmail, toAddr):
    #Send yourself the results. Need to setup an email account.
    fromAddr = 'YOUR_SENDER_ADDRESS_HERE'
    msg = MIMEMultipart()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = 'Websites, update @ %s' %(initTime)
    msg.attach(MIMEText(parseToEmail, 'plain'))
    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server.starttls()
    server.login(fromAddr, 'YOUR_SENDER_PASSWORD_HERE')
    text = msg.as_string()
    server.sendmail(fromAddr, toAddr, text)
    server.quit()

def format_email_text(websiteNotFound, pagesChanged, couldNotFind, toAddr):
    pagesChangedString = '\n'.join(pagesChanged)
    pagesChangedParse = 'These pages changed: \n%s\n' % (pagesChangedString)
    websiteNotFoundString = '\n'.join(websiteNotFound)
    websiteNotFoundParse = 'These pages could not be found online: \n%s\n' % (websiteNotFoundString)
    couldNotFindString = '\n'.join(couldNotFind)
    couldNotFindParse = 'These websites were scraped and saved for the first time: \n%s\n' % (couldNotFindString)
    finTime = datetime.now()
    timeTaken = finTime - initTime
    timeString = 'The scraping took %s\n ~Started at %s and finished at %s' %(timeTaken, initTime, finTime)
    parseToEmail = '%s\n%s\n%s\n%s' % (pagesChangedParse, websiteNotFoundParse, couldNotFindParse, timeString)
    send_email(parseToEmail, toAddr)

def scrape_page(fileWithURLs, toAddr):
    #Get the markup from sites and save them to the saved files directory
    pagesChanged = []
    websiteNotFound = []
    couldNotFind = []
    #This file is referenced from the root folder, because that's the path that Cron uses to find files.
    with open('/home/userName/python/webWatcher/' + fileWithURLs, 'r') as csvFile:
        csvRead = csv.reader(csvFile, delimiter=',')
        for row in csvRead:
            try:
                r = requests.get(row[0])
                print row[0]
                soup = BeautifulSoup(r.content, 'html5lib')
                externalHtml = soup.get_text()
                if row[1] == 'null' and row[2] == 'null':
                    externalHtml = str(soup.find('body'))
                else:
                    externalHtml = str(soup.find('div', {row[1] : row[2]}))
                externalHtml = re.sub('[\n\t\s\d\W]', '', externalHtml)
                fileName = re.sub(r'[^\w]', '', row[0])        
                try:
                    with open('/home/userName/python/webWatcher/savedFiles/' + fileName + '.txt', 'r') as internalHtml:
                        if externalHtml != internalHtml.read():
                            pagesChanged.append(row[0])
                except IOError:
                    couldNotFind.append(row[0])
                with open('/home/userName/python/webWatcher/savedFiles/' + fileName + '.txt', 'w') as fileToSave:
                    fileToSave.write(externalHtml)
            except IOError:
                websiteNotFound.append(row[0])
    format_email_text(websiteNotFound, pagesChanged, couldNotFind, toAddr)

scrape_page('websitesToScrape.csv', 'ENTER_RECIPIENT_PASSWORD_HERE')
sys.exit()