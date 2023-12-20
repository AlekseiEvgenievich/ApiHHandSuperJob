import json
import os
import pathlib
import time
from datetime import datetime, timedelta
from urllib.parse import unquote, urlsplit

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from is not None and salary_to is not None:
        if salary_from == 0 and salary_to == 0:
            return None
        elif salary_from != 0 and salary_to == 0:
            return 1.2*salary_from
        elif salary_from == 0 and salary_to != 0:
            return 0.8*salary_to
        return (salary_from + salary_to)/2
    elif salary_from is None and salary_to is not None:
        return 0.8*salary_to
    elif salary_from is not None and salary_to is None:
        return 1.2*salary_from
    else:
        return None
        

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    else:
        return predict_salary(vacancy['payment_from'],vacancy['payment_to'] )
    

def predict_rub_salary_hh(vacancy):
    if vacancy['salary'] is None:
        return None
    else:
        if vacancy['salary']['currency'] == 'RUR':
            return predict_salary(vacancy['salary']['from'],vacancy['salary']['to'])
        else:
            return None


def get_hh_dict(hh_search_field,hh_area,hh_period):
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    hh_dict = {lang: {"vacancies_found": 0, "vacancies_processed": 0, "average_salary": 0} for lang in languages}
    hh_url = 'https://api.hh.ru/vacancies/'
    for language in languages:
        url = 'https://api.hh.ru/vacancies/'
        total_count = 0
        total_salary = 0
        page = 0
        pages_number = 1
        while page < pages_number:
            time.sleep(0.1)
            page_response = requests.get(hh_url, params={'page': page,'text': language,'search_field': hh_search_field, 'area':int(hh_area),'period':int(hh_period)})
            page_response.raise_for_status()
            page_payload = page_response.json()
            pages_number = page_payload['pages']
            page += 1
            hh_dict[language]["vacancies_found"] += len(page_payload['items'])
            for vacancy in page_payload["items"]:
                salary = predict_rub_salary_hh(vacancy)
                if salary is not None:
                    total_salary += salary
                    total_count += 1
        if total_count > 0:
            hh_dict[language]["vacancies_processed"] = total_count
            hh_dict[language]["average_salary"] = total_salary // total_count
    return hh_dict


def get_sj_dict(sj_token,sj_catalogue,sj_srws,sj_skws,sj_town):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_token
    }
    current_date = datetime.now()
    one_month_ago = current_date - timedelta(days=30)
    unixtime_one_month_ago = int(time.mktime(one_month_ago.timetuple()))
    
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    superjob_dict = {lang: {"vacancies_found": 0, "vacancies_processed": 0, "average_salary": 0} for lang in languages}
    for language in languages:
        page = 0
        total_salary = 0
        total_count = 0
        while True:
            response = requests.get(superjob_url,  headers=headers,params={
                'page': page,
                'catalogues': int(sj_catalogue),
                'date_published_from': unixtime_one_month_ago,
                't':int(sj_town),
                'srws': int(sj_srws),
                'skwc': sj_skws,
                'keys': language
            })
            response.raise_for_status()
            page_payload = response.json()
            superjob_dict[language]["vacancies_found"] += len(page_payload['objects'])
            for vacancy in page_payload['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary is not None:
                    total_salary += salary
                    total_count += 1
            if not page_payload['more']:
                break
            page += 1
        if total_count > 0:
            superjob_dict[language]["vacancies_processed"] = total_count
            superjob_dict[language]["average_salary"] = total_salary // total_count
    return superjob_dict


def get_table(dict):
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    table_data = [["languages","vacancies_found","vacancies_processed","average_salary"]]
    for language,details in dict.items():
        table_data.append([language,details['vacancies_found'], details['vacancies_processed'],details['average_salary']])
    return table_data
    

if __name__ == '__main__':
    load_dotenv()
    sj_token = os.environ["SJ_TOKEN"]
    sj_catalogue = os.environ["SJ_CATALOGUES"]
    sj_srws = os.environ["SJ_SRWS"]
    sj_skws = os.environ["SJ_SKWS"]
    sj_town = os.environ["SJ_TOWN"]
    
    hh_search_field = os.environ["HH_SEARCH_FIELD"]
    print(hh_search_field)
    hh_area = os.environ["HH_AREA"]
    hh_period = os.environ["HH_PERIOD"]
    
    hh_dict = get_hh_dict(hh_search_field,hh_area,hh_period)
    hh_table = get_table(hh_dict)
    
    sj_dict = get_sj_dict(sj_token,sj_catalogue,sj_srws,sj_skws,sj_town)
    sj_table = get_table(sj_dict)
    
    hh_tittle = 'HeadHunter Moscow'
    hh_table_instance = AsciiTable(hh_table,hh_tittle)
    print(hh_table_instance.table)
    
    sj_tittle = 'SuperJob Moscow'
    sj_table_instance = AsciiTable(sj_table,sj_tittle)
    print(sj_table_instance.table)
