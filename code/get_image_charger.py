from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.request
import os

# ChromeDriver 경로 설정 (필요시 절대 경로로 수정)
driver = webdriver.Chrome()

# 웹 페이지 열기
driver.get("https://skelectlink.co.kr/charger")

# 페이지가 완전히 로드될 때까지 기다리기
time.sleep(3)

# 페이지 스크롤 대기 시간
PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")
new_height = 0

# 페이지 끝까지 스크롤
while True:
    driver.execute_script("window.scrollBy(0, 5000)")
    time.sleep(PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 모든 이미지 요소 찾기
img_elements = driver.find_elements(By.TAG_NAME, "img")
imgs = []

# 이미지 URL 및 alt 속성 추출
for idx, img in enumerate(img_elements):
    try:
        img_src = img.get_attribute("src")
        img_alt = img.get_attribute("alt")
        if img_src:
            imgs.append({"alt": img_alt, "src": img_src})
    except Exception as e:
        print(f"Error at {idx}:", e)
        continue

# 드라이버 종료
driver.quit()

# 이미지 저장 경로 설정
save_path = "./img"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 이미지 다운로드 및 저장
total_N = len(imgs)
for idx, one in enumerate(imgs):
    src = one["src"]
    alt = one["alt"] or "image"
    try:
        urllib.request.urlretrieve(src, f"{save_path}/{alt}_{idx}.png")
        print(f"Downloaded: {alt}_{idx}.png")
    except Exception as e:
        print(f"Failed to download {alt}_{idx}.png: {e}")

print("done")
