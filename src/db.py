from typing import Any, Dict, List
import psycopg2


class DBManager:
    """Класс для управления базой данных"""
    def __init__(self, db_name: str, db_config: dict):
        self.db_name = db_name
        self.db_config = db_config
        self.conn = None
        self._connect()

    def _connect(self) -> None:
        """Устанавливает соединение с базой данных."""
        try:
            self.conn = psycopg2.connect(dbname=self.db_name, **self.db_config)
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def __del__(self) -> None:
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()

    def create_database(self) -> None:
        """Создает базу данных"""
        conn = None
        try:
            conn = psycopg2.connect(dbname="template1", **self.db_config)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{self.db_name}'")
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {self.db_name}")
        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
        finally:
            if conn:
                conn.close()

    def create_tables(self) -> None:
        """Создает таблицы в базе данных"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
            return
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS employers (
                        employer_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url VARCHAR(255)
                    )
                """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies (
                        vacancy_id SERIAL PRIMARY KEY,
                        employer_id INT REFERENCES employers(employer_id),
                        name VARCHAR(255) NOT NULL,
                        salary_from INT,
                        salary_to INT,
                        url VARCHAR(255),
                        description TEXT
                    )
                """
                )
                self.conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    def save_companies(self, companies: List[Dict[str, Any]]) -> None:
        """Сохраняет данные о компаниях"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
            return
        try:
            with self.conn.cursor() as cur:
                for company in companies:
                    try:
                        cur.execute(
                            """
                            INSERT INTO employers (employer_id, name, url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (employer_id) DO NOTHING
                        """,
                            (company["id"], company["name"], company["url"]),
                        )
                    except psycopg2.Error as e:
                        print(f"Ошибка при вставке компании {company['name']}: {e}")
                self.conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def save_vacancies(self, vacancies: List[Dict[str, Any]], employer_id: int) -> None:
        """Сохраняет данные о вакансиях"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
            return
        try:
            with self.conn.cursor() as cur:
                for vacancy in vacancies:
                    try:
                        cur.execute(
                            """
                            INSERT INTO vacancies (employer_id, name, salary_from, salary_to, url, description)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                            (
                                employer_id,
                                vacancy["name"],
                                vacancy["salary_from"],
                                vacancy["salary_to"],
                                vacancy["url"],
                                vacancy["description"],
                            ),
                        )
                    except psycopg2.Error as e:
                        print(f"Ошибка при вставке вакансии {vacancy['name']}: {e}")
                self.conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных или выполнении запроса: {e}")

    def get_companies_and_vacancies_count(self) -> Dict[str, int]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
            return {}
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT employers.name, COUNT(vacancies.vacancy_id)
                    FROM employers
                    LEFT JOIN vacancies ON employers.employer_id = vacancies.employer_id
                    GROUP BY employers.name
                    ORDER BY employers.name
                """
                )
                results = cur.fetchall()
                return {company: count for company, count in results}
        except psycopg2.Error:
            return {}

    def get_all_vacancies(self) -> List[Any]:
        """Получает список всех вакансий с указанием названий компании, вакансии, зарплаты и ссылки на вакансию"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
            return []
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.url
                    FROM vacancies
                    JOIN employers ON vacancies.employer_id = employers.employer_id
                """
                )
                return cur.fetchall()
        except psycopg2.Error:
            return []

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям"""
        if self.conn is None:
            print("Соединение с базой данных не установлено")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT AVG(salary_from)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL
                """
                )
                result = cur.fetchone()
                return result[0] if result[0] is not None else 0.0
        except psycopg2.Error:
            return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Any]:
        """Получает список всех вакансий, у которых зарплата выше средней"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
        try:
            with self.conn.cursor() as cur:
                cur.execute("""SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.url
                   FROM vacancies
                   JOIN employers ON vacancies.employer_id = employers.employer_id
                   WHERE vacancies.salary_from > (SELECT AVG(salary_from)
                   FROM vacancies WHERE salary_from IS NOT NULL)""")
                return cur.fetchall()
        except psycopg2.Error:
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Any]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        if self.conn is None:
            print("Соединение с базой данных не установлено.")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT employers.name, vacancies.name, vacancies.salary_from, vacancies.url
                    FROM vacancies
                    JOIN employers ON vacancies.employer_id = employers.employer_id
                    WHERE vacancies.name LIKE %s
                """,
                    ("%" + keyword + "%",),
                )
                return cur.fetchall()
        except psycopg2.Error:
            return []
