import time
import requests
import json
import re
import random
from urllib.parse import urlparse, parse_qs

headers = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
                   "537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/"
                   "537.36"),
    "host": "wenku.baidu.com",
}

wenku_view_url = "https://wenku.baidu.com/view/"

# doc_id = "3c2a63f130d4b14e852458fb770bf78a65293a97"


def parse_web_url(url: str) -> tuple:
    # 获取 doc_id
    doc_id_list = re.findall(r"https://wenku.baidu.com/view/(.*?).html", url)
    if len(doc_id_list) == 0:
        doc_id = ""
    else:
        doc_id = doc_id_list[0]

    # 解析 URL 查询参数
    parsed_url = urlparse(url)
    # 获取查询参数字符串
    query_params = parsed_url.query
    # 解析查询参数
    query_info = parse_qs(query_params, keep_blank_values=True)

    return doc_id, query_info


def check_url(url: str, doc_id: str) -> bool:
    if url.startswith(wenku_view_url) and doc_id:
        return True
    return False


def get_page_date(url: str, query_info: dict) -> dict | BaseException:
    wkts = int(time.time() * 1000)
    query_info["_wkts_"] = wkts
    response = requests.get(url=url, params=query_info, headers=headers)
    try:
        page_data_str = re.findall(r"var pageData = (.*?);", response.text)[0]
        page_data = json.loads(page_data_str.strip())
        return page_data
    except BaseException as error:
        return error


def get_read_info(document_url: str, doc_id: str,
                  reader_info: dict, query_info: dict):
    url = "https://wenku.baidu.com/ndocview/readerinfo"
    # 1 表示来自百度搜索 0表示其他
    is_from_bd_search = random.randint(0, 1)
    params = {
        "doc_id": doc_id,
        "docId": doc_id,
        "type": "html",
        "clientType": 1,
        "pn": reader_info["showPage"] + 1,
        "t": int(time.time() * 1000),
        # /(www|m)\.baidu\.com/.test(document.referrer) ? 1 : 0
        "isFromBdSearch": is_from_bd_search,
        # 0 === this.resetNewDoc.count ? document.referrer.split("?")[0] :
        # location.href.split("?")[0]
        "srcRef": "https://www.baidu.com/link" if is_from_bd_search else "",
        "rn": 50,
        "powerId": 2,
        "bizName": "mainPc",
    }
    bd_query = query_info.get("bdQuery", None)
    wk_query = query_info.get("wkQuery", None)
    if bd_query:
        params["bdQuery"] = bd_query[0]
    if wk_query:
        params["wkQuery"] = wk_query[0]
    response = requests.get(
        url, params=params, headers={
            "referer": document_url, **headers})
    return response.text


def get_document_data(url: str):
    doc_id, query_info = parse_web_url(url)
    if not check_url(url, doc_id):
        print(f"百度文库地址 {url} 错误")
        return
    page_data = get_page_date(f"{wenku_view_url}{doc_id}.html", query_info)
    if isinstance(page_data, BaseException):
        print(f"获取页面数据错误, message: {str(page_data)}")
        return


def main():
    pass


if __name__ == "__main__":
    main()
