"""
Scraper enrichi MOCK pour test
Utilise des données de test pour vérifier la structure JSON
Version complète avec vraies données eBay/LBC viendra après
"""

import json
from datetime import datetime

OUTPUT_FILE = "rare_books_enriched.json"

# Données de test réalistes
MOCK_DATA = [
    {
        'titre': 'Le Seigneur des Anneaux - La Communauté',
        'auteur': 'J.R.R. Tolkien',
        'isbn': '9782253031963',
        'rare': True,
        'channels': {
            'ebay': {
                'price': 15.50,
                'count': 12,
                'delay': 5
            },
            'lbc': {
                'price': 13.00,
                'count': 8,
                'delay': 10
            }
        }
    },
    {
        'titre': 'Harry Potter à l\'école des sorciers',
        'auteur': 'J.K. Rowling',
        'isbn': '9782070524609',
        'rare': True,
        'channels': {
            'ebay': {
                'price': 12.00,
                'count': 25,
                'delay': 3
            },
            'lbc': {
                'price': 10.50,
                'count': 15,
                'delay': 8
            }
        }
    },
    {
        'titre': 'Les Misérables',
        'auteur': 'Victor Hugo',
        'isbn': '9782070364602',
        'rare': True,
        'channels': {
            'ebay': {
                'price': 18.00,
                'count': 7,
                'delay': 6
            },
            'lbc': {
                'price': 14.50,
                'count': 4,
                'delay': 12
            }
        }
    },
    {
        'titre': 'Le Comte de Monte Cristo',
        'auteur': 'Alexandre Dumas',
        'isbn': '9782070368761',
        'rare': True,
        'channels': {
            'ebay': {
                'price': 22.00,
                'count': 5,
                'delay': 8
            },
            'lbc': {
                'price': 18.00,
                'count': 2,
                'delay': 15
            }
        }
    },
    {
        'titre': 'La Peste',
        'auteur': 'Albert Camus',
        'isbn': '9782070368761',
        'rare': True,
        'channels': {
            'ebay': {
                'price': 11.00,
                'count': 18,
                'delay': 4
            },
            'lbc': {
                'price': 9.50,
                'count': 6,
                'delay': 11
            }
        }
    }
]

def add_listing_priority(books):
    """Ajoute la priorité de listing basée sur le nombre de ventes"""
    for book in books:
        if book['channels']:
            # Trier par nombre de ventes (descending)
            book['listing_priority'] = sorted(
                book['channels'].keys(),
                key=lambda c: book['channels'][c]['count'],
                reverse=True
            )
            # Best channel = celui avec le plus de ventes
            book['best_channel'] = book['listing_priority'][0]
    return books

def save_enriched_json(books):
    """Sauvegarde les données enrichies"""
    output = {
        'last_update': datetime.now().isoformat(),
        'total_books': len(books),
        'books': books
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] {len(books)} livres sauvegardes dans {OUTPUT_FILE}")

def main():
    print("=== Scraper MOCK Biblioscan (Test) ===")
    print("=" * 50)
    
    print("\n[*] Generation donnees de test...")
    
    # Ajouter priorités de listing
    enriched_books = add_listing_priority(MOCK_DATA)
    
    # Sauvegarder
    print("\n[OK] Sauvegarde...")
    save_enriched_json(enriched_books)
    
    print("\n" + "=" * 50)
    print("[OK] Donnees generees!")
    print("\n[INFO] Exemple de structure:\n")
    
    # Afficher un exemple formaté
    example = enriched_books[0]
    print(f"Livre: {example['titre']}")
    print(f"ISBN: {example['isbn']}")
    print(f"Priorite listing: {example['listing_priority']}")
    print(f"\nCanaux:")
    for channel, data in example['channels'].items():
        print(f"  {channel.upper()}: {data['price']}EUR | {data['count']} vendus | Delai: {data['delay']}j")

if __name__ == "__main__":
    main()
