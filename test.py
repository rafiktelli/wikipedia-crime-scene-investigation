import re

keywords = 'work|banana'
phrase = 'A working day keeps the doctor away'

match = re.search(keywords, phrase)
if match:
    print(f"Corresponding word: {match.group()}")