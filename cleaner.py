import json
import re

# Загрузка файла
with open("bible_nrt_named.json", "r", encoding="utf-8") as f:
    bible_data = json.load(f)

def is_valid_verse(verse):
    """ Проверяет, что стих валидный и не содержит всю главу. """
    text = verse["Text"].strip()

    # Слишком длинный текст (например, вся глава)
    if len(text) > 500 and text.count("\n") > 5:
        return False

    # Повтор заголовков, как в первых двух строках
    if re.match(r'^[А-Яа-я].+\n\d+\s+', text):
        return False

    # Часто заголовки начинаются с цифры, но без настоящего ID
    if verse["VerseId"] != 1 and text.startswith("1 "):
        return False

    return True

def clean_text(text):
    """ Удаляет сноски вида [123] и лишние пробелы. """
    text = re.sub(r"\[\d+]", "", text)     # Удаление сносок
    text = re.sub(r"\s+", " ", text)       # Удаление лишних пробелов
    return text.strip()

# Чистка
for book in bible_data["Books"]:
    for chapter in book["Chapters"]:
        seen_ids = set()
        clean_verses = []

        for verse in chapter["Verses"]:
            vid = verse["VerseId"]
            if vid in seen_ids:
                continue
            if not is_valid_verse(verse):
                continue

            # Очищаем текст стиха
            verse["Text"] = clean_text(verse["Text"])

            seen_ids.add(vid)
            clean_verses.append(verse)

        # Обновляем главу
        chapter["Verses"] = sorted(clean_verses, key=lambda v: v["VerseId"])

# Сохраняем очищенный JSON
with open("bible_nrt_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(bible_data, f, ensure_ascii=False, indent=2)

print("✅ JSON очищен от сносок и сохранён в bible_nrt_cleaned.json")