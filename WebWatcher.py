#!/usr/bin/python

import re, csv, sys, smtplib, time, os, requests, httplib
from bs4 import BeautifulSoup
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from datetime import datetime
from contextlib import closing
from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
vdisplay = Xvfb()
vdisplay.start() #This is the function that begins the X server. It is required to run Spynner, which is a headless web browser.

def format_web_page(filePathForCron, resultsForWebDisplay, initTime):
    previousTime = ''
    with open(filePathForCron + 'previousTime.txt', 'r+') as previousTxt:
        previousTime = previousTxt.read()
        previousTxt.seek(0)
        previousTxt.truncate()
        previousTxt.write(str(initTime))
    pageHTML = []
    pageHTML.append('<html><head>')
    pageHTML.append('<link rel="stylesheet" href="style.css">')    
    pageHTML.append('</head><body>')
    previousScrapeString = '<h3>Previous scrape - %s' % (str(previousTime)[:16])
    thisScrapeString = '<h3>This scrape - %s' % (str(initTime)[:16])    
    pageHTML.append(previousScrapeString)
    pageHTML.append(thisScrapeString)
    pageHTML.append('<h3>Results</h3>')
    pageHTML.append('<p>The <span class="changed">highlighted rows</span> are sites that have changed this time.</p>')
    pageHTML.append('<p>The picture links on the <b>Screenshot</b> column, where available, show what the page looked like when it was saved the <b>previous time</b>.</p>')
    pageHTML.append('<table>')
    pageHTML.append('<tr><th>Site</th><th>Status</th><th>Screenshot</th></tr>')
    for result in resultsForWebDisplay:
        linkString = '<a href="%s" target="_blank">%s</a>' % (result[0], result[0])
        if result[len(result)-2] != 'none':
            picString = '<a href="%s" target="_blank">pic</a>' % (result[len(result)-2])
        else:
            picString = result[len(result)-2]
        td1 = '<td>%s</td>' % (linkString)
        td2 = '<td>%s</td>' % (result[len(result)-1])
        td3 = '<td>%s</td>' % (picString)
        if result[len(result)-1] == 'changed':
            tr = '<tr class="changed">%s%s%s</tr>' % (td1,td2,td3)
        else:
            tr = '<tr>%s%s%s</tr>' % (td1,td2,td3)
        pageHTML.append(tr)
    pageHTML.append('<script></script>')
    pageHTML.append('</table></body></html>')
    pageHTML = ''.join(str(x) for x in pageHTML)
    #Below, look for the file path entered in the init function, and use the filepath accordingly
    with open(filePathForCron + 'index.html', 'w') as htmlFile:
        htmlFile.write(pageHTML)

def send_email(parseToEmail, peopleToEmail, fromAddr, fromPswd, initTime):
    #Below, if you want emails about every scrape that occurs
    #peopleToEmail.append('jason.thomas@sbs.com.au')
    print 'peopleToEmail', peopleToEmail
    for toAddr in peopleToEmail:
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

def format_email_text(websiteNotFound, pagesChanged, couldNotFind, contentMissing, urlsSkipped, sitesInList, initTime, duplicates):
    if len(pagesChanged) > 0:
        pagesChangedString = '%s\n%s' %('\n'.join(pagesChanged),len(pagesChanged))
    else:
        pagesChangedString = '%s' % (len(pagesChanged))
    pagesChangedParse = 'These pages changed: \n%s\n' % (pagesChangedString)

    websiteString = '<b>Go to %s' %('http://188.166.250.243/WebWatcher/ for a greater summary</b>')

    if len(websiteNotFound) > 0:    
        websiteNotFoundString = '%s\n%s' %('\n'.join(websiteNotFound),len(websiteNotFound))
    else:
        websiteNotFoundString = '%s' % (len(websiteNotFound))
    websiteNotFoundParse = 'Could not be found online/ request timed out: \n%s\n' % (websiteNotFoundString)

    if len(contentMissing) > 0:
        contentMissingString = '%s\n%s' %('\n'.join(contentMissing),len(contentMissing))
    else:
        contentMissingString = '%s' % (len(contentMissing))
    contentMissingParse = 'Could not find content: \n%s\n' % (contentMissingString)

    if len(couldNotFind) > 0:
        couldNotFindString = '%s\n%s' %('\n'.join(couldNotFind),len(couldNotFind))
    else:
        couldNotFindString = '%s' % (len(couldNotFind))
    couldNotFindParse = 'Scraped and saved for the first time: \n%s\n' % (couldNotFindString)

    otherString = '%s sites on list, %s skipped by instruction, %s duplicate urls also skipped \n' % (len(sitesInList), urlsSkipped, duplicates)
    finTime = datetime.now()
    timeTaken = finTime - initTime
    timeString = 'In total, took %s\n ~ Started at %s and finished at %s' %(timeTaken, initTime, finTime)
    print 'timeString', timeString
    return '%s\n\n%s\n\n%s%s%s\n%s%s' % (pagesChangedParse, websiteString, websiteNotFoundParse, contentMissingParse, couldNotFindParse, otherString, timeString)

