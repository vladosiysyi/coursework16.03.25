import pytest
from unittest.mock import patch, Mock
from scr.api_client import HH
from scr.vacancy import Vacancy
from scr.storage import JSONStorage
import tempfile
import json


@pytest.fixture
def test_json_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_file.write(b'[]')
        temp_file.close()
        yield temp_file.name


@pytest.fixture
def test_vacancy():
    return Vacancy(
        title="Python Developer",
        link="https://example.com",
        salary="100000 - 150000 RUB",
        description="Development of web applications",
        company="Test Company",
        city="Moscow",
        experience="3-5 years"
    )


def test_add_and_get_vacancy(test_json_file, test_vacancy):
    storage = JSONStorage(test_json_file)
    storage.add_vacancy(test_vacancy.__dict__)
    vacancies = storage.get_vacancies({"title": "Python Developer"})
    assert len(vacancies) == 0


def test_delete_vacancy(test_json_file, test_vacancy):
    storage = JSONStorage(test_json_file)
    vacancy_data = test_vacancy.__dict__
    vacancy_data['id'] = 1
    storage.add_vacancy(vacancy_data)
    storage.delete_vacancy(1)
    vacancies = storage.get_vacancies({})
    assert len(vacancies) == 0


def test_vacancy_post_init():
    with pytest.raises(ValueError):
        Vacancy(title="", link="https://example.com", salary="", description="")

    with pytest.raises(ValueError):
        Vacancy(title="Python Developer", link="", salary="", description="")


def test_load_vacancies():
    mock_response = {'items': [{'name': 'Python Developer', 'alternate_url': 'https://example.com',
                                'salary': {'from': 100000, 'to': 150000, 'currency': 'RUB'}}]}
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = mock_response
        hh = HH()
        hh.load_vacancies("Python")
        assert len(hh.vacancies) == 20


def test_parse_salary():
    assert Vacancy.parse_salary({'from': 100000, 'to': 150000, 'currency': 'RUB'}) == "100000 - 150000 RUB"
    assert Vacancy.parse_salary({}) == "Не указано - Не указано"
    assert Vacancy.parse_salary(None) == "Зарплата не указана"


def test_context_manager(test_json_file):
    with JSONStorage(test_json_file) as storage:
        storage.add_vacancy({"name": "Python Developer", "alternate_url": "https://example.com"})
    with open(test_json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    assert len(data) == 1
