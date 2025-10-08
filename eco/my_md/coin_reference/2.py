import requests
from bs4 import BeautifulSoup
import re
import json
import time

BASE_URL = "https://www.ouchyi.support"
START_URL = "https://www.ouchyi.support/zh-hans/learn/category/trading-ideas"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_all_article_links(start_url):
    """
    抓取分类页面中所有文章链接（含分页自动识别）
    """
    links = set()
    next_page = start_url

    while next_page:
        print(f"🔍 正在抓取页面：{next_page}")
        res = requests.get(next_page, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 匹配所有以 /zh-hans/learn/ 开头且以 -cn 结尾的文章
        for a in soup.select("a[href*='/zh-hans/learn/']"):
            href = a.get("href")
            if href and re.search(r"/zh-hans/learn/[^/]+-cn$", href):
                links.add(BASE_URL + href)

        # 检测是否有分页按钮（如 “下一页”）
        next_btn = soup.find("a", string=re.compile("下一页|Next"))
        if next_btn and next_btn.get("href"):
            next_page = BASE_URL + next_btn["href"]
            time.sleep(1)
        else:
            next_page = None

    print(f"✅ 共发现 {len(links)} 篇文章。")
    return list(links)


def parse_article(url):
    """
    抓取单篇文章内容
    """
    print(f"📖 抓取文章：{url}")
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 标题
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "未知标题"

    # 日期
    date = ""
    time_tag = soup.find("time")
    if time_tag:
        date = time_tag.get_text(strip=True)
    else:
        meta_date = soup.find("meta", {"property": "article:published_time"})
        if meta_date and meta_date.get("content"):
            date = meta_date["content"]

    # 正文（兼容多种结构）
    article_section = (
        soup.find("article")
        or soup.find("div", class_=re.compile("(article-content|learn-article|content-body)"))
    )

    paragraphs = []
    if article_section:
        for p in article_section.find_all(["p", "li"]):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
    else:
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)

    return {
        "title": title,
        "url": url,
        "date": date,
        "content": "\n".join(paragraphs)
    }


def main():
    article_links = get_all_article_links(START_URL)
    results = []

    for i, url in enumerate(article_links, 1):
        try:
            article = parse_article(url)
            results.append(article)
            time.sleep(1)
        except Exception as e:
            print(f"❌ 抓取失败：{url}, 错误：{e}")

    with open("ouchyi_all_articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"🎉 全部完成，共 {len(results)} 篇，保存为 ouchyi_all_articles.json")


if __name__ == "__main__":
    main()