def PhantomJS_getshot_markup(filePathForCron, row, fileName):
    try:
        driver = webdriver.PhantomJS()
        driver.set_window_size(2024, 3000)
        driver.set_page_load_timeout(30)
        driver.get(row[0])
        time.sleep(float(row[7]))
        newPhotoPath = '%s%s%s' % ('images/', fileName, 'new.png')
        oldPhotoPath = '%s%s%s' % ('images/', fileName, 'old.png')    
        if os.path.exists(filePathForCron + newPhotoPath):
            os.rename(filePathForCron + newPhotoPath, filePathForCron + oldPhotoPath)
        driver.save_screenshot(filePathForCron + newPhotoPath)
        driver.quit()
        print 'screenshot success'
        #Returns old photo, since you don't want to look at the new one - the new one is the same as the webpage.
        return oldPhotoPath
    except httplib.BadStatusLine:
        print '^ BadStatusLine (PhantomJS), screenshot fail'
        return 'none'
    except TimeoutException:
        print '^ Timed out, screenshot fail'
        return 'none'
    except WebDriverException:
        print '^ Typeerror, screenshot fail'
        return 'none'

def get_markup(row, fileName, websiteNotFound, contentMissing):
    
    def requests_get_markup(row, fileName):
        urlHeaders = {"User-Agent": "Jason Thomas, journalist, SBS News, https://github.com/JasonThomasData/WebWatcher, jason.thomas(at)sbs.com.au", "Referer": "www.sbs.com.au/news"}
        r = requests.get(row[0], headers=urlHeaders, timeout=30)
        return r.content

    #Scrapes the page. If no such page, pushes that to an array
    print row[0]
    try:
        scrapedHtml = requests_get_markup(row, fileName)
        print 'request success'
    except IOError:
        websiteNotFound.append(row[0]) #Integrate this into the above function
        print '^ Site missing'
        return ''
    except AttributeError:
        websiteNotFound.append(row[0])
        print '^ Site missing'
        return ''

    #If page has no content, this pushes errors to an array for recording
    try:
        soup = BeautifulSoup(scrapedHtml, 'lxml')
        if row[3] == 'null' and row[4] == 'null':
            findHtml = soup.find('body')
        else:
            findHtml = soup.find(row[2], {row[3] : row[4]})
        findHtml = str(findHtml.findAll(text=True))
        return re.sub('[\n\t]', '', findHtml)
    except AttributeError:
        contentMissing.append(row[0])
        print '^ No content'
        return ''

def _init_(filePathForCron, fileWithURLs, fromAddr, fromPswd):
    initTime = datetime.now()
    sitesInList = [] #Sites that have been processed
    duplicates = 0
    urlsSkipped = 0 #The CSV file will declare if a URL is to be skipped in row[5]
    pagesChanged = []
    resultsForWebDisplay = []
    websiteNotFound = [] #Or site timed out
    couldNotFind = [] #Could not find file in savedFiles
    contentMissing = [] #Could not find the element in the scraped markup          
    peopleToEmail = []
    
    def add_email_to_list(emails):
        emailList = emails.split(',')
        for email in emailList:
            if email not in peopleToEmail:
                peopleToEmail.append(email)

    def compare_save_html(row, fileName, externalHtml):
        #Take screeshot, if instructed 
        photoPath = 'none'
        if row[8] == 'screenshot':
            photoPath = PhantomJS_getshot_markup(filePathForCron, row, fileName)        
        row.append(photoPath)

        #Compare file with site
        try:
            with open(filePathForCron + 'savedFiles/' + fileName + '.txt', 'r') as internalHtml:
                if externalHtml != internalHtml.read():
                    pagesChanged.append(row[0]) #This gets sent to the email function
                    compareResult = 'changed'
                    add_email_to_list(row[1])
                else:
                    compareResult = 'unchanged'
                row.append(compareResult)
                resultsForWebDisplay.append(row) #Passed to the format_web_page() function   
        except IOError:
            couldNotFind.append(row[0])
        with open(filePathForCron + 'savedFiles/' + fileName + '.txt', 'w') as fileToSave:
            fileToSave.write(externalHtml)

    #Start looping through the CSV, calling functions to compare and save markup
    with open(filePathForCron + fileWithURLs, 'r') as csvFile:
        csvRead = csv.reader(csvFile, delimiter=',')
        for row in csvRead:
            if row[0] not in sitesInList:  #Filters out duplicates
                sitesInList.append(row[0])
                if row[5] != 'skip': #Sites where the CSV contains an instruction to skip
                    fileName = re.sub(r'[^\w]', '', row[0])
                    fileName = fileName[:243] #THe maximum file length in Ubuntu is 255, so this is playing safe, including .txt, so this is safe by two characters
                    externalHtml = get_markup(row, fileName, websiteNotFound, contentMissing)
                    time.sleep(1) #Important for several requests from the same server, so you don't make their server slower (IP address could get blacklisted.
                    if row[0] not in websiteNotFound and row[0] not in contentMissing:
                        compare_save_html(row, fileName, externalHtml)
                    else:
                        print '^ File compare and save not attempted'
                else:
                    urlsSkipped += 1
            else:
                duplicates += 1
    parseToEmail = format_email_text(websiteNotFound, pagesChanged, couldNotFind, contentMissing, urlsSkipped, sitesInList, initTime, duplicates)
    send_email(parseToEmail, peopleToEmail, fromAddr, fromPswd, initTime)
    format_web_page(filePathForCron, resultsForWebDisplay, initTime)

vdisplay.stop()

_init_('/var/www/html/WebWatcher/', 'websitesToScrape.csv', 'YOUR EMAIL HERE', 'YOUR EMAIL PASSWORD')
#/var/www/html/WebWatcher/ - first param, path to folder required to run with cron
#For testing, replace the first param with ''

print 'Task finished at %s' %(datetime.now())
sys.exit()