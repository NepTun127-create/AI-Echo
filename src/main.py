from datetime import datetime
import os
import requests
import dotenv
import re
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv




class TextAnalyzer:
    def clean_data(self):           # Функція, яка прибирає «сміття» з тексту.
        clean_text = re.sub(r"[^\w\s]", "", self.content.lower())  # Бере сирий текст, переводить у нижній регістр і за допомогою формули видаляє все, що не є буквою чи пробілом
        self.words = clean_text.split()     # Розрізає очищений текст на окремі слова і зберігає їх у пам'ять

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.aimlapi.com/v1/chat/completions"
        self.stop_words = {
            # Українські (частки, прийменники, сполучники, займенники)
            "і", "та", "й", "а", "але", "чи", "бо", "як", "що", "щоб", "якщо", "бо", "та й",
            "в", "у", "на", "під", "за", "до", "з", "із", "через", "при", "біля", "по", "над",
            "не", "ні", "так", "же", "ж", "лише", "тільки", "ось", "навіть", "хіба",
            "я", "ти", "він", "вона", "воно", "ми", "ви", "они", "цей", "ця", "це", "ці",
            "мій", "твій", "свій", "наш", "ваш", "їх", "хто", "що", "який", "чий", "цього",
            "того", "мене", "мене", "собі", "мене", "вже", "ще", "тут", "там", "де", "коли",
            "про", "від", "для", "над", "проти", "між", "перед", "після",

            # English (articles, prepositions, conjunctions, pronouns, auxiliary verbs)
            "a", "an", "the", "and", "but", "or", "so", "because", "as", "if", "while",
            "in", "on", "at", "to", "for", "with", "by", "from", "up", "about", "into", "over", "after",
            "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their",
            "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "can", "will", "should", "would", "could",
            "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during",

            # Загальний "шум" (слова, що часто зустрічаються в статтях)
            "це", "може", "можуть", "дуже", "такий", "яка", "яке", "які", "наприклад", "один",
            "просто", "також", "тому", "свою", "своє", "свої", "його", "її", "є", "було", "буде"}
        self.script_path = Path(__file__)
        self.DATA_DIR = self.script_path.parent.parent / "data"
        self.DATA_FILE = self.DATA_DIR / "data.txt"
        self.content = self.DATA_FILE.read_text(encoding="utf-8")
        self.clean_data()


    def get_ai_summary(self):
        import time

        top_words = self.get_report()
        prompt = f"""
Ти — професійний аналітик даних. Твоє завдання — проаналізувати семантичне ядро тексту та сформулювати гіпотезу про його зміст.

Вхідні дані (ТОП-5 частотних слів):
{top_words}

Завдання:
Сформулюй стислий узагальнений висновок про ймовірну тематику першоджерела.

Вимоги до результату:
1. Тільки 1- максимум 2 речення українською мовою.
2. Використовуй науковий стиль та ймовірнісні конструкції ("Текст, імовірно, присвячений...", "Дані вказують на те, що зміст стосується...").
3. Уникай переліку вхідних слів, шукай зв'язок між ними.
4. СТРОГО: Жодних вступних фраз. Тільки текст висновку.
"""

        payload = {
            "model": "gpt-4o-mini", # Або інша безкоштовна модель з документації
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}", # Формат Bearer
            "Content-Type": "application/json"
        }

        for attempt in range(5):
            try:
                # Відправляємо запит
                response = requests.post(url=self.api_url, headers=headers, json=payload)

                # 1. Успіх (Код 200)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content']

                # 2. Перевищення ліміту (Код 429)
                elif response.status_code == 429:
                    print(f"Спроба {attempt + 1}: Ліміт вичерпано. Чекаю 65 секунд...")
                    time.sleep(65) # Пауза перед наступним циклом
                    continue # Переходимо до наступної ітерації циклу

                # 3. Інші помилки сервера
                else:
                    return f"Помилка сервера (Код {response.status_code}): {response.text}"

            except Exception as e:
                return f"Помилка підключення: {e}" #

        return "Помилка 429: Не вдалося отримати відповідь після 5 спроб. Спробуйте пізніше."


    def save_report_to_file(self, ai_summary):
        # 1. Створюємо шлях до папки 'reports' поруч із файлом main.py
        report_dir = self.script_path.parent / "reports"

        # 2. Створюємо папку, якщо її ще не існує
        report_dir.mkdir(parents=True, exist_ok=True)

        # 3. Формуємо назву файлу (дата_час)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_file = report_dir / f"report_{timestamp}.txt"

        # 4. Отримуємо дані для звіту
        top_words = self.get_report()

        # 5. Формуємо контент
        report_content = f"""
==================================================
        ЗВІТ АНАЛІЗУ ТЕКСТУ "AI-ECHO"
==================================================
Дата: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
--------------------------------------------------

1. КЛЮЧОВІ СЛОВА (ТОП-5):
"""
        for word, count in top_words:
            report_content += f"• {word}: {count} разів\n"

        report_content += f"""
--------------------------------------------------
2. ВИСНОВОК ШІ:
{ai_summary}

==================================================
Звіт згенеровано автоматично.
"""

        # 6. Запис у файл
        report_file.write_text(report_content, encoding="utf-8")
        return report_file


    def get_report(self):
        self.clean_words = [w for w in self.words if w not in self.stop_words]  # «Фільтр». Проходить по всіх словах і залишає тільки ті, яких немає в списку
        word_counts = Counter(self.clean_words) # Рахує частоту кожного важливого слова
        return word_counts.most_common(5)


analyzer = TextAnalyzer()
print("⏳ Починаю аналіз тексту через AI/ML API...")

# Отримуємо відповідь від ШІ
ai_result = analyzer.get_ai_summary()

# Виводимо в консоль для перевірки
print(f"\nРезультат аналізу:\n{ai_result}")

# Зберігаємо у файл
file_path = analyzer.save_report_to_file(ai_result)
print(f"\n✅ Звіт успішно збережено: {file_path}")


