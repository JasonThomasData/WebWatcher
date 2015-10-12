#!/usr/bin/env python
import requests, re, csv, sys, smtplib
from bs4 import BeautifulSoup
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from datetime import datetime

initTime = datetime.now()

def send_email(parseToEmail, toAddr, fromAddr, fromPswd):
    #Send yourself the results. Need to setup an email account.
    msg = MIMEMultipart()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = 'Websites, update @ %s' %(str(initTime)[:16])  #Cut off the decimal places from the local time
    msg.attach(MIMEText(parseToEmail, 'plain'))
    server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
    server.starttls()
    server.login(fromAddr, fromPswd)
    text = msg.as_string()
    server.sendmail(fromAddr, toAddr, text)
    server.quit()
    return

def format_email_text(websiteNotFound, pagesChanged, couldNotFind, contentMissing):
    if len(pagesChanged) > 0:
        pagesChangedString = '\n'.join(pagesChanged)
    else:
        pagesChangedString = 'none'
    pagesChangedParse = 'These pages changed: \n%s\n' % (pagesChangedString)
    if len(websiteNotFound) > 0:    
        websiteNotFoundString = '\n'.join(websiteNotFound)
    else:
        websiteNotFoundString = 'none'
    websiteNotFoundParse = 'Could not be found online: \n%s\n' % (websiteNotFoundString)
    if len(contentMissing) > 0:
        contentMissingString = '\n'.join(contentMissing)
    else:
        contentMissingString = 'none'        
    contentMissingParse = 'Could not find content: \n%s\n' % (contentMissingString)
    if len(couldNotFind) > 0:
        couldNotFindString = '\n'.join(couldNotFind)
    else:
        couldNotFindString = 'none'    
    couldNotFindParse = 'Scraped and saved for the first time: \n%s\n' % (couldNotFindString)
    finTime = datetime.now()
    timeTaken = finTime - initTime
    timeString = 'The scraping took %s\n ~Started at %s and finished at %s' %(timeTaken, initTime, finTime)
    return '%s\n\n%s%s%s\n%s' % (pagesChangedParse, websiteNotFoundParse, contentMissingParse, couldNotFindParse, timeString)
    
def get_markup(row, websiteNotFound, contentMissing):
    #Scrapes the page. If no such page, or if page has no content, this pushes errors to arrays for email
    print row[0]
    try:
        #I recommend you enter your details here. If we want governments to be more open, than so should we be transparent.
        urlHeaders = {"User-Agent": "YOUR_NAME, YOUR_EMAIL, https://github.com/JasonThomasData/WebWatcher, ", "Referer": "YOUR_SITE_HERE"}
        r = requests.get(row[0], headers=urlHeaders, timeout=None)
    except IOError:
        websiteNotFound.append(row[0])
        print 'Site missing'
        return ''
    try:
        soup = BeautifulSoup(r.content, 'html5lib')
        if row[2] == 'null' and row[3] == 'null':
            findHtml = soup.find('body')
            findHtml = str(findHtml.findAll(text=True))
        else:
            findHtml = soup.find(row[1], {row[2] : row[3]})
            findHtml = str(findHtml.findAll(text=True))
        #return findHtml.encode('ascii')
        return re.sub('[\n\t\s\d\W]', '', findHtml)
    except AttributeError:
        contentMissing.append(row[0])
        print 'No content'
        return ''

def _init_(filePathForCron, fileWithURLs, toAddr, fromAddr, fromPswd):
    #Start looping through the CSV, comparing and saving markup
    pagesChanged = []
    websiteNotFound = []
    couldNotFind = []
    contentMissing =[]
    with open(filePathForCron + fileWithURLs, 'r') as csvFile:
        csvRead = csv.reader(csvFile, delimiter=',')
        for row in csvRead:
            externalHtml = get_markup(row, websiteNotFound, contentMissing)
            fileName = re.sub(r'[^\w]', '', row[0])
            fileName = fileName[:75] #Watch this, if you're scraping sites with the same URL, eg different q strings, you'll need to make this longer
            try:
                with open(filePathForCron + 'savedFiles/' + fileName + '.txt', 'r') as internalHtml:
                    if externalHtml != internalHtml.read():
                        pagesChanged.append(row[0])
            except IOError:
                couldNotFind.append(row[0])
            with open(filePathForCron + 'savedFiles/' + fileName + '.txt', 'w') as fileToSave:
                fileToSave.write(externalHtml)
    parseToEmail = format_email_text(websiteNotFound, pagesChanged, couldNotFind, contentMissing)
    send_email(parseToEmail, toAddr, fromAddr, fromPswd)

_init_('/path/to/scraper/', 'websitesToScrape.csv', 'RECIPIENT_EMAIL_ADDRESS', 'SENDER_EMAIL_ADDRESS', 'SENDER_EMAIL_PASSPHRASE')
sys.exit()