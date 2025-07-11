import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

filename = ""
translation = ""

driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)  # ждём до 10 секунд

# Загружаем существующий JSON
with open(f"{filename}.json", "r", encoding="utf-8") as f:
    bible_data = json.load(f)

existing_ids = {book["BookId"] for book in bible_data["Books"]}

old_testament_names = [
    "Бытие", "Исход", "Левит", "Числа", "Второзаконие",
    "Иисус Навин", "Судьи", "Руфь", "1 Царств", "2 Царств",
    "3 Царств", "4 Царств", "1 Паралипоменон", "2 Паралипоменон",
    "Ездра", "Неемия", "Есфирь", "Иов", "Псалтирь",
    "Притчи", "Екклесиаст", "Песня Песней", "Исаия", "Иеремия",
    "Плач Иеремии", "Иезекииль", "Даниил", "Осия", "Иоиль",
    "Амос", "Авдий", "Иона", "Михей", "Наум",
    "Аввакум", "Софония", "Аггей", "Захария", "Малахия"
]

start_book_id_for_json = 28  # нумерация в JSON с 28

for real_book_id in range(1, 40):
    json_book_id = start_book_id_for_json + real_book_id - 1
    book_name = old_testament_names[real_book_id - 1]

    if json_book_id in existing_ids:
        print(f"⏭ Книга с JSON BookId {json_book_id} уже есть — пропускаем")
        continue

    print(f"📘 Парсим книгу {real_book_id} ({book_name}) с JSON BookId {json_book_id}")

    book_obj = {
        "BookId": json_book_id,
        "BookName": book_name,
        "Chapters": []
    }

    chapter_id = 1
    while True:
        url = f"https://bible.by/{translation}/{real_book_id}/{chapter_id}/"
        driver.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "text")))
        except TimeoutException:
            print(f"❌ Глава {chapter_id} не найдена, выходим")
            break

        try:
            text_block = driver.find_element(By.CLASS_NAME, "text")
            verse_divs = text_block.find_elements(By.TAG_NAME, "div")
            if not verse_divs:
                print(f"❌ Пустая глава {chapter_id}, выходим")
                break
        except NoSuchElementException:
            print(f"❌ Ошибка поиска стихов в главе {chapter_id}, выходим")
            break

        chapter_obj = {
            "ChapterId": chapter_id,
            "Verses": []
        }

        for div in verse_divs:
            try:
                ver_id = div.find_element(By.TAG_NAME, "sup").find_element(By.TAG_NAME, "a").text
                ver_text = re.sub(r'^\d+\s+', '', div.text).strip()
                if ver_id.isdigit():
                    chapter_obj["Verses"].append({
                        "VerseId": int(ver_id),
                        "Text": ver_text
                    })
            except NoSuchElementException:
                continue

        book_obj["Chapters"].append(chapter_obj)
        print(f"✅ Глава {chapter_id} книги {book_name} собрана")
        chapter_id += 1

    if book_obj["Chapters"]:
        bible_data["Books"].append(book_obj)
        print(f"✅ Книга {book_name} с JSON BookId {json_book_id} добавлена\n")
    else:
        print(f"⏭ Книга {book_name} не содержит глав — пропущена\n")

driver.quit()

with open(f"filename.json", "w", encoding="utf-8") as f:
    json.dump(bible_data, f, ensure_ascii=False, indent=2)

print("✅ Ветхий Завет (с 1 по 39 книгу, JSON BookId с 28) добавлен. Файл сохранён.")
