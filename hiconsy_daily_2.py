import imp
from urllib.error import HTTPError
from atlassian import Confluence
from datetime import datetime
from pytz import timezone
import os
import yaml
import logging
import time
from requests import get
import json


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

        url = "spaces/flyingpdf/pdfpageexport.action?pageId={pageId}".format(pageId=daily_page_id)
        download_url = None

        try:
            long_running_task = True
            headers = confluence.form_token_headers
            response = confluence.get(url, headers=headers, not_json_response=True)
            response_string = response.decode(encoding="utf-8", errors="strict")
            task_id = response_string.split('name="ajs-taskId" content="')[1].split('">')[0]
            poll_url = "/services/api/v1/task/{0}/progress".format(task_id)
            while long_running_task:
                long_running_task_response = confluence.get(poll_url, headers=headers, not_json_response=True)

                long_running_task_response_parts = json.loads(long_running_task_response.decode(
                    encoding="utf-8", errors="strict"
                ))

                percentage_complete = long_running_task_response_parts["progress"]
                is_update_final = long_running_task_response_parts["progress"] == 100
                current_state = long_running_task_response_parts["state"]

                time.sleep(5)
                
                if is_update_final and current_state == "UPLOADED_TO_S3":
                    download_url = long_running_task_response_parts["result"][6:]
                    long_running_task = False
                elif not is_update_final and current_state == "FAILED":
                    logger.error("PDF conversion not successful.")
                    break
                else:
                    print(long_running_task_response_parts)

        except IndexError as e:
            logger.error(e)


        if ( download_url != None):
            s3_url = confluence.get(download_url, headers=headers, not_jsonresponse=True)

            with open(file_name, "wb") as file:   
                response = get(s3_url)
                try:
                    file.write(response.content) 
                    confluence.attach_file('./' + str(daily_page_id) + '/' + file_name, page_id=daily_page_id, comment="uploaded by macro")
                except HTTPError as e:
                    logger.error(e)