# api_client.py
from dataclasses import dataclass
import requests
import time
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)


class Parser(ABC):
    @abstractmethod
    def load_vacancies(self, keyword):
        pass


class HH(Parser):
    """
    Класс для работы с API HeadHunter
    """

    def __init__(self):
        self.url = 'https://api.hh.ru/vacancies'
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'text': '', 'page': 0, 'per_page': 100}
        self.vacancies = []

    def load_vacancies(self, keyword):
        self.params['text'] = keyword
        self.params['page'] = 0
        while self.params['page'] < 20:
            try:
                response = requests.get(self.url, headers=self.headers, params=self.params)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('items'):
                        break  # Если вакансий нет, прерываем цикл
                    self.vacancies.extend(data['items'])
                    logging.info(f"Загружена страница {self.params['page']} ({len(data['items'])} вакансий)")
                    self.params['page'] += 1
                    time.sleep(0.5)  # Задержка для предотвращения блокировки API
                else:
                    logging.error(f"Ошибка {response.status_code}: {response.text}")
                    break
            except requests.RequestException as e:
                logging.error(f"Ошибка запроса: {e}")
                break


@dataclass
class Vacancy:
    title: str
    link: str
    salary: str
    description: str
    company: str = "Не указана"
    city: str = "Не указан"
    experience: str = "Не указан"

    def __post_init__(self):
        if not self.title:
            raise ValueError("Название вакансии не может быть пустым.")
        if not self.link:
            raise ValueError("Ссылка на вакансию не может быть пустой.")

    @staticmethod
    def parse_salary(salary):
        """Обрабатывает зарплату из API HH"""
        if isinstance(salary, dict):
            salary_from = salary.get('from', 'Не указано')
            salary_to = salary.get('to', 'Не указано')
            currency = salary.get('currency', '')
            return f"{salary_from} - {salary_to} {currency}".strip()
        return salary if salary else "Зарплата не указана"

    def __lt__(self, other):
        """Сравнение вакансий по зарплате (меньше)"""
        if not isinstance(self.salary, (int, float)) or not isinstance(other.salary, (int, float)):
            return False
        return self.salary < other.salary

    def __gt__(self, other):
        """Сравнение вакансий по зарплате (больше)"""
        if not isinstance(self.salary, (int, float)) or not isinstance(other.salary, (int, float)):
            return False
        return self.salary > other.salary

    def __eq__(self, other):
        """Сравнение вакансий по зарплате (равно)"""
        if not isinstance(self.salary, (int, float)) or not isinstance(other.salary, (int, float)):
            return False
        return self.salary == other.salary

    def __str__(self):
        return (f"Название: {self.title}\n"
                f"Ссылка: {self.link}\n"
                f"Зарплата: {self.salary}\n"
                f"Описание: {self.description[:100] + '...' if self.description else 'Описание отсутствует'}\n")

    # def __repr__(self):
    #     """
    #     Представление объекта вакансии в виде строки.
    #     :return: Строковое представление вакансии.
    #     """
    #     return (f"Vacancy(title={self.title}, link={self.link}, "
    #             f"salary={self.salary}, description={self.description})")
    #
# if __name__ == "__main__":
#     # Создаем несколько вакансий
#     vacancy1 = Vacancy("Python Developer", "http://example.com/python", 120000, "Опыт работы от 3 лет.")
#     vacancy2 = Vacancy("Java Developer", "http://example.com/java", 100000, "Опыт работы от 2 лет.")
#     vacancy3 = Vacancy("Data Scientist", "http://example.com/data", "Зарплата не указана", "Знание Python и SQL.")
#
#     # Сравниваем вакансии по зарплате
#     print(f"Python Developer > Java Developer: {vacancy1 > vacancy2}")  # True
#     print(f"Java Developer < Python Developer: {vacancy2 < vacancy1}")  # True
#     print(f"Data Scientist == Python Developer: {vacancy3 == vacancy1}")  # False
#
#     # Выводим информацию о вакансиях
#     print(vacancy1)
#     print(vacancy2)
#     print(vacancy3)
