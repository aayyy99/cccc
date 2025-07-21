import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
import re

# 省份对应的FOFA链接
urls_dict = {
    "hebei": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iSGViZWki",
    "beijing": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iYmVpamluZyI%3D",
    "guangdong": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iZ3Vhbmdkb25nIg%3D%3D",
    "shanghai": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbmdoYWki",
    "tianjin": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0idGlhbmppbiI%3D",
    "chongqing": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iY2hvbmdxaW5nIg%3D%3D",
    "shanxi": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbnhpIg%3D%3D",
    "shaanxi": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iU2hhYW54aSI%3D",
    "liaoning": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ibGlhb25pbmci",
    "jiangsu": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iamlhbmdzdSI%3D",
    "zhejiang": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iemhlamlhbmci",
    "anhui": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5a6J5b69Ig%3D%3D",
    "fujian": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iRnVqaWFuIg%3D%3D",
    "jiangxi": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rGf6KW%2FIg%3D%3D",
    "shandong": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5bGx5LicIg%3D%3D",
    "henan": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5Y2XIg%3D%3D",
    "hubei": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5YyXIg%3D%3D",
    "hunan": "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5Y2XIg%3D%3D"
}

def process_url(url):
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    # 使用WebDriver访问网页
    driver.get(url)
    time.sleep(10)
    # 获取网页内容
    page_content = driver.page_source
    driver.quit()

    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    urls_all = re.findall(pattern, page_content)
    urls = list(set(urls_all))  # 去重

    for url in urls:
        print(url)

    results = []
    for url in urls:
        try:
            json_url = f"{url}/iptv/live/1000.json?key=txiptv"
            response = requests.get(json_url, timeout=3)
            json_data = response.json()

            for item in json_data.get('data', []):
                if isinstance(item, dict):
                    name = item.get('name')
                    urlx = item.get('url')
                    urld = f"{url}{urlx}"

                    if name and urlx:
                        # 频道名格式化
                        name = name.replace("中央", "CCTV").replace("高清", "").replace("HD", "")\
                            .replace("标清", "").replace("频道", "").replace("-", "")\
                            .replace(" ", "").replace("PLUS", "+").replace("(", "")\
                            .replace(")", "").replace("CCTV1综合", "CCTV1").replace("CCTV2财经", "CCTV2")\
                            .replace("CCTV3综艺", "CCTV3").replace("CCTV4国际", "CCTV4")\
                            .replace("CCTV4中文国际", "CCTV4").replace("CCTV5体育", "CCTV5")\
                            .replace("CCTV6电影", "CCTV6").replace("CCTV7军事", "CCTV7")\
                            .replace("CCTV7军农", "CCTV7").replace("CCTV7国防军事", "CCTV7")\
                            .replace("CCTV8电视剧", "CCTV8").replace("CCTV9记录", "CCTV9")\
                            .replace("CCTV9纪录", "CCTV9").replace("CCTV10科教", "CCTV10")\
                            .replace("CCTV11戏曲", "CCTV11").replace("CCTV12社会与法", "CCTV12")\
                            .replace("CCTV13新闻", "CCTV13").replace("CCTV新闻", "CCTV13")\
                            .replace("CCTV14少儿", "CCTV14").replace("CCTV15音乐", "CCTV15")\
                            .replace("CCTV16奥林匹克", "CCTV16").replace("CCTV17农业农村", "CCTV17")\
                            .replace("CCTV5+体育赛视", "CCTV5+").replace("CCTV5+体育赛事", "CCTV5+")
                        results.append(f"{name},{urld}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to process JSON for URL {json_url}. Error: {str(e)}")
            continue
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON for URL {url}. Error: {str(e)}")
            continue

    return results

def save_results(results, filename):
    # 保存结果到文本文件
    with open(filename, "w", encoding="utf-8") as file:
        for result in results:
            file.write(result + "\n")
            print(result)

if __name__ == '__main__':
    all_files = []
    # 依次处理每个省份
    for province, url in urls_dict.items():
        results = process_url(url)
        txt_file = f"{province}.txt"
        save_results(results, txt_file)
        all_files.append(txt_file)

    # 合并所有省份文件到IPTV.txt
    file_contents = []
    for file_path in all_files:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)

    with open("IPTV.txt", "w", encoding="utf-8") as output:
        output.write('\n'.join(file_contents))
