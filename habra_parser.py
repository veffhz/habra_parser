from bs4 import BeautifulSoup
from helper import clean_word, group_by_weeks

import requests
import pymorphy2
import dateparser
import argparse


def generate_new_url(page_num):
    """generate new habr.com url by page number"""
    base_url = "https://habr.com/all/"
    return "{}/page{}".format(base_url, page_num)


def download_raw_pages_content(pages_count):
    """download habr pages by page count"""
    return [fetch_raw_content(page) for page in range(1, pages_count + 1)]


def fetch_pages_count_from_args():
    """fetch pages count for habr urls"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pages', help='Count pages to parse', type=int)
    args = parser.parse_args()
    default_value = 1
    return args.pages or default_value


def fetch_raw_content(page):
    """get raw page content"""
    url = generate_new_url(page)
    request = requests.get(url)
    return request.text


def extract_data_by_class(raw_content, elem, class_name, is_all=False):
    """extract html tags by element and class name"""
    parser = "html.parser"
    soup = BeautifulSoup(str(raw_content), parser)
    if is_all:
        return soup.find_all(elem, class_=class_name)
    else:
        return soup.find(elem, class_=class_name)


def extract_date(raw_item):
    """extract post date from html"""
    text_date = extract_data_by_class(raw_item, "span", "post__time").contents[0]
    return dateparser.parse(text_date).date()


def parse_block(article_block):
    """parse post date ant title from article block element"""
    post_date = extract_date(article_block)
    post_title = extract_data_by_class(article_block, "a", "post__title_link").contents[0]
    return post_date, post_title.split(" ")


def process_page_content(page_content):
    """iterate over article block elements"""
    items = []
    article_blocks = extract_data_by_class(page_content, "article", "post post_preview", is_all=True)
    for article_block in article_blocks:
        parsed_data = parse_block(article_block)
        post_date = parsed_data[0]
        words = filter_words_on_morphy(parsed_data[1])
        if words:
            items.append(
                (post_date, words)
            )
    return items


def collect_items(pages_content):
    """collect post date ant title elements"""
    data = {}
    for page_content in pages_content:
        items = process_page_content(page_content)
        for item in items:
            post_date = item[0]
            words = item[1]
            if post_date in data:
                data[post_date].extend(words)
            else:
                data[post_date] = words
    return data


def filter_words_on_morphy(words):
    """get nouns from word list"""
    filtered = []
    morph = pymorphy2.MorphAnalyzer()
    for word in words:
        cleaned_word = clean_word(word)
        p = morph.parse(cleaned_word)[0]
        if "NOUN" in p.tag or "LATN" in p.tag:
            filtered.append(p.normal_form)
    return filtered


def print_result(data):
    for item in data:
        print("{} {}".format(item, data[item]))


def main():
    pages_count = fetch_pages_count_from_args()
    pages_content = download_raw_pages_content(pages_count)
    data = collect_items(pages_content)
    data_grouped_by_week = group_by_weeks(data)
    print_result(data_grouped_by_week)


if __name__ == "__main__":
    main()
