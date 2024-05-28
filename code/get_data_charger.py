from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")  # 브라우저창 사이즈 조절

# ChromeDriver 경로 설정
chrome_driver_path = "/Users/USER/Documents/GitHub/project001/chromedriver.exe"
# Chrome WebDriver 객체 생성
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)
# 웹 페이지 로드
url = "https://skelectlink.co.kr/charger"
driver.get(url)

# 페이지 소스 가져오기
soup = BeautifulSoup(driver.page_source, "html.parser")

contentlist = []
main_title = []
sub_title = []
# 원하는 텍스트 추출 (예: 특정 태그나 클래스 선택)
for i in range(5):
    contentlist.append(
        soup.select(
            f"#__next > div:nth-child(2) > div:nth-child(2) > div:nth-child({i+1}) > div > div"
        )
    )
    main_title.append(contentlist[i][0].text.strip())  # 제목
    sub_title.append(contentlist[i][1].text.strip())  # 내용

df1 = pd.DataFrame({"제목": main_title, "내용": sub_title})
df1.to_excel(r'C:\Users\USER\Documents\GitHub\project001\chargerInfo.xlsx', index=False)

charger_func = []
for i in range(2):
    charger_func.append(
        soup.select(
            f"#__next > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div > div:nth-child({i+3}) > div > div > table"
        )[0].text.strip()
    )
print(charger_func)
df2 = pd.DataFrame({"충전기기능": charger_func})
df2.to_excel(r"C:\Users\USER\Documents\GitHub\project001\functions.xlsx", index=False)

model_names = []
models = soup.select("div.goods-title.common-text-1")
for i in range(13):
    model_names.append(models[i].text.strip())
print(model_names)

detail = []
for i in range(2, 9):  # 완속 충전 모델
    try:
        driver.find_element(  # 자세히 보기 버튼 클릭
            By.CSS_SELECTOR,
            f"#__next > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > div.sc-jqUVSM.hYPGgq.box-listType-2 > div:nth-child(1) > div:nth-child({i+2}) > div > div > div.link",
        ).click()

        # table 내용 읽어오기
        soup = BeautifulSoup(driver.page_source, "html.parser")
        elements = soup.select("div.table-wrapper table")
        detail.append(elements[0].text.strip().strip("\n"))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.find_element(  # 닫기 버튼 클릭
            By.XPATH, "/html/body/div[2]/div/div/div/div[2]/button"
        ).click()
        time.sleep(2)

        # print("닫기버튼눌림")
    except Exception as e:
        print(e)


driver.execute_script("window.scrollTo(0, 0);")
time.sleep(5)

for i in range(2, 8):  # 급속 충전 모델
    try:
        driver.find_element(  # 자세히 보기 버튼 클릭
            By.CSS_SELECTOR,
            f"#__next > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div > div.sc-jqUVSM.hYPGgq.box-listType-2 > div:nth-child(2) > div:nth-child({i+2}) > div > div > div.link",
        ).click()

        # table 내용 읽어오기
        soup = BeautifulSoup(driver.page_source, "html.parser")
        elements = soup.select("div.table-wrapper table")
        detail.append(elements[0].text.strip().strip("\n"))
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.find_element(  # 닫기 버튼 클릭
            By.XPATH, "/html/body/div[2]/div/div/div/div[2]/button"
        ).click()
        time.sleep(2)

        # print("닫기버튼눌림")

    except Exception as e:
        print(e)


print(detail)
df2 = pd.DataFrame({"모델명": model_names, "내용": detail})
df2.to_excel(
    r"C:\Users\USER\Documents\GitHub\project001\modelinfo.xlsx",
    index=False,
)

driver.quit()
