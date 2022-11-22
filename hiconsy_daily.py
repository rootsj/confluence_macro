from urllib.error import HTTPError
from atlassian import Confluence
from datetime import datetime
from pytz import timezone
import os
import yaml
import logging


def daily_macro():
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


    for daily_page_id in DAILY_PAGE_ID_LIST:
        # 파일 이름
        page_space = confluence.get_page_space(daily_page_id)
        page_title = confluence.get_page_by_id(daily_page_id).get('title')
        file_name = page_space + '-' + page_title + '-' + ddmmyy + '-' + seconds + '.pdf'

        # 폴더 여부
        try:
            if not os.path.exists(str(daily_page_id)):
                os.makedirs(str(daily_page_id))
        except OSError:
            logger.error(e + "Error: Failed to create the directory.")

        with open("./" +str(daily_page_id) + "/" + file_name, "wb") as pdf_file:
            try:
                # pdf 파일 생성
                pdf_file.write(confluence.get_page_as_pdf(str(daily_page_id)))
                confluence.attach_file('./' + str(daily_page_id) + '/' + file_name, page_id=daily_page_id, comment="uploaded by macro")
            except HTTPError as e:
                logger.error(e)
            except OSError as e :
                logger.error(e)