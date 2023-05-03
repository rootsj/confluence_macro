from urllib.error import HTTPError
from atlassian import Confluence
from datetime import datetime, timezone
from pytz import timezone
import os
import yaml
import logging


def monthly_macro():
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
    MONTHLY_LIST = info['monthly']

    # 컨플루언스 접속
    confluence = Confluence(
        url=HICONSY_URL,
        api_version='cloud',
        username=HICONSY_ID,
        password=HICONSY_PW)

    # 날짜 정보
    utc_now = datetime.now(timezone.utc)
    today = utc_now.date()
    ddmmyy = utc_now.strftime("%d%m%y")
    hhmm = utc_now.strftime("%H%M")
    # 월화수목금토일 구분값
    weekday = utc_now.weekday()

    # 몇번째 요일
    weekday_of_first = datetime.date(today.year, today.month, 1).weekday()
    current_weekday = (today.day - 1 + weekday_of_first) % 7

    for monthly in MONTHLY_LIST:
        if weekday in monthly['weekday'] and current_weekday == monthly['weeks']:

            # 파일 이름
            page_space = confluence.get_page_space(monthly['page_id'])
            file_name = page_space + '-' + str(monthly['page_id']) + '-' + ddmmyy + '-' + hhmm + '.pdf'

            # 폴더 여부
            try:
                if not os.path.exists(str(monthly['page_id'])):
                    os.makedirs(str(monthly['page_id']))
            except OSError:
                logger.error(e + "Error: Failed to create the directory.")
            

            # pdf다운 및 업로드 실행
            with open("./" +str(monthly['page_id']) + "/" + file_name, "wb") as pdf_file:
                try:
                    # pdf 파일 생성
                    pdf_file.write(confluence.get_page_as_pdf(str(monthly['page_id'])))
                    confluence.attach_file('./' + str(monthly['page_id']) + '/' + file_name, page_id=monthly['page_id'], comment="uploaded by macro")
                except HTTPError as e:
                    logger.error(e)
                except OSError as e:
                    logger.error(e)