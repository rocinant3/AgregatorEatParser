import requests



def build_url(code: str):
    return f"https://tender-cache-api.agregatoreat.ru/api/TradeLot/{code}"


codes = ["e1e11762-58a0-486f-831c-9aa099c0e977", "f35f0b56-e2dc-4cc1-9ce7-2ca55af724c4"]

for code in codes:
    response =requests.get(build_url(code))
    print(response.status_code)