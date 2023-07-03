DROP DATABASE 'headhunter'
CREATE DATABASE 'headhunter'

CREATE TABLE employers ( employer_id SERIAL PRIMARY KEY,
                            employer_name VARCHAR(255) NOT NULL,
                            open_vacancies INTEGER,
                            trusted BOOLEAN,
                            town VARCHAR(255),
                            description TEXT)

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
                            description TEXT)


