import os
import time
from datetime import datetime, timedelta

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


def process_hh_vacancies():
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    city_id = 1
    search_period = 30
    min_timeout = 0.1
    hh_vacancies = {}
    hh_url = 'https://api.hh.ru/vacancies/'
    for language in languages:
        url = 'https://api.hh.ru/vacancies/'
        total_count = 0
        total_salary = 0
        vacancies_found = 0
        page = 0
        pages_number = 1
        while page < pages_number:
            time.sleep(min_timeout)
            page_response = requests.get(hh_url, params={'page': page,'text': language,'search_field': 'name', 'area':city_id,
            'period':search_period})
            page_response.raise_for_status()
            page_payload = page_response.json()
            pages_number = page_payload['pages']
            page += 1
            for vacancy in page_payload["items"]:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    total_salary += salary
                    total_count += 1
        total_vacancies_found = page_payload['found']
        if total_count:
            average_salary = total_salary // total_count
        else:
            average_salary = 0
            
        hh_vacancies[language] = {
            "vacancies_found": total_vacancies_found,
            "vacancies_processed": total_count,
            "average_salary": average_salary
        }
    return hh_vacancies


def process_sj_vacancies(sj_token):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': sj_token
    }
    industry_catalogue_id = 48
    city_id = 4
    search_in_text_block = 1
    current_date = datetime.now()
    one_month_ago = current_date - timedelta(days=30)
    timestamp_one_month_ago = int(time.mktime(one_month_ago.timetuple()))
    
    languages = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    sj_vacancies = {}
    for language in languages:
        page = 0
        total_salary = 0
        total_count = 0
        vacancies_found = 0
        while True:
            response = requests.get(superjob_url,  headers=headers,params={
                'page': page,
                'catalogues': industry_catalogue_id,
                'date_published_from': timestamp_one_month_ago,
                't':city_id,
                'srws': search_in_text_block,
                'skwc': 'AND',
                'keys': language
            })
            response.raise_for_status()
            page_payload = response.json()
            for vacancy in page_payload['objects']:
                salary = predict_rub_salary_sj(vacancy)
                if salary:
                    total_salary += salary
                    total_count += 1
            if not page_payload['more']:
                break
            page += 1
        total_vacancies_found = page_payload['total']
        if total_count:
            average_salary = total_salary // total_count
        else:
            average_salary = 0
        
        sj_vacancies[language] = {
            "vacancies_found": total_vacancies_found,
            "vacancies_processed": total_count,
            "average_salary": average_salary
        }
    return sj_vacancies


def get_language_vacancy_stats(programming_vacancies_data):
    language_vacancy_stats = [["languages","vacancies_found","vacancies_processed","average_salary"]]
    for language,vacancies in programming_vacancies_data.items():
        language_vacancy_stats.append([language,vacancies['vacancies_found'], vacancies['vacancies_processed'],vacancies['average_salary']])
    return language_vacancy_stats
    

if __name__ == '__main__':
    load_dotenv()
    sj_token = os.environ["SJ_TOKEN"]
    
    hh_vacancies = process_hh_vacancies()
    hh_language_vacancy_stats = get_language_vacancy_stats(hh_vacancies)
    
    sj_vacancies = process_sj_vacancies(sj_token)
    sj_language_vacancy_stats = get_language_vacancy_stats(sj_vacancies)
    
    hh_tittle = 'HeadHunter Moscow'
    hh_language_vacancy_stats_instance = AsciiTable(hh_language_vacancy_stats,hh_tittle)
    print(hh_language_vacancy_stats_instance.table)
    
    sj_tittle = 'SuperJob Moscow'
    sj_language_vacancy_stats_instance = AsciiTable(sj_language_vacancy_stats,sj_tittle)
    print(sj_language_vacancy_stats_instance.table)
