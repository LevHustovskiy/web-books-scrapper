import requests

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(page_number: int) -> str | None:
    url = BASE_URL.format(page_number)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as exc:
        print(f"[!] Ошибка сети на странице {page_number}: {exc}")
        return None

    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.text

def main():
    html = fetch_page(1)
    print(f"Скачано {len(html)} символов")

if __name__ == "__main__":
    main()
