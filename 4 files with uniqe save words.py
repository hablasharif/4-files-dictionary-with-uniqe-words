import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

# File paths
database_path = r"C:\Users\style\Desktop\Dictionary research\Englsih Words Database.txt"
found_bangla_path = r"C:\Users\style\Desktop\Dictionary research\Found Bangla Words - Copy.txt"
not_found_english_path = r"C:\Users\style\Desktop\Dictionary research\Not Found English Words - Copy.txt"
garbage_words_path = r"C:\Users\style\Desktop\Dictionary research\Garbage english words.txt"

# Helper functions
def read_words_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())
    return set()

def save_words_to_file(file_path, words):
    existing_words = read_words_from_file(file_path)
    new_words = [word.strip() for word in words if word.strip() not in existing_words]
    if new_words:
        with open(file_path, 'a', encoding='utf-8') as file:
            for word in new_words:
                file.write(f"{word}\n")

def search_online(word):
    url = f"https://www.english-bangla.com/dictionary/{word}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                return False, None  # Not found online
            else:
                content = response.text
                soup = BeautifulSoup(content, 'html.parser')
                span_tags = soup.find_all('span', class_='format1')
                if span_tags:
                    meanings = ', '.join(tag.get_text() for tag in span_tags)
                    return True, meanings
                return False, None
        except requests.RequestException:
            continue
    return False, None

def process_words(user_input_words):
    # Read existing words from files
    database_words = read_words_from_file(database_path)
    found_bangla_words = read_words_from_file(found_bangla_path)
    not_found_english_words = read_words_from_file(not_found_english_path)
    garbage_words = read_words_from_file(garbage_words_path)

    # Initialize sets for different categories
    words_to_search_online = set()
    found_bangla_meanings = {}
    not_found_words = set()

    # Process user input words
    for word in tqdm(user_input_words, desc="Processing words"):
        if word in database_words:
            if word in found_bangla_words:
                continue  # Word already found with Bangla meaning
            elif word in not_found_english_words:
                continue  # Word already marked as not found in English
            else:
                words_to_search_online.add(word)  # Word needs to be searched online
        else:
            garbage_words.add(word)  # Word not found in database, move to garbage words

    # Save new garbage words to file
    save_words_to_file(garbage_words_path, garbage_words)

    # Search online for words to be searched
    for word in tqdm(words_to_search_online, desc="Searching online"):
        found, meaning = search_online(word)
        if found:
            found_bangla_meanings[word] = meaning
        else:
            not_found_words.add(word)

    # Save found meanings and not found words to respective files
    save_words_to_file(found_bangla_path, found_bangla_meanings.keys())
    save_words_to_file(not_found_english_path, not_found_words)

# Example usage
user_input_words = ["zinka", "dinka", "fuck","suck","dick", "word","vagina"]
process_words(user_input_words)
