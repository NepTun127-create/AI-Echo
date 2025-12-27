import re
from collections import Counter
from pathlib import Path


script_path = Path(__file__)
DATA_DIR = script_path.parent.parent / "data"
DATA_FILE = DATA_DIR / "data.txt"

content = DATA_FILE.read_text(encoding="utf-8")

clean_text = re.sub(r"[^\w\s]", "", content.lower())
words = clean_text.split()

stop_words = {
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
    "просто", "також", "тому", "свою", "своє", "свої", "його", "її", "є", "було", "буде"
}


clean_words = [w for w in words if w not in stop_words]

word_counts = Counter(clean_words)
print("-" * 590)

print(word_counts.most_common(5))
