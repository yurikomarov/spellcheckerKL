import re
from collections import defaultdict
from functools import lru_cache


class SpellChecker:
    def __init__(self, dictionary_path):
        self.dictionary = set()
        self.ngram_index = defaultdict(set)
        self.load_dictionary(dictionary_path)

        self.common_confusions = {
            'е': 'и', 'и': 'е',
            'о': 'а', 'а': 'о',
            'э': 'е', 'е': 'э'
        }

    def load_dictionary(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            for word in file:
                word = word.strip().lower()
                if word:
                    self.dictionary.add(word)
                    for i in range(min(3, len(word) - 1)):
                        self.ngram_index[word[i:i + 2]].add(word)

    @lru_cache(maxsize=65536)
    def damerau_levenshtein(self, word, right_word):
        word_len, right_len = len(word), len(right_word)

        if abs(word_len - right_len) > 2:
            return float('inf')

        current_row = [0] * (right_len + 1)
        previous_row = [0] * (right_len + 1)
        preprev_row = [0] * (right_len + 1)

        for j in range(right_len + 1):
            previous_row[j] = j

        for i in range(1, word_len + 1):
            current_row[0] = i

            for j in range(1, right_len + 1):
                if (word[i - 1] in self.common_confusions and
                        self.common_confusions[word[i - 1]] == right_word[j - 1]):
                    cost = 0
                elif word[i - 1] == right_word[j - 1]:
                    cost = 0
                else:
                    cost = 1

                current_row[j] = min(
                    previous_row[j] + 1,  # Удаление
                    current_row[j - 1] + 1,  # Вставка
                    previous_row[j - 1] + cost  # Замена
                )

                if (i > 1 and j > 1 and
                        word[i - 1] == right_word[j - 2] and
                        word[i - 2] == right_word[j - 1]):
                    current_row[j] = min(
                        current_row[j],
                        preprev_row[j - 2] + 1
                    )

            preprev_row, previous_row, current_row = previous_row, current_row, preprev_row

        return previous_row[right_len]

    def get_candidates(self, word):
        word = word.lower()

        confusion_variants = set()
        for i in range(len(word)):
            if word[i] in self.common_confusions:
                variant = word[:i] + self.common_confusions[word[i]] + word[i + 1:]
                confusion_variants.add(variant)

        seen = set()
        for source_word in [word] + list(confusion_variants):
            for i in range(min(2, len(source_word) - 1)):
                ngram = source_word[i:i + 2]
                for candidate in self.ngram_index.get(ngram, set()):
                    if candidate not in seen:
                        seen.add(candidate)
                        yield candidate

    def find_corrections(self, word, max_distance=2, top_n=3):
        word = word.lower()

        if word in self.dictionary:
            return []

        suggestions = []

        for candidate in self.get_candidates(word):
            if abs(len(candidate) - len(word)) > max_distance:
                continue

            ngram_matches = 0
            for i in range(min(2, len(word) - 1)):
                if word[i:i + 2] in candidate:
                    ngram_matches += 1
            if ngram_matches < 1:
                continue

            distance = self.damerau_levenshtein(word, candidate)
            if distance <= max_distance:
                suggestions.append((candidate, distance))

        suggestions.sort(key=lambda x: (x[1], abs(len(x[0]) - len(word))))
        return [word for word, _ in suggestions[:top_n]]

    def check_text(self, text):
        for match in re.finditer(r'\b\w+\b', text.lower()):
            word = match.group()
            if word not in self.dictionary:
                corrections = self.find_corrections(word)
                if corrections:
                    print(f"Ошибка: '{word}' | Варианты: {', '.join(corrections)}")


if __name__ == "__main__":
    checker = SpellChecker(".venv/russian.txt")
    text = input()
    checker.check_text(text)
