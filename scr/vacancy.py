# vacancy.py
from dataclasses import dataclass

@dataclass
class Vacancy:
    """Класс для представления вакансии."""

    title: str
    link: str
    salary: str
    description: str
    company: str = "Не указана"
    city: str = "Не указан"
    experience: str = "Не указан"

    def __post_init__(self):
        """Валидация данных после инициализации."""

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
        """Возвращает строковое представление вакансии."""

        return (f"Название: {self.title}\n"
                f"Ссылка: {self.link}\n"
                f"Зарплата: {self.salary}\n"
                f"Описание: {self.description[:100] + '...' if self.description else 'Описание отсутствует'}\n")
