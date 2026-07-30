"""
Generate full mock rare_books_enriched.json for all parsed rare_books.txt entries.
Uses deterministic pseudo-random values per ISBN so results are stable across runs.
"""
from scraper_enrichi import parse_rare_books
import json
import hashlib
import random
from datetime import datetime

OUTPUT_FILE = "rare_books_enriched.json"

books = parse_rare_books()

enriched = []
for b in books:
    isbn = b['isbn']
    # deterministic seed from ISBN
    seed = int(hashlib.md5(isbn.encode('utf-8')).hexdigest()[:8], 16)
    rnd = random.Random(seed)

    # base price between 5 and 50
    base_price = 5 + (seed % 460) / 10.0  # 5.0 - 51.0

    ebay_price = round(base_price * (0.9 + rnd.random()*0.5), 2)
    lbc_price = round(base_price * (0.8 + rnd.random()*0.4), 2)

    ebay_count = rnd.randint(0, 30)
    lbc_count = rnd.randint(0, 20)

    # derive delay: more sales -> faster
    def delay_from_count(c):
        if c >= 20:
            return rnd.randint(1,4)
        if c >= 10:
            return rnd.randint(3,7)
        if c >= 5:
            return rnd.randint(5,12)
        if c > 0:
            return rnd.randint(7,20)
        return rnd.randint(10,40)

    ebay_delay = delay_from_count(ebay_count)
    lbc_delay = delay_from_count(lbc_count)

    channels = {}
    if ebay_count > 0:
        channels['ebay'] = {'price': ebay_price, 'count': ebay_count, 'delay': ebay_delay}
    if lbc_count > 0:
        channels['lbc'] = {'price': lbc_price, 'count': lbc_count, 'delay': lbc_delay}

    listing_priority = []
    best_channel = None
    if channels:
        # sort by count then price
        listing_priority = sorted(channels.keys(), key=lambda c: (channels[c]['count'], channels[c]['price']), reverse=True)
        best_channel = listing_priority[0]

    enriched.append({
        'titre': b['titre'],
        'auteur': b['auteur'],
        'isbn': isbn,
        'rare': b.get('rare', False),
        'channels': channels,
        'listing_priority': listing_priority,
        'best_channel': best_channel
    })

output = {
    'last_update': datetime.now().isoformat(),
    'total_books': len(enriched),
    'books': enriched
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"[OK] Generated {len(enriched)} mock enriched books into {OUTPUT_FILE}")
