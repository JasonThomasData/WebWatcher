# WebWatcher
A web scraper for keeping an eye on websites. Some time ago I got sick of checking websites, since it's a pain and inefficient.

This script will:
- Take a CSV file with a list of websites.
- Scrape the markup for each and compare that to the previous markup for that site (savedFiles folder).
- Take a screenshot you can compare in the future, if you're not sure a site changed.
- If the markup is different, the script pushes this URL to a list of changed URLs.
- Saves the new markup.
- Emails you with a list of sites that have changed.
- Places all details in an html page for you to look at.

I've got my one running on a virtual private server.
It uses Cron - a scheduler for Linux distros - to run this job every two hours.

If you've also got a Linux-based VPS, and you've set up an SSH key with the server (you really should get a SSH key):
- Upload files with sftp.
- Logout, login with ssh to the server.
- Change the timezone on the host machine, via terminal ```sudo dpkg-reconfigure tzdata```
- Restart cron ```sudo service cron restart```
- Load crontab ```crontab -e```
- Cron has an explainer about how to format your jobs, follow that.

You'll notice all file locations in this script are referenced from the server's root folder.
You'll need to change the file locations when you call the _init_ function, to the same file path that Cron uses, where mine say ```/var/www/webWatcher/```

Hope this script saves you some sanity.

TO DO
- Add a function to get the string that wasn't there in the older html, and tell the user what that is, so users don't have to follow links.
- Add a function to push the results to an SQL database, and use Flask to create html templates from those results. So, users can choose to receive emails or check a website, or both.
