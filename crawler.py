import requests
from lxml import html
import csv

def crawl(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return parse_html(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        return None

def parse_html(html_text):
    try:
        tree = html.fromstring(html_text)
        td_list = tree.xpath('//table[@id="top20"]/thead/tr/th/text()')
        tt_list = []
        tr_list = tree.xpath('//table[@id="top20"]/tbody/tr')
        tt_list.append(td_list)
        for tr in tr_list:
            td_text:list[str] = tr.xpath('./td/text()')
            td_text.insert(2,'')
            tt_list.append(td_text)
        write_csv(tt_list)
        return  tt_list
    except IndexError:
        print("Error parsing HTML: No title or paragraphs found.")
        return None, None

def write_csv(tt_list):
    with open('csv_data/tiobe_index.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(tt_list)

for t in crawl("https://www.tiobe.com/tiobe-index/"):
    print(t)