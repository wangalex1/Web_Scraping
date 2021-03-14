import re
import time

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from user_agent import generate_user_agent


# TODO: rewrite this
def format_data(name, link, salary, site):
    if "—" in salary:
        min_s, max_s = salary.split("—")
        return "-" * 79 + f"\n{name} ({link})\nMin salary: {min_s}\nMax salary: {max_s}\nSite: {site}"
    elif "-" in salary:
        min_s, max_s = salary.split("-")
        return "-" * 79 + f"\n{name} ({link})\nMin salary: {min_s}\nMax salary: {max_s}\nSite: {site}"
    elif "от" in salary.lower():
        min_s = re.search(r"от\s*(\d+[^до]*)(до|руб|kzt|₽)", salary.lower())
        min_s = min_s.group(1) if min_s else salary
        max_s = "-"
        return "-" * 79 + f"\n{name} ({link})\nMin salary: {min_s}\nMax salary: {max_s}\nSite: {site}"
    else:
        return "-" * 79 + f"\n{name} ({link})\nSalary: {salary}\nSite: {site}"


def make_request(url, params):
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": generate_user_agent()})
        resp.raise_for_status()
        return resp.text
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} while parsing hh.ru (maybe number of pages was too big)')


def parse_hh(vacancy, pages):
    search_url = "https://hh.ru/search/vacancy"

    for page in range(pages):

        time.sleep(1)

        params = {"text": f"{vacancy}", "page": f"{page}"}

        html = make_request(search_url, params=params)

        if html is None:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        job_list = soup.find_all("div", class_="vacancy-serp-item")
        for job in job_list:
            link = job.find('a').get('href', 'no link')
            name = job.find('a').get_text()
            salary_div = job.find("div", class_="vacancy-serp-item__compensation")
            salary = "З/П не указана"
            if salary_div:
                salary = salary_div.get_text()
            print(format_data(name, link, salary, "hh.ru"))


def main():
    position = input("Введите должность: ")  # python
    page_num = int(input("Введите кол-во страниц: "))  # 2

    parse_hh(position, page_num)


if __name__ == "__main__":
    main()