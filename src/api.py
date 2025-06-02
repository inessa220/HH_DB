import requests


class HHAPI:
    """Класс взаимодействия с API"""

    def __init__(self):
        self.base_url = "https://api.hh.ru/"
        self.user_agent = {"User-Agent": "HH-User-Agent"}

    def get_company(self, company_id: int) -> dict:
        """Получает информацию о компании"""
        try:
            response = requests.get(f"{self.base_url}employers/{company_id}", headers=self.user_agent)
            response.raise_for_status()
            data = response.json()
            return {"id": data["id"], "name": data["name"], "url": data["alternate_url"]}
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных: {e}")
            return {}

    def get_vacancies(self, company_id: int) -> list:
        """Получает список вакансий"""
        vacancies = []
        area = 1481
        page = 0
        per_page = 100
        all_pages_loaded = False

        while not all_pages_loaded:
            try:
                params = {
                    "employer_id": company_id,
                    "page": page,
                    "per_page": per_page,
                    "area": area,
                    "only_with_salary": True,
                }
                response = requests.get(f"{self.base_url}vacancies", headers=self.user_agent, params=params)
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])
                if not items:
                    all_pages_loaded = True
                    continue
                for item in items:
                    vacancies.append(
                        {
                            "name": item["name"],
                            "salary_from": item["salary"]["from"],
                            "salary_to": item["salary"]["to"],
                            "url": item["alternate_url"],
                            "description": item.get("snippet", {}).get("responsibility", ""),
                        }
                    )
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении данных: {e}")
                break
        return vacancies
