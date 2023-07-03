import psycopg2


class DBManager:
    """
    Класс для работы с базой данных
    """

    @staticmethod
    def create_database(database_name, params):
        """
        Создание базы данных
        :param database_name: Наименование базы данных
        :param params: параметры из database.ini
        """
        conn = psycopg2.connect(dbname="postgres", **params)
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"DROP DATABASE {database_name}")
        except psycopg2.errors.InvalidCatalogName:
            cur.execute(f"CREATE DATABASE {database_name}")
        else:
            cur.execute(f"CREATE DATABASE {database_name}")
        conn.close()

        conn = psycopg2.connect(dbname=database_name, **params)

        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE employers (
                            employer_id SERIAL PRIMARY KEY,
                            employer_name VARCHAR(255) NOT NULL,
                            open_vacancies INTEGER,
                            trusted BOOLEAN,
                            town VARCHAR(255),
                            description TEXT
                        )
                    """)

        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE vacancies (
                            vacancy_id SERIAL,
                            vacancy_name VARCHAR(255),
                            employer_id INTEGER REFERENCES employers(employer_id),
                            experience VARCHAR(255),
                            salary_сurrency VARCHAR(255),
                            salary_from INTEGER,
                            salary_to INTEGER,
                            town VARCHAR(255),
                            published_at TIMESTAMP,
                            vacancy_url TEXT,
                            description TEXT
                        )
                    """)

        conn.commit()
        conn.close()

    @staticmethod
    def save_data_to_db(data, db_name, params):
        """
        Метод для сохранения информации в базу данных
        :param data: исходные данные list[dict]
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            for employer in data:
                employer_data = employer['employer']
                cur.execute(
                    """
                    INSERT INTO employers (employer_id, employer_name, open_vacancies, trusted, town, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (employer_data['id'], employer_data['name'], employer_data['open_vacancies'],
                     employer_data['trusted'], employer_data['area']['name'], employer_data['description'])
                )

                vacancy_data = employer['vacancies']
                try:
                    for vacancy in vacancy_data:
                        cur.execute(
                            """
                            INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, experience, salary_сurrency, 
                                        salary_from, salary_to, town, published_at, vacancy_url, description)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (vacancy['id'], vacancy['name'], vacancy['employer']['id'],
                             vacancy['experience']['name'], vacancy['salary']['currency'], vacancy['salary']['from'],
                             vacancy['salary']['to'], vacancy['area']['name'], vacancy['published_at'],
                             vacancy['alternate_url'],
                             vacancy['snippet']['responsibility'])
                        )
                except Exception:
                    for vacancy in vacancy_data:
                        cur.execute(
                            """
                            INSERT INTO vacancies (vacancy_id, vacancy_name, employer_id, experience, salary_сurrency, 
                                        salary_from, salary_to, town, published_at, vacancy_url, description)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (vacancy['id'], vacancy['name'], vacancy['employer']['id'],
                             vacancy['experience']['name'], None, None, None, vacancy['area']['name'],
                             vacancy['published_at'],
                             vacancy['alternate_url'], vacancy['snippet']['responsibility']))

            conn.commit()
            conn.close()

    @classmethod
    def get_companies_and_vacancies_count(cls, db_name, params):
        """
        Получает список всех компаний и количество вакансий у каждой компании
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT employer_name, COUNT(*) FROM vacancies
                           RIGHT JOIN employers
                           USING(employer_id)
                           GROUP BY employer_name""")
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    @classmethod
    def get_all_vacancies(cls, db_name, params):
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT employer_name, vacancy_name, vacancy_url, CONCAT(salary_from, '-', salary_to, ' ', salary_сurrency) as salary 
                           FROM vacancies
                           JOIN employers USING(employer_id) """)
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    @classmethod
    def get_avg_salary(cls, db_name, params):
        """
        Получает среднюю зарплату по вакансиям
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT AVG(salary_from) as avg_salary
                           FROM vacancies
                           JOIN employers USING(employer_id)""")
            data = cur.fetchone()
        conn.commit()
        conn.close()
        return data

    @classmethod
    def get_vacancies_with_higher_salary(cls, db_name, params):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM vacancies WHERE salary_to > (
                           SELECT AVG(salary_from)
                           FROM vacancies
                           JOIN employers USING(employer_id))""")
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data

    @classmethod
    def get_vacancies_with_keyword(cls, db_name, params, keyword):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например “python”
        :param db_name: название базы данных
        :param params: параметры из файла database.ini
        :param keyword: ключевое слово для поиска
        """
        conn = psycopg2.connect(dbname=db_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM vacancies
                WHERE vacancy_name LIKE %s OR description LIKE %s""", (f"%{keyword}%)", "%{keyword}%)"))
            data = cur.fetchall()
        conn.commit()
        conn.close()
        return data
