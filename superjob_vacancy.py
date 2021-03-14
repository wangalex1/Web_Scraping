import pandas as pd
import requests
from pprint import pprint
import json
from getpass import getpass
from bs4 import BeautifulSoup as bs
import pytils.translit as ptr
import time

OUTER_JOB_BLOCK = {'class': 'iJCa5 f-test-vacancy-item _1fma_ undefined _2nteL'}
JOB_TITLE = {'class': '_3mfro PlM3e _2JVkc _3LJqf'}
SALARY_BLOCK = {'class': "_3mfro _2Wp8I PlM3e _2JVkc _2VHxz"}
COMPANY_BLOCK = {'class': "_3mfro _3Fsn4 f-test-text-vacancy-item-company-name _9fXTd _2JVkc _2VHxz _15msI"}
JOB_URL = {'class': '_3mfro PlM3e _2JVkc _3LJqf'}


def make_translit(word):  # преобразует слово в кириллице в английские буквы
    word = word.lower()
    return ptr.translify(word)


def parse_salary(data_string):  # преобразует строку зп в кортеж мин и макс. зп в числовом виде
    if data_string == 'По договорённости':
        salary_min=None
        salary_max=None
    else:
        data_list=data_string.split()
        if data_list[0] == 'от':
            salary_min=int(data_list[1] + data_list[2])
            salary_max=None
        elif data_list[0] == 'до':
            salary_min=None
            salary_max=int(data_list[1] + data_list[2])
        elif len(data_list) == 6:
            salary_min=int(data_list[0] + data_list[1])
            salary_max=int(data_list[3] + data_list[4])
        else:
            salary_min=int(data_list[0] + data_list[1])
            salary_max=salary_min
    return salary_min, salary_max


def collect_data_from_page(page_html):  # собираем данные с одной страницы
    jobs=[]
    for v in page_html.find_all('div', OUTER_JOB_BLOCK):
        job_title=v.find('div', JOB_TITLE).text
        try:
            job_salary=v.find('span', SALARY_BLOCK).text
            job_salary=parse_salary(job_salary)
        except:
            job_salary= "NaN"
        try:
            job_provider=v.find('span', COMPANY_BLOCK).text
        except:
            job_provider=None
        try:
            job_page_url='https://russia.superjob.ru//' + v.find('div', JOB_URL).find('a', {'target': '_blank'})['href']
        except:
            job_page_url = None
        jobs.append([job_title, job_provider, job_salary[0], job_salary[1], job_page_url])
    return jobs


def convert_list_2_df(data_list):  # переводим массив данных в формат dataframe
    df=pd.DataFrame([], columns=['Job_Title', 'Employer', 'Salary_min', 'Salary_max', 'URL'])
    job_title_list, employer_list, salary_min_list, salary_max_list, url_list = [], [], [], [], []
    for vacancy in data_list:
        job_title_list.append(vacancy[0])
        employer_list.append(vacancy[1])
        salary_min_list.append(vacancy[2])
        salary_max_list.append(vacancy[3])
        url_list.append(vacancy[4])
    df['Job_Title']=job_title_list
    df['Employer']=employer_list
    df['Salary_min']=salary_min_list
    df['Salary_max']=salary_max_list
    df['URL']=url_list
    return df


def collect_all_data(job_name,  verbose=True):  # запускает цикл по старницам и выводит конечный результат в фомате Dataframe
    preprocessed_list=[]
    page=1
    job_name_eng=make_translit(job_name)
    print(job_name_eng)

    while True:
        request_url_1=f'https://russia.superjob.ru/vakansii/{job_name_eng}.html?&page={page}'
        request_url_1=f'https://russia.superjob.ru/vacancy/search/?keywords={job_name_eng}&page={page}'
        if requests.get(request_url_1).ok:
            request_url=request_url_1
        elif request.get(request_url_2).ok:
            request_url=request_url_2
        else:
            print('something wrong, operation stopped')
            break
            return None
        page_request=requests.get(request_url)
        page_html=bs(page_request.text, 'lxml')
        print("УДАЧНО")
        if page_html.find_all('a', NEXT_BUTTON) != []:
            page_data=collect_data_from_page(page_html)
            preprocessed_list.extend(page_data)
            page+=1
        else:
            page_data=collect_data_from_page(page_html)
            preprocessed_list.extend(page_data)
            break
    df=convert_list_2_df(preprocessed_list)
    return df
name = 'Data Scientist'
final_df = collect_all_data(name, verbose=False)
print(final_df)
display(final_df.head(10))
display(final_df.shape)