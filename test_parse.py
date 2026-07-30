from scraper_enrichi import parse_rare_books

books = parse_rare_books()
print(f"Loaded books: {len(books)}")
# print first 10
for b in books[:10]:
    print(b['titre'], ' - ', b['isbn'])
