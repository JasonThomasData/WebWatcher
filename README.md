# WebWatcher
A web scraper for keeping an eye on websites. Some time ago I got sick of checking websites, since it's a pain and inefficient.

This script will:
- Take a CSV file with a list of websites.
- Scrape the markup for each and compare that to the previous markup for that site (savedFiles folder).
- If the markup is different, the script pushes this URL to a list of changed URLs.
- Saves the new markup.
- Emails you with a list of sites that have changed.

This is obviously a time saver, and valuable if you work in news.
I suggest people should not overdo this - don't go crazy and scrape a site every 5 minutes.
I've got my one running on a virtual private server.
It uses Cron - a scheduler for Linux distros - to run this job every two hours.

If you've also got a Linux-based VPS, and you've set up an SSH key with the server (you really should get a SSH key):
- Upload the files to your directory using sftp, for me, ```sftp userName@serverIpAddress```
- Log into the server using ssh, for me this is ```ssh userName@serverIpAddress```
- Change the timezone on the host machine, via terminal ```dpkg-reconfigure tzdata```
- Restart cron ```sudo service cron restart```
- Load crontab ```crontab -e```
- Cron has an explainer about how to format your jobs, follow that.

You'll notice all file locations in this script are referennced from the server's root folder.
You'll need to change the file locations inside the python script, to the same file path that Cron uses, where mine say ```/home/userName/python/webWatcher/```

Hope this script saves you some sanity.

TO DO
- Fix the bug that says some websites couldn't scrape, then saves them. I'm catching an error in the wrong spot.
- Add a function to push the results to an SQL database, and use Flask to create html templates from those results. So, lists of people can choose to receive emails or check a website, or both.
