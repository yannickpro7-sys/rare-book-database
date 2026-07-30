"""
Scraper enrichi pour Biblioscan
Récupère les données de vente réelles depuis eBay et Le Bon Coin
Génère rare_books_enriched.json pour l'app mobile
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time

# URLs de base
EBAY_URL = "https://www.ebay.com/sch/i.html"
LBC_URL = "https://www.leboncoin.fr/search"
RARE_BOOKS_FILE = "rare_books.txt"
OUTPUT_FILE = "rare_books_enriched.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def parse_rare_books():
    """Parse rare_books.txt et retourne liste de livres avec ISBN"""
    books = []
    try:
        with open(RARE_BOOKS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse format: Titre | Auteur | ISBN
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    books.append({
                        'titre': parts[0],
                        'auteur': parts[1],
                        'isbn': parts[2],
                        'rare': True
                    })
    except FileNotFoundError:
        print(f"Erreur: {RARE_BOOKS_FILE} non trouvé")
        return []
    
    print(f"✅ {len(books)} livres rares chargés")
    return books

def scrape_ebay_listings(isbn):
    """
    Scrape eBay pour les annonces vendues (sold listings)
    Retourne: prix moyen, nombre vendus, délai moyen en jours
    """
    try:
        # eBay API REST alternative: utilise les paramètres de recherche
        params = {
            '_nkw': isbn,
            'LH_Sold': 1,  # Sold listings only
            'LH_Complete': 1,  # Completed listings
            'rt': 'nc'
        }
        
        response = requests.get(EBAY_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse results (simplified - adapté à la structure eBay)
        prices = []
        items = soup.find_all('div', class_='s-item')
        
        for item in items[:10]:  # Limiter à 10 résultats
            try:
                price_elem = item.find('span', class_='s-price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract price (e.g., "$15.99" or "£12.50")
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        prices.append(price)
            except:
                continue
        
        if prices:
            avg_price = sum(prices) / len(prices)
            # Délai moyen estimé: eBay = 5 jours (standard)
            return {
                'price': round(avg_price, 2),
                'count': len(prices),
                'delay': 5
            }
        return None
        
    except Exception as e:
        print(f"  ⚠️ eBay error for ISBN {isbn}: {str(e)[:50]}")
        return None

def scrape_leboncoin_listings(isbn):
    """
    Scrape Le Bon Coin pour les annonces vendues
    Retourne: prix moyen, nombre vendus, délai moyen en jours
    """
    try:
        # Le Bon Coin search
        params = {
            'q': isbn,
            'category': 288,  # Livres
        }
        
        response = requests.get(LBC_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse results (simplifié)
        prices = []
        items = soup.find_all('a', class_='link')  # Adapt to LBC structure
        
        for item in items[:5]:  # Limiter à 5
            try:
                price_elem = item.find('span', class_='price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())
                        prices.append(price)
            except:
                continue
        
        if prices:
            avg_price = sum(prices) / len(prices)
            # Délai moyen estimé: LBC = 10 jours (plus lent)
            return {
                'price': round(avg_price, 2),
                'count': len(prices),
                'delay': 10
            }
        return None
        
    except Exception as e:
        print(f"  ⚠️ Le Bon Coin error for ISBN {isbn}: {str(e)[:50]}")
        return None

def enrich_books(books):
    """
    Enrichit chaque livre avec données de vente
    """
    enriched = []
    total = len(books)
    
    for idx, book in enumerate(books, 1):
        print(f"[{idx}/{total}] Enriching {book['titre'][:40]}...")
        
        # Scrape eBay
        ebay_data = scrape_ebay_listings(book['isbn'])
        time.sleep(1)  # Rate limiting
        
        # Scrape Le Bon Coin
        lbc_data = scrape_leboncoin_listings(book['isbn'])
        time.sleep(1)  # Rate limiting
        
        # Construct enriched entry
        enriched_book = {
            'isbn': book['isbn'],
            'titre': book['titre'],
            'auteur': book['auteur'],
            'rare': book['rare'],
            'channels': {}
        }
        
        if ebay_data:
            enriched_book['channels']['ebay'] = ebay_data
        
        if lbc_data:
            enriched_book['channels']['lbc'] = lbc_data
        
        # Calculate best channel
        if enriched_book['channels']:
            best_channel = max(
                enriched_book['channels'].keys(),
                key=lambda c: enriched_book['channels'][c]['count']
            )
            enriched_book['best_channel'] = best_channel
            
            # Listing priority (by number of sales)
            enriched_book['listing_priority'] = sorted(
                enriched_book['channels'].keys(),
                key=lambda c: enriched_book['channels'][c]['count'],
                reverse=True
            )
        
        enriched.append(enriched_book)
    
    return enriched

def save_enriched_json(enriched_books):
    """Sauvegarde les données enrichies en JSON"""
    output = {
        'last_update': datetime.now().isoformat(),
        'total_books': len(enriched_books),
        'books': enriched_books
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(enriched_books)} livres enrichis sauvegardés dans {OUTPUT_FILE}")

def main():
    print("🚀 Scraper Enrichi Biblioscan")
    print("=" * 50)
    
    # 1. Charger rare_books.txt
    print("\n📖 Étape 1: Charger livres rares...")
    books = parse_rare_books()
    
    if not books:
        print("❌ Aucun livre à enrichir")
        return
    
    # 2. Enrichir avec données eBay/LBC
    print("\n🔍 Étape 2: Scraper eBay et Le Bon Coin...")
    enriched_books = enrich_books(books)
    
    # 3. Sauvegarder
    print("\n💾 Étape 3: Sauvegarder...")
    save_enriched_json(enriched_books)
    
    print("\n" + "=" * 50)
    print("✅ Scraper terminé!")
    print(f"📱 L'app peut maintenant consulter {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
