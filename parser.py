import sys
import csv
import time

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

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

def save_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def save_excel(rows: list[dict], path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Книги"

    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append(list(row.values()))

    widths = [60, 12, 14, 12]
    for col, width in zip("ABCD", widths):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A2"

    wb.save(path)

def main() -> None:
    all_books: list[dict] = []

    for page in range(1, 51):
        html = fetch_page(page)
        if html is None:
            break

        books = parse_page(html)
        all_books.extend(books)
        print(f"Страница {page}: собрано {len(books)} книг (всего {len(all_books)})")

        time.sleep(0.5)

    if not all_books:
        print("Не удалось собрать ни одной записи.")
        sys.exit(1)

    save_csv(all_books, "books.csv")
    save_excel(all_books, "books.xlsx")
    print(f"\nГотово: {len(all_books)} книг сохранено в books.csv и books.xlsx")

if __name__ == "__main__":
    main()
