import json
import requests


class HeadHunter:
    """
    Класс для работы с API HeadHunter
    """
    @staticmethod
    def get_employers(employers_id: int):
        """
        Получает по API информацию о конкретном работодателе
        :param employers_id: id работодателя
        :return: json форматированная информация о работодателе
        """
        params = {
            "only_with_vacancies": True,
            "per_page": 100
        }
        response = requests.get(f"https://api.hh.ru/employers/{employers_id}", params=params)
        return response.json()

    @staticmethod
    def get_vacancies(page: int, employer_id: int):
        """
        Получает по API вакансии конкретного работодателя
        :param page: страница для итерации
        :param employer_id: id работодателя
        :return: ответ по API по списку вакансий
        """
        params = {
            "page": page,
            "per_page": 100
        }
        response = requests.get(f"https://api.hh.ru/vacancies?employer_id={employer_id}", params=params)
        response.close()
        return response.content

    @staticmethod
    def json_vacancies(employer_id: int):
        """
        Получение нужных вакансий в формате списка словарей Python - работа с JSON
        :param employer_id: id работодателя
        :return: список вакансий list[dict]
        """
        js_list = []

        for page in range(0, 20):
            js_obj = json.loads(HeadHunter.get_vacancies(page, employer_id))
            js_list.extend(js_obj['items'])
            if js_obj['pages'] - page <= 1:
                break
        return js_list

    @staticmethod
    def employers_vacancies_unite_data(employer_data, vacancies_data):
        """
        Объединяет информацию о работодателе и его вакансиях в один словарь
        :param employer_data: информация о работодателе
        :param vacancies_data: информация о вакансии
        :return:
        """
        return {'employer': employer_data,
                'vacancies': vacancies_data}

    @staticmethod
    def parsed_united_data(employer_id: dict):
        """
        Объединяет информацию о работодателе и вакансиях по списку работодателей
        :param employer_id: dict с id работодателя
        :return:
        """
        all_vacancies_by_employer = []

        for k, v in employer_id.items():
            employer_data = HeadHunter.get_employers(v)
            vacancy_data = HeadHunter.json_vacancies(v)
            united_data = HeadHunter.employers_vacancies_unite_data(employer_data, vacancy_data)
            all_vacancies_by_employer.append(united_data)

        return all_vacancies_by_employer
