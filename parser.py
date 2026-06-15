import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

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

    response.encoding = "utf-8"
    return response.text

def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for card in soup.select("article.product_pod"):
        title = card.h3.a["title"]

        price_text = card.select_one("p.price_color").get_text(strip=True)
        price = float(price_text.lstrip("£"))

        rating_class = card.select_one("p.star-rating")["class"]
        rating = RATING_MAP.get(rating_class[1], 0)

        in_stock = "In stock" in card.select_one("p.instock").get_text()

        books.append(
            {
                "Название": title,
                "Цена, £": price,
                "Рейтинг (1-5)": rating,
                "В наличии": "да" if in_stock else "нет",
            }
        )
    return books

def main():
    html = fetch_page(1)
    if html is None:
        print("Не удалось скачат страницу.")
        sys.exit(1)

    books = parse_page(html)
    print(f"Найдено книг на странице: {len(books)}\n")
    for book in books[:5]:
        print(book)

if __name__ == "__main__":
    main()
