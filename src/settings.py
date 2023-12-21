from dotenv import load_dotenv
from os import getenv

load_dotenv()

BUCKET=getenv("BUCKET")
GOOGLE_APPLICATION_CREDENTIALS=getenv("GOOGLE_APPLICATION_CREDENTIALS")

BOT_NAME = 'src'

SPIDER_MODULES = ['src.spiders']
NEWSPIDER_MODULE = 'src.spiders'
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.25
CONCURRENT_REQUESTS_PER_DOMAIN = 32
COOKIES_ENABLED = True
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}
DOWNLOAD_HANDLERS = {
    'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'ftp': None,
    'file': None,
    's3': None
}
DOWNLOADER_MIDDLEWARES = {
  # 'scrapy_splash.SplashCookiesMiddleware': 720,
  # 'scrapy_splash.SplashMiddleware': 730,
  # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
  
  # Agent-user
  'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
  'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}
ITEM_PIPELINES = {
    'src.pipelines.PipelineDefault': 300,
}

AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 20
AUTOTHROTTLE_TARGET_CONCURRENCY = 20
#AUTOTHROTTLE_DEBUG = False

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# FEEDS = {
#     'data.json': {'format': 'json', 'overwrite': True}
#     # 'data.jsonl': {'format': 'jsonlines', 'overwrite': True}
# }