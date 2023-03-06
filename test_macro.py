from urllib.error import HTTPError
from atlassian import Confluence
from datetime import datetime
from pytz import timezone
import os
import yaml
import logging
import json
import time
from requests import get

with open('confluence_macro_setting.yml') as f:
    info = yaml.load(f, Loader = yaml.FullLoader)

    # log 정보
    Log_Format = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(filename = "logfile.log",
                        filemode = "w",
                        format = Log_Format, 
                        level = logging.ERROR)
    logger = logging.getLogger()
    handler = logging.FileHandler('logfile.log')
    logger.addHandler(handler)

    # yaml 파일 정보
    HICONSY_URL = info['login']['url']
    HICONSY_ID = info['login']['id']
    HICONSY_PW = info['login']['password'] if info['login']['password'] else os.environ['HICONSY_CONFLUENCE_TOKEN']
    DAILY_PAGE_ID_LIST = info['daily']['page_id']

    # 컨플루언스 접속
    confluence = Confluence(
        url=HICONSY_URL,
        api_version='cloud',
        username=HICONSY_ID,
        password=HICONSY_PW)

    # 날짜 정보
    today = datetime.utcnow()
    ddmmyy = today.strftime("%d%m%y")
    hhmm = today.strftime("%H%M")
    
    start = datetime(today.year, today.month, today.day)
    seconds = str((today - start).seconds).zfill(6)
