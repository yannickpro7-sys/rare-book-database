import time
from requests_html import HTMLSession
import re

URL = "https://lebouquinfrancais.fr/livres-recherches.php"
OUTPUT = "rare_books.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Détection ISBN
def extract_isbn(text):
    match = re.search(r"\b(?:97[89]\d{10}|\d{9}[\dX])\b", text)
    return match.group(0) if match else None

# Nettoyage du texte avant extraction
def clean_text(t):
    parasites = [
        "critique(s)", "lecteurs", "Aucune offre aujourd'hui",
        "Publié en", "collection", "chez", "critiques(s)"
    ]
    for p in parasites:
        t = t.replace(p, "")
    return t.strip()

def scrape_lbf():
    print("Scraping Le Bouquin Français...")

    for attempt in range(MAX_RETRIES):
        try:
            session = HTMLSession()
            response = session.get(URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            break
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Tentative {attempt + 1}/{MAX_RETRIES} échouée ({str(e)[:50]}...). Nouvelle tentative dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Avertissement : impossible de se connecter après {MAX_RETRIES} tentatives.")
                print("Le workflow continue sans mise à jour (le site peut bloquer les IPs de GitHub Actions).")
                return  # Exit gracefully without error

    soup = response.html

    rows = soup.find_all("tr")
    print(f"Lignes trouvées : {len(rows)}")

    livres = []

    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        text = " ".join(cell.get_text(" ", strip=True) for cell in cells)
        isbn = extract_isbn(text)
        if not isbn:
            continue

        # On coupe avant l’ISBN
        avant = text.split(isbn)[0].strip()
        avant = clean_text(avant)

        # Tentative de séparation Titre / Auteur
        # Cas 1 : "Titre | Auteur"
        if "|" in avant:
            parts = [p.strip() for p in avant.split("|") if p.strip()]
            titre = parts[0]
            auteur = parts[1] if len(parts) > 1 else "Auteur inconnu"

        # Cas 2 : "Titre - Auteur"
        elif " - " in avant:
            parts = [p.strip() for p in avant.split(" - ") if p.strip()]
            titre = parts[0]
            auteur = parts[1] if len(parts) > 1 else "Auteur inconnu"

        # Cas 3 : fallback
        else:
            titre = avant
            auteur = "Auteur inconnu"

        livres.append((titre, auteur, isbn))

    # Suppression des doublons
    livres = list(set(livres))

    # Écriture du fichier final
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Liste des livres recherchés (Bouquin Français)\n")
        f.write("# Format : Titre | Auteur | ISBN\n\n")
        for titre, auteur, isbn in livres:
            f.write(f"{titre} | {auteur} | {isbn}\n")

    print(f"{len(livres)} livres propres enregistrés dans {OUTPUT} !")

if __name__ == "__main__":
    scrape_lbf()
