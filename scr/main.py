# main.py
from api_client import HH
from storage import JSONStorage
from vacancy import Vacancy  # Теперь импорт из vacancy.py


def get_user_input(prompt, convert_func=str):
    """Функция для безопасного получения ввода пользователя"""
    while True:
        user_input = input(prompt).strip()
        try:
            return convert_func(user_input)
        except ValueError:
            print("Некорректный ввод. Попробуйте ещё раз.")


def search_vacancies():
    """Основная функция для поиска и обработки вакансий"""
    hh = HH()

    # Запрос ключевого слова у пользователя
    keyword = input("Введите ключевое слово для поиска вакансий: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return

    print("\nЗагружаем вакансии...")
    hh.load_vacancies(keyword)

    if not hh.vacancies:
        print("По вашему запросу вакансий не найдено.")
        return

    # Преобразуем вакансии в объекты Vacancy
    vacancy_objects = []
    for item in hh.vacancies:
        vacancy = Vacancy(
            title=item.get("name", "Без названия"),
            link=item.get("alternate_url", "#"),
            salary=Vacancy.parse_salary(item.get("salary")),
            description=item.get("snippet", {}).get("responsibility", "Описание отсутствует"),
            company=item.get("employer", {}).get("name", "Не указана"),
            city=item.get("area", {}).get("name", "Не указан"),
            experience=item.get("experience", {}).get("name", "Не указан"),
        )
        vacancy_objects.append(vacancy)

    print(f"Загружено {len(vacancy_objects)} вакансий.")

    # Сохранение в JSON
    with JSONStorage("vacancies.json") as storage:
        for vac in vacancy_objects:
            storage.add_vacancy(vac.__dict__)

    # Запрос у пользователя количества топ N вакансий по зарплате
    top_n = get_user_input("\nСколько топ-вакансий по зарплате вывести? ", int)
    sorted_vacancies = sorted(vacancy_objects, key=lambda v: v.salary if isinstance(v.salary, (int, float)) else 0,
                              reverse=True)
    top_vacancies = sorted_vacancies[:top_n]

    # Сохранение топ вакансий в JSON
    with JSONStorage("vacancies.json") as storage:
        for vac in top_vacancies:
            vacancy_dict = {
                "name": vac.title,
                "alternate_url": vac.link,
                "salary": vac.salary,
                "description": vac.description,
                "company": vac.company,
                "city": vac.city,
                "experience": vac.experience
            }
            storage.add_vacancy(vacancy_dict)

    print(f"\nТоп-{top_n} вакансий по зарплате:")
    for vac in sorted_vacancies[:top_n]:
        print(vac, "\n" + "-" * 50)

    # Фильтрация вакансий по ключевому слову в описании
    keyword_desc = input("\nВведите ключевое слово для поиска в описании вакансий: ").strip().lower()
    filtered_vacancies = [v for v in vacancy_objects if v.description and keyword_desc in v.description.lower()]

    if filtered_vacancies:
        print(f"\nНайдено {len(filtered_vacancies)} вакансий с ключевым словом '{keyword_desc}' в описании:")
        for vac in filtered_vacancies:
            print(vac, "\n" + "-" * 50)
    else:
        print(f"\nВакансий с ключевым словом '{keyword_desc}' не найдено.")


if __name__ == "__main__":
    search_vacancies()
