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
    if not salary_from  and not salary_to:
        return None
    elif salary_from  and not salary_to :
        return 1.2 * salary_from
    elif not salary_from and salary_to :
        return 0.8 * salary_to
    else:
        return (salary_from + salary_to) / 2
        

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    else:
        return predict_salary(vacancy['payment_from'],vacancy['payment_to'] )
    

def predict_rub_salary_hh(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])
    return None


def get_hh_job_data():
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    hh_job_data = {}
    hh_url = 'https://api.hh.ru/vacancies/'
    for language in languages:
        url = 'https://api.hh.ru/vacancies/'
        total_count = 0
        total_salary = 0
        vacancies_found = 0
        page = 0
        pages_number = 1
        while page < pages_number:
            time.sleep(0.1)
            page_response = requests.get(hh_url, params={'page': page,'text': language,'search_field': 'name', 'area':1,
            'period':30})
            page_response.raise_for_status()
            page_payload = page_response.json()
            pages_number = page_payload['pages']
            page += 1
            vacancies_found += len(page_payload['items'])
            for vacancy in page_payload["items"]:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    total_salary += salary
                    total_count += 1
        if total_count > 0:
            average_salary = total_salary // total_count
        else:
            average_salary = 0
            
        hh_job_data[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": total_count,
            "average_salary": average_salary
        }
    return hh_job_data


def get_sj_job_data(sj_token):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_token
    }
    current_date = datetime.now()
    one_month_ago = current_date - timedelta(days=30)
    unixtime_one_month_ago = int(time.mktime(one_month_ago.timetuple()))
    
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    sj_job_data = {}
    for language in languages:
        page = 0
        total_salary = 0
        total_count = 0
        vacancies_found = 0
        while True:
            response = requests.get(superjob_url,  headers=headers,params={
                'page': page,
                'catalogues': 48,
                'date_published_from': unixtime_one_month_ago,
                't':4,
                'srws': 1,
                'skwc': 'AND',
                'keys': language
            })
            response.raise_for_status()
            page_payload = response.json()
            vacancies_found += len(page_payload['objects'])
            for vacancy in page_payload['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    total_salary += salary
                    total_count += 1
            if not page_payload['more']:
                break
            page += 1
        if total_count > 0:
            average_salary = total_salary // total_count
        else:
            average_salary = 0
        
        sj_job_data[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": total_count,
            "average_salary": average_salary
        }
    return sj_job_data


def get_table(dict):
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    table_data = [["languages","vacancies_found","vacancies_processed","average_salary"]]
    for language,vacancies in dict.items():
        table_data.append([language,vacancies['vacancies_found'], vacancies['vacancies_processed'],vacancies['average_salary']])
    return table_data
    

if __name__ == '__main__':
    load_dotenv()
    sj_token = os.environ["SJ_TOKEN"]
    
    hh_job_data = get_hh_job_data()
    hh_table = get_table(hh_job_data)
    
    sj_job_data = get_sj_job_data(sj_token)
    sj_table = get_table(sj_job_data)
    
    hh_tittle = 'HeadHunter Moscow'
    hh_table_instance = AsciiTable(hh_table,hh_tittle)
    print(hh_table_instance.table)
    
    sj_tittle = 'SuperJob Moscow'
    sj_table_instance = AsciiTable(sj_table,sj_tittle)
    print(sj_table_instance.table)
