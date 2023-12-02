#!/bin/bash
#(crontab -l ; echo "* * * * * /home/ubuntu/upload-html.sh \"$template\" >> /var/log/cron.log") | crontab
#cron

# docker run -e spider="test" aw/scraping

cd /scrapy
eval "scrapy crawl $spider"