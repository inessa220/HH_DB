from src.api import HHAPI
from src.db import DBManager
from src.saver import save_companies_to_file, connection
from contextlib import suppress


def create_tables(db_manager: DBManager) -> None:
    """Создает базу данных и таблицы"""
    db_manager.create_database()
    db_manager.create_tables()


def load_data(db_manager: DBManager) -> None:
    """Загружает данные о компаниях и вакансиях из API и сохраняет их в базу данных"""
    companies_file = "data/companies.json"
    hh_api = HHAPI()
    company_ids = [1740, 80, 78638, 3529, 4181, 1455, 2748, 208707, 15478, 3388]
    companies = []
    for company_id in company_ids:
        company = hh_api.get_company(company_id)
        if company:
            companies.append(company)
    save_companies_to_file(companies, companies_file)
    print("Компании загружены из API и сохранены в файл.")

    db_manager.save_companies(companies)
    for company in companies:
        vacancies = hh_api.get_vacancies(company["id"])
        db_manager.save_vacancies(vacancies, company["id"])


def user_interaction(db_manager: DBManager) -> None:
    """Взаимодействие с пользователем для выполнения различных действий"""
    while True:
        print("\nВыберите действие:")
        print("1 - Получить список компаний и количество вакансий у каждой компании")
        print("2 - Получить список всех вакансий")
        print("3 - Получить среднюю зарплату по вакансиям")
        print("4 - Получить список вакансий с зарплатой выше средней")
        print("5 - Получить список вакансий, содержащих ключевое слово")
        print("0 - Выход")

        choice = input("\nВаш выбор: ")

        if choice == "1":
            companies_vacancies = db_manager.get_companies_and_vacancies_count()
            if companies_vacancies:
                for company, count in companies_vacancies.items():
                    print(f"{company}: {count} вакансий")
            else:
                print("Нет данных о компаниях и вакансиях.")

        elif choice == "2":
            all_vacancies = db_manager.get_all_vacancies()
            if all_vacancies:
                for vacancy in all_vacancies:
                    print(
                        f"Компания: {vacancy[0]}, Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Ссылка: {vacancy[3]}"
                    )
            else:
                print("Нет данных о вакансиях.")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата: {avg_salary}")

        elif choice == "4":
            higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
            if higher_salary_vacancies:
                for vacancy in higher_salary_vacancies:
                    print(
                        f"Компания: {vacancy[0]}, Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Ссылка: {vacancy[3]}"
                    )
            else:
                print("Нет вакансий с зарплатой выше средней.")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска вакансий: ")
            keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            if keyword_vacancies:
                for vacancy in keyword_vacancies:
                    print(
                        f"Компания: {vacancy[0]}, Вакансия: {vacancy[1]}, Зарплата: {vacancy[2]}, Ссылка: {vacancy[3]}"
                    )
            else:
                print(f"Нет вакансий, содержащих ключевое слово {keyword!r}.")

        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")


def main() -> None:
    """
    Основная функция для взаимодействия с пользователем.
    """
    db_config = connection()
    db_name = "hh_database"
    db_manager = DBManager(db_name, db_config)
    create_tables(db_manager)
    load_data(db_manager)

    with suppress(KeyboardInterrupt):
        user_interaction(db_manager)


if __name__ == "__main__":
    main()
