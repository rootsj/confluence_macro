import os
from datetime import datetime
from pytz import timezone
import hiconsy_daily
import hiconsy_weekly
from github_utils import get_github_repo, upload_github_issue

if __name__ == '__main__':
    hiconsy_daily.daily_macro()
    hiconsy_weekly.weekly_macro()

    seoul_timezone = timezone('Asia/Seoul')
    today = datetime.now(seoul_timezone)
    today_date = today.strftime("%Y년 %m월 %d일")

    issue_title = f"({today_date}) ERROR LOG"

    with open("logfile.log", "r") as file:
        str_list = file.readlines()
        upload_contents = "".join(str_list)

    access_token = os.environ['HICONSY_GITHUB_TOKEN']
    repository_name = "confluence_macro"

    if upload_contents != "":
        repo = get_github_repo(access_token, repository_name)
        upload_github_issue(repo, issue_title, upload_contents)
