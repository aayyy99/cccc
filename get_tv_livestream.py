from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import re
import random

def wait_for_download(download_dir, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        txt_files = [f for f in os.listdir(download_dir) if f.endswith('.txt')]
        if txt_files:
            return max([os.path.join(download_dir, f) for f in txt_files], key=os.path.getctime)
        time.sleep(1)
    return None

def get_livestream_data(search_keywords):
    url = "http://live-search.cniptv.top/zbss/"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(current_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True)
    print(f"下载目录: {download_dir}")

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = None
    all_collected_urls = set()

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        print(f"正在访问：{url}")
        time.sleep(random.uniform(1, 3))

        print("等待并点击 '线路2'...")
        try:
            line2_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '线路2')]"))
            )
            line2_button.click()
        except TimeoutException:
            print("线路2 按钮加载超时，尝试刷新页面...")
            driver.refresh()
            time.sleep(2)
            line2_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '线路2')]"))
            )
            line2_button.click()
        print("'线路2' 已点击。")
        time.sleep(random.uniform(1, 3))

        for keyword in search_keywords:
            print(f"\n--- 正在搜索关键词: '{keyword}' ---")
            search_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='搜索关键词，回车搜索']"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.submit()
            print(f"已输入 '{keyword}' 并触发搜索。")
            time.sleep(random.uniform(2, 5))

            print("等待 '一键下载TXT' 按钮...")
            try:
                download_txt_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., '一键下载TXT')]"))
                )
                download_txt_button.click()
                print(f"'一键下载TXT' 已点击，用于 '{keyword}'。")
            except TimeoutException:
                print(f"未找到 '一键下载TXT' 按钮，跳过 '{keyword}'。")
                continue

            latest_file = wait_for_download(download_dir, timeout=120)
            if latest_file:
                print(f"检测到新下载文件: {os.path.basename(latest_file)}")
                with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = re.findall(r".+?,https?://.+", content)
                    for line in lines:
                        all_collected_urls.add(line.strip())
                os.remove(latest_file)
                print(f"已从 '{keyword}' 结果中收集 {len(lines)} 条直播源，并已删除临时文件。")
            else:
                print(f"未找到 '{keyword}' 的下载文件。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            driver.quit()

    return sorted(list(all_collected_urls))

if __name__ == "__main__":
    keywords_to_search = ["齐鲁", "山东卫视"]
    final_livestreams = get_livestream_data(keywords_to_search)
    output_filename = "combined_livestreams.txt"
    if final_livestreams:
        with open(output_filename, "w", encoding="utf-8") as output:
            for line in final_livestreams:
                output.write(line + "\n")
        print(f"\n--- 已将所有去重后的直播源合并到 {output_filename} ({len(final_livestreams)} 行) ---")
    else:
        print(f"\n--- 没有找到任何直播源可合并到 {output_filename} ---")
    print("\n脚本运行结束。")
