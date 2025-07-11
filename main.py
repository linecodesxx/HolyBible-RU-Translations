import re
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


filename = ""
translation = ""

driver = webdriver.Firefox()
driver.get(f"https://bible.by/{translation}")
time.sleep(5)

# Список книг
allbooks = driver.find_element(By.CLASS_NAME, "listing-main")
book_divs = allbooks.find_elements(By.TAG_NAME, "div")

# Собираем ссылки и имена книг
books_info = []
for div in book_divs:
    a_tag = div.find_element(By.TAG_NAME, "a")
    book_name = a_tag.text.strip()
    book_href = a_tag.get_attribute("href")
    books_info.append((book_name, book_href))

# Основной JSON-объект
bible_data = {
    "Translation": f"{translation.upper}",
    "Books": []
}

book_id = 1

for book_name, book_link in books_info:
    print(f"📖 Обрабатываем книгу {book_id}: {book_name}")
    book_obj = {
        "BookId": book_id,
        "BookName": book_name,
        "Chapters": []
    }
    book_id += 1

    # Пример: https://bible.by/nrt/43/1/ → book_num = 43
    parts = book_link.rstrip("/").split("/")
    book_num = parts[-2]

    chapter_num = 1
    while True:
        chapter_link = f"https://bible.by/{translation}/{book_num}/{chapter_num}/"
        driver.get(chapter_link)
        time.sleep(2)

        try:
            text_block = driver.find_element(By.CLASS_NAME, "text")
            verse_divs = text_block.find_elements(By.TAG_NAME, "div")
            if not verse_divs:
                break
        except NoSuchElementException:
            break

        chapter_obj = {
            "ChapterId": chapter_num,
            "Verses": []
        }

        for div in verse_divs:
            try:
                ver_id = div.find_element(By.TAG_NAME, "sup").find_element(By.TAG_NAME, "a").text
                ver_text = re.sub(r'^\d+\s+', '', div.text).strip()

                if ver_id.isdigit():
                    verse_obj = {
                        "VerseId": int(ver_id),
                        "Text": ver_text
                    }
                    chapter_obj["Verses"].append(verse_obj)
            except NoSuchElementException:
                continue

        book_obj["Chapters"].append(chapter_obj)
        print(f"✅ Глава {chapter_num} книги {book_name} собрана")
        chapter_num += 1

    bible_data["Books"].append(book_obj)
    print(f"✅ Завершена книга: {book_name} ({book_id - 1})\n")

driver.quit()

# Сохраняем в файл
with open(f"{filename}.json", "w", encoding="utf-8") as f:
    json.dump(bible_data, f, ensure_ascii=False, indent=2)

print(f"✅ Готово! Сохранено в {filename}.json")
