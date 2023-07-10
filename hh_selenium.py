import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

KEY_WORDS = ['python', 'flask', 'django']

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


def wait_elements(driver, delay_seconds=10, by=By.XPATH, value=None):
    return WebDriverWait(driver, delay_seconds).until(
        expected_conditions.presence_of_all_elements_located((by, value)))


def get_links(page_index):
    parsed_list = []
    driver.get(f'https://hh.ru/search/vacancy?area=1&area=2'
               f'&search_field=description&text={"%20".join(KEY_WORDS)}'
               f'&page={page_index}')
    for vacancy in driver.find_elements(By.CLASS_NAME,
                                        'vacancy-serp-item__layout'):
        link_element = vacancy.find_element(By.CLASS_NAME, 'serp-item__title')
        link = link_element.get_attribute('href')
        parsed_list.append(link)
    return parsed_list


def get_data(links, currency=None):
    parse_dict = []
    for item in links:
        driver.get(item)
        salaries = wait_elements(driver, value='//span[@data-qa="vacancy-salary-compensation-type-net"]')
        # driver.find_elements(By.XPATH, '//span[@data-qa="vacancy-salary-compensation-type-net"]')
        if len(salaries) < 1:
            salaries = wait_elements(driver, value='//span[@data-qa="vacancy-salary-compensation-type-gross"]')
            # driver.find_elements(By.XPATH, '//span[@data-qa="vacancy-salary-compensation-type-gross"]')
            salary = salaries[0].text if len(salaries) > 0 else ""
        else:
            salary = salaries[0].text
        if currency is not None and currency not in salary:
            continue
        cities = wait_elements(driver, value='//p[@data-qa="vacancy-view-location"]')
        # driver.find_elements(By.XPATH, '//p[@data-qa="vacancy-view-location"]')
        if len(cities) < 1:
            cities = wait_elements(driver, value='//span[@data-qa="vacancy-view-raw-address"]')
            # driver.find_elements(By.XPATH, '//span[@data-qa="vacancy-view-raw-address"]')
            parts = cities[0].text.split(',')
            city = parts[0]
        else:
            city = cities[0].text
        companies = wait_elements(driver, value='//span[@data-qa="bloko-header-2"]')
        # driver.find_elements(By.XPATH, '//span[@data-qa="bloko-header-2"]')
        company = companies[0].text
        parse_dict.append({
            'company': company,
            'city': city,
            'salary': salary,
            'link': item
        })
    return parse_dict


if __name__ == '__main__':
    vacancies = []
    page_count = 3
    for page in range(0, page_count):
        print(f'Обрабатывается страница: {page + 1}/{page_count}')
        links = get_links(page)
        if links is None:
            continue
        vacancies.extend(get_data(links))  # , '$'))

    print('Общее количество найденных вакансий:', len(vacancies))
    json_object = json.dumps(vacancies, ensure_ascii=False, indent=4)
    with open("vacancies.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_object)
    print('Данные записаны в файл.')
    driver.close()
