from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time, os, argparse, json
import naver_paper_clien as clien
import naver_paper_damoang as damoang
import naver_paper_ppomppu as ppomppu

def grep_campaign_links():
    campaign_links = []
    campaign_links += clien.find_naver_campaign_links()
    campaign_links += damoang.find_naver_campaign_links()
    campaign_links += ppomppu.find_naver_campaign_links()

    if(campaign_links == []):
        print("모든 링크를 방문했습니다.")
        exit()

    return campaign_links

def main(campaign_links, id, pwd, headness = True):

    # 크롬 드라이버 옵션 설정
    chrome_options = webdriver.ChromeOptions()
    if(headness):
        chrome_options.add_argument('headless') # headless mode

    # 새로운 창 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://naver.com')

    # 현재 열려 있는 창 가져오기
    current_window_handle = driver.current_window_handle

    # <a href class='MyView-module__link_login___HpHMW'> 일때 해당 링크 클릭
    driver.find_element(By.XPATH, "//a[@class='MyView-module__link_login___HpHMW']").click()

    # 새롭게 생성된 탭의 핸들을 찾습니다
    # 만일 새로운 탭이 없을경우 기존 탭을 사용합니다.
    new_window_handle = None
    for handle in driver.window_handles:
        if handle != current_window_handle:
            new_window_handle = handle
            break
        else:
            new_window_handle = handle

    # 새로운 탭을 driver2로 지정합니다
    driver.switch_to.window(new_window_handle)
    driver2 = driver

    username = driver2.find_element(By.NAME, 'id')
    pw = driver2.find_element(By.NAME, 'pw')

    # GitHub Action을 사용하지 않을 경우, 아래와 같이 변경 해주어야 합니다.
    input_id = id
    input_pw = pwd

    # ID input 클릭
    username.click()
    # js를 사용해서 붙여넣기 발동 <- 왜 일부러 이러냐면 pypyautogui랑 pyperclip를 사용해서 복붙 기능을 했는데 운영체제때문에 안되서 이렇게 한거다.
    driver2.execute_script("arguments[0].value = arguments[1]", username, input_id)
    time.sleep(1)

    pw.click()
    driver2.execute_script("arguments[0].value = arguments[1]", pw, input_pw)
    time.sleep(1)

    #입력을 완료하면 로그인 버튼 클릭
    driver2.find_element(By.CLASS_NAME, "btn_login").click()
    time.sleep(1)

    # new.save 등록
    # new.dontsave 등록 안함
    try:
        driver2.find_element(By.ID, "new.dontsave").click()
        time.sleep(1)
    except:
        pass

    try_login_limit = os.getenv("TRY_LOGIN", 3)
    try_login_count = 1
    while True:
        page_title = driver2.title
        if(page_title == "NAVER"):
            break
        if(try_login_count > try_login_limit):
            exit()
        print(f"로그인 되지 않음 #{try_login_count}")
        print(f"페이지 타이틀 : {page_title}")
        time.sleep(1)
        try_login_count += 1

    for link in campaign_links:
        print(link) # for debugging
        try:
            # Send a request to the base URL
            driver2.get(link)
            result = driver2.switch_to.alert
            print(result.text)
            result.accept()
        except:
            print("알럿창 없음")
            time.sleep(3)
            # pageSource = driver2.page_source
            # print(pageSource)
        time.sleep(1)


if __name__ == "__main__":
    # for debug
    headness = True
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', type=str, required=False, help="naver id")
    parser.add_argument('-p', '--pw', type=str, required=False, help="naver password")
    parser.add_argument('-c', '--cd', type=str, required=False, help="credential json")
    args = parser.parse_args()
    if args.id is None and args.pw is None and args.cd is None:
        id = os.getenv("USERNAME", "ID is NULL")
        pw = os.getenv("PASSWORD", "PASSWORD is NULL")
        campaign_links = grep_campaign_links()
        main(campaign_links, id, pw, headness)
    elif(args.cd is not None):
        try:
            json_obj = json.loads(args.cd)
        except:
            print('use -i or --cd argument')
            print('credential json sample [{"id":"id1","pw":"pw1"},{"id":"id2","pw":"pw2"}]')
            print('json generate site https://jsoneditoronline.org/')
            exit()
        credential_length = len(json_obj)
        campaign_links = grep_campaign_links()
        for idx in range(credential_length):
            print(f"{idx+1}번째 계정")
            main(campaign_links, json_obj[idx]["id"], json_obj[idx]["pw"], headness)
    else:
        if args.id is None:
            print('use -i or --id argument')
            exit()
        if args.pw is None:
            print('use -p or --pwd argument')
            exit()
        campaign_links = grep_campaign_links()
        main(campaign_links, args.id, args.pw, headness)
