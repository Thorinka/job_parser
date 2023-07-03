from config import config
from src.database import DBManager
from pprint import pprint
from src.headhunter import HeadHunter


def main():
    employers_id = {
        "Ostrovok.ru": 697715,
        "Webtronics": 5843588,
        "ООО СФЕРА": 4402893,
        "SL KG": 9472269,
        "Convergent": 57862,
        "Mindbox": 205152,
        "Звук": 1829949,
        "Пикассо": 737268,
        "Eqvanta": 3785152,
        "B.ART": 9352347
    }
    params = config()

    all_vacancies = HeadHunter.parsed_united_data(employers_id)
    DBManager.create_database('headhunter', params)
    DBManager.save_data_to_db(all_vacancies, 'headhunter', params)

    pprint(DBManager.get_companies_and_vacancies_count('headhunter', params))
    pprint(DBManager.get_all_vacancies('headhunter', params))
    pprint(DBManager.get_avg_salary('headhunter', params))
    pprint(DBManager.get_vacancies_with_higher_salary('headhunter', params))
    pprint(DBManager.get_vacancies_with_keyword('headhunter', params, "Python"))


if __name__ == '__main__':
    main()
