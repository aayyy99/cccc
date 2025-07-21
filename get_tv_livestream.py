from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

def get_livestream_data(search_keywords):
    """
    访问 http://live-search.cniptv.top/zbss/ 网站，
    对提供的关键词进行搜索，点击“线路2”，然后点击“一键下载TXT”并收集所有结果。
    """
    url = "http://live-search.cniptv.top/zbss/"
    
    # 获取当前脚本所在目录作为下载路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(current_dir, "downloads")
    os.makedirs(download_dir, exist_ok=True) # 如果 downloads 文件夹不存在则创建

    chrome_options = Options()
    chrome_options.add_argument('--headless')           # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    # 配置下载路径
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safeBrowse.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = None
    all_collected_urls = set() # 使用集合存储所有搜索结果，自动去重

    try:
        # 连接到 Docker 容器中的 Selenium Grid Hub
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chrome_options
        )
        driver.get(url)
        print(f"正在访问：{url}")

        # 1. 等待并点击 "线路2" 按钮 (只需点击一次)
        print("等待并点击 '线路2'...")
        line2_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., '线路2')]"))
        )
        line2_button.click()
        print("'线路2' 已点击。")
        
        # 给页面一些时间加载线路数据
        time.sleep(2) 

        for keyword in search_keywords:
            print(f"\n--- 正在搜索关键词: '{keyword}' ---")
            
            # 清空搜索框（如果里面有上次的关键词）
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='搜索关键词，回车搜索']"))
            )
            search_input.clear() # 清空输入框内容
            
            # 输入新的关键词并触发搜索
            search_input.send_keys(keyword)
            search_input.submit()
            print(f"已输入 '{keyword}' 并触发搜索。")
            
            # 给页面一些时间加载搜索结果
            time.sleep(5) 

            # 点击“一键下载TXT”按钮
            print("等待 '一键下载TXT' 按钮...")
            download_txt_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '一键下载TXT')]"))
            )
            download_txt_button.click()
            print(f"'一键下载TXT' 已点击，用于 '{keyword}'。")

            # 等待文件下载完成
            # 注意：Selenium 不直接知道文件何时下载完成，这里只是给一个固定的等待时间
            time.sleep(5) 
            
            # 获取最新下载的文件，并读取其内容
            # 找到 downloads 目录下最新的 .txt 文件
            list_of_files = os.listdir(download_dir)
            txt_files = [os.path.join(download_dir, f) for f in list_of_files if f.endswith('.txt')]
            if txt_files:
                latest_file = max(txt_files, key=os.path.getctime) # 找到创建时间最新的文件
                print(f"检测到新下载文件: {os.path.basename(latest_file)}")
                with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 提取所有 "名称,http://URL" 格式的行
                    lines = re.findall(r".+?,https?://.+", content)
                    for line in lines:
                        all_collected_urls.add(line.strip())
                os.remove(latest_file) # 读取后删除临时下载文件
                print(f"已从 '{keyword}' 结果中收集 {len(lines)} 条直播源，并已删除临时文件。")
            else:
                print(f"未找到 '{keyword}' 的下载文件。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        if driver:
            driver.quit() # 确保关闭浏览器

    return sorted(list(all_collected_urls)) # 返回排序后的去重结果

if __name__ == "__main__":
    # 定义要搜索的关键词列表
    keywords_to_search = ["齐鲁", "山东卫视"]
    
    # 执行搜索并获取所有直播源
    final_livestreams = get_livestream_data(keywords_to_search)

    # 将所有去重后的结果保存到 combined_livestreams.txt
    output_filename = "combined_livestreams.txt"
    if final_livestreams:
        with open(output_filename, "w", encoding="utf-8") as output:
            for line in final_livestreams:
                output.write(line + "\n")
        print(f"\n--- 已将所有去重后的直播源合并到 {output_filename} ({len(final_livestreams)} 行) ---")
    else:
        print(f"\n--- 没有找到任何直播源可合并到 {output_filename} ---")

    print("\n脚本运行结束。")
