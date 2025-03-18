# storage.py
import json
import os
from abc import ABC, abstractmethod


class Storage(ABC):
    """Абстрактный класс для хранилища вакансий."""
    @abstractmethod
    def add_vacancy(self, vacancy):
        """Добавляет вакансию в хранилище"""
        pass

    @abstractmethod
    def get_vacancies(self, criteria):
        """Возвращает список вакансий, соответствующих критериям"""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id):
        """Удаляет вакансию по её идентификатору"""
        pass


class JSONStorage(Storage):
    """Класс для работы с JSON-файлом как хранилищем вакансий."""

    def __init__(self, filename="vacancies.json"):
        """Инициализирует JSON-хранилище, создавая файл при необходимости."""
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_dir)
        data_dir = os.path.join(parent_dir, 'data')

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        self.filename = os.path.join(data_dir, filename)

        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([], file)

    def add_vacancy(self, vacancy):
        """Добавляет вакансию в JSON-файл, избегая дублирования"""
        if not vacancy.get("name") or not vacancy.get("alternate_url"):
            return

        try:
            with open(self.filename, 'r+', encoding='utf-8') as file:
                vacancies = json.load(file)

                # Проверяем, есть ли такая вакансия уже в файле
                if any(v.get("name") == vacancy["name"] and v.get("company") == vacancy["company"] and v.get("city") ==
                       vacancy["city"] for v in vacancies):
                    return

                vacancies.append(vacancy)
                file.seek(0)
                json.dump(vacancies, file, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, FileNotFoundError):
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([vacancy], file, ensure_ascii=False, indent=4)

    def get_vacancies(self, criteria):
        """Возвращает список вакансий, соответствующих критериям"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                vacancies = json.load(file)
            except json.JSONDecodeError:
                return []

        def matches(vacancy):
            for key, value in criteria.items():
                if key.startswith("salary_"):
                    if not isinstance(vacancy.get("salary"), dict):
                        return False
                    if key == "salary_from" and vacancy["salary"].get("from", 0) < value:
                        return False
                    if key == "salary_to" and vacancy["salary"].get("to", float('inf')) > value:
                        return False
                elif vacancy.get(key) != value:
                    return False
            return True

        return [v for v in vacancies if matches(v)]

    def delete_vacancy(self, vacancy_id):
        """Удаляет вакансию из JSON-файла"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            try:
                vacancies = json.load(file)
            except json.JSONDecodeError:
                vacancies = []

        vacancies = [vacancy for vacancy in vacancies if vacancy.get('id') != vacancy_id]

        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies, file, ensure_ascii=False, indent=4)

    def __enter__(self):
        """Добавление поддержки контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
