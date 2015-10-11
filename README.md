# WebWatcher
A web scraper for keeping an eye on websites. Some time ago I got sick of checking websites, since it's a pain and inefficient.

This script will:
- Take a CSV file with a list of websites.
- Scrape the markup for each and compare that to the previous markup for that site (savedFiles folder).
- If the markup is different, the script pushes this URL to a list of changed URLs.
- Saves the new markup.
- Emails you with a list of sites that have changed.

This is obviously a time saver, and valuable if you work in news.
I suggest people should not overdo this - don't go crazy and scrape a site every 5 minutes please.
I've got my one running on a virtual private server.
It uses Cron - a scheduler for Linux distros - to run this job every two hours.

If you've also got a Linux-based VPS, and you've set up an SSH key with the server (you really should get a SSH key):
- Upload files with sftp.
- Logout, login with ssh to the server.
- Change the timezone on the host machine, via terminal ```dpkg-reconfigure tzdata```
- Restart cron ```sudo service cron restart```
- Load crontab ```crontab -e```
- Cron has an explainer about how to format your jobs, follow that.

You'll notice all file locations in this script are referenced from the server's root folder.
You'll need to change the file locations when you call the _init_ function, to the same file path that Cron uses, where mine say ```/home/userName/python/webWatcher/```

Your CSV takes:
- Every row as a website to scrape.
- Every row has four cells.
- The first cell is the URL of the site to scrape.
- The second cell is the kind of element to look for, eg, div or ul.
- The third cell is the element identifier to look for, eg, the ID or the class. 
- The fourth is the name of the element's class or ID.
- Be careful not to have spaces in the columns if they aren't intended to be there, or BeautifulSoup can't find the element.
- If you just want to scrape the whole page, enter null in the second and third cells for each row. Then the scraper will look for the html's body.

Hope this script saves you some sanity.

TO DO
- Add a virtual env to emulate javascript for dynamic pages
- Add a function to get the string that wasn't there in the older html, and tell the user what that is, so users don't have to follow links.
- Add a function to push the results to an SQL database, and use Flask to create html templates from those results. So, users can choose to receive emails or check a website, or both.