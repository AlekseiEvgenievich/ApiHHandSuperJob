import requests
import pathlib
import json
from urllib.parse import unquote
from urllib.parse import urlsplit
import os


def download_image(url, name_path, params=None):
    headers = {
        'User-Agent': 'MyApp/1.0 (my-app-feedback@example.com)'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    print(data)
    with open(name_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def create_db():
    all_data = []
    page = 0
    pages_number = 1
    while page < pages_number:
        page_response = requests.get(url, params={'page': page,'professional_role':96, 'area':1,'period':30})
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        all_data.extend(page_payload['items'])
        page += 1
    return all_data
    
    
def predict_rub_salary(programmimg_languages,all_data):
   vacancy_found = 0
   vacancies_processed = 0
   average_salary = 0
   salary = 0
   for vacancy in all_data:
       if programmimg_languages in vacancy['name']:
           vacancy_found += 1
           if vacancy['salary'] is None:
               pass
           else:
               if vacancy['salary']['currency'] == 'RUR':
                   if (vacancy['salary']['from'] is None) and (vacancy['salary']['to'] is not None):
                       vacancies_processed += 1
                       salary += 0.8 * vacancy['salary']['to']
                   elif (vacancy['salary']['from'] is not None) and (vacancy['salary']['to'] is None):
                       vacancies_processed += 1
                       salary += 1.2 * vacancy['salary']['from']
                   elif (vacancy['salary']['from'] is not None) and (vacancy['salary']['to'] is not None):
                       vacancies_processed += 1
                       salary += (vacancy['salary']['to'] - vacancy['salary']['from'])/2
   print(programmimg_languages)
   print(vacancy_found)
   print(vacancies_processed)
   if vacancies_processed != 0:
       average_salary = salary/vacancies_processed
   else:
       average_salary = 0
       
   print("=================")
   return vacancy_found,vacancies_processed,average_salary
        
    

if __name__ == '__main__':
    path = pathlib.Path("pattt")
    path.mkdir(parents=True, exist_ok=True)
    file_name = path/ "gg.json"
    url = 'https://api.hh.ru/vacancies/'
 #   download_image(url, file_name)
    page = 0
    pages_number = 1
    i = 0
    salary_information = {
        "vacancy_found": 0,
        "vacancies_processed": 0,
        "average_salary": 0
    }
    languages = {
        'Python': salary_information.copy(),
        'Java': salary_information.copy(),
        'C++': salary_information.copy(),
        'JavaScript': salary_information.copy(),
        'C#': salary_information.copy(),
        'C': salary_information.copy(),
        'ruby': salary_information.copy(),
        'go': salary_information.copy(),
        '1c': salary_information.copy(),
        'PHP': salary_information.copy(),
        'Shell': salary_information.copy(),
        'Scala': salary_information.copy(),
        'Swift': salary_information.copy(),
    }
    
    mentions = ['Python', 'Java', 'C++', 'JavaScript','C#','C','ruby','go', '1c', 'PHP','Shell', 'Scala', 'Swift']
    #all_data = create_db()
    #predict_rub_salary('Python',all_data)
    #for programmimg_languages in mentions:
    #    vacancy_found,vacancies_processed,average_salary = predict_rub_salary(programmimg_languages,all_data)
    #    languages[programmimg_languages]["vacancy_found"] = vacancy_found
    #    languages[programmimg_languages]["vacancies_processed"] = vacancies_processed
    #    languages[programmimg_languages]["average_salary"] = average_salary
    page = 0
    pages_number = 1
    while page < pages_number:
        page_response = requests.get(url, params={'page': page,'text': 'P',1 'area':1,'period':30})
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        page += 1
        print(page_payload)
        #print(page_payload["items"])
     #   all_data.extend(page_payload['items'])
        #print(len(page_payload["items"]))
     ##   for k in range(len(page_payload["items"])):
     ##       i = i + 1
     ##       for programmimg_languages in mentions:
     ##           if programmimg_languages.lower() in page_payload["items"][0]["name"].lower():
     ##               languages[programmimg_languages] += 1
            #print(page_payload["items"][0])
            #print(page_payload["items"][0]["name"])
            #print("=======================")
        #print("++++++++++++++++++++++")
      #  page += 1
    print("ggggg")
    print(i)
   # for k in all_data:
   #     print(k['salary'])
   #     print("++++++++++++++++++++++")
    for language,count in languages.items():
        for staff,price in count.items():
            print(f"{language}: {staff} {price}")
        #print(f"{language}: {count}")
    #print(len(all_data))
    
    # TODO добавить данные из page_payload в итоговый список
    ...
    
    
            't':4,
            'srws': 1,  # Например, поиск в должности
            'skwc': 'and',  # Например, поиск всех слов
            'keys': 'Python',
            
            
                    '''
        response = requests.get(url,  headers=headers,params={
            'page': page,
            'srws': 1,  # Например, поиск в должности
            'skwc': 'and',  # Например, поиск всех слов
            'keys': 'Программист' , # Ключевые слова для поиска
            'date_published_from': unixtime_one_month_ago
    })
        '''
