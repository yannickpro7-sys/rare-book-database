# Architecture Biblioscan — Application No-Code

## Vue d'ensemble

Biblioscan est une app mobile no-code (Flutter Flow) qui aide à identifier rapidement les livres rares et rentables en brocante.

**Flux principal :**
```
📱 Scan ISBN
    ↓
🔍 Vérifier dans rare_books.txt (GitHub)
    ↓
💰 Appeler Rakuten API → Prix + Dispo
    ↓
📊 Afficher : "Rare?" + "Bon achat?" + Prix
    ↓
💾 Sauvegarder dans historique local
```

---

## Sources de données

### 1. rare_books.txt (GitHub)
**Localisation :** https://raw.githubusercontent.com/yannickpro7-sys/rare-book-database/main/rare_books.txt

**Format :**
```
Titre | Auteur | ISBN | Rareté | Date_Mise_à_Jour
Le Seigneur des Anneaux | Tolkien | 9782253031963 | Très Recherché | 2026-07-30
```

**Utilité pour l'app :**
- Recherche rapide d'ISBN dans la liste
- Afficher le statut "Livre recherché" immédiatement
- Cache local pour mode hors-ligne

### 2. Rakuten API
**Documentation :** https://webservice.rakuten.fr/

**Endpoints utiles :**
- `ProductSearch` → Chercher par ISBN/Titre
- Retour : Prix, Disponibilité, Marchand, Nombre d'avis

**Clé API :** À obtenir

**Limites :** À vérifier (X appels/jour gratuit ?)

---

## Architecture Flutter Flow

### Écran 1 : Accueil (Home)
**Composants :**
- Bouton "Scanner ISBN" (camera widget)
- Bouton "Recherche manuelle" (text input)
- Bouton "Ma collection" (link to screen 3)
- Bouton "Paramètres" (link to screen 4)

### Écran 2 : Résultat du scan (Scan Result)
**Entrée :** ISBN (string)

**Logique :**
1. Appel API : `GET rare_books.txt` → Chercher ISBN
2. Stockage : Variable `isRareBook` = true/false
3. Appel API : Rakuten `ProductSearch(ISBN)` → Prix, Dispo
4. Calcul : Indicateur "Bon achat ?" basé sur prix + rareté

**Affichage :**
```
📖 [Titre]
✍️ [Auteur]
🏷️ ISBN : [ISBN]

⚠️ Statut : [Recherché / Commun]
💵 Prix moyen : [XX€]
📦 Disponibilité : [Dispo / Rare / Rupture]
🎯 Bon achat ? [OUI / NON] (indicateur rouge/vert)

📌 Ajouter à ma collection
```

**Boutons :**
- Ajouter à ma collection (sauve en local)
- Rechercher ailleurs (ouvre Google)
- Retour accueil

### Écran 3 : Ma collection
**Stockage :** SQLite local / Firebase

**Affichage :**
- Liste des livres scannés
- Valeur totale estimée
- Alertes : "Ce livre a augmenté de 20% ⬆️"
- Bouton Export CSV

### Écran 4 : Paramètres
**Options :**
- Actualiser rare_books.txt (force sync GitHub)
- Clé Rakuten API (champ texte)
- Mode brocante (UI simplifiée, boutons plus gros)
- Mode hors-ligne (use cache local)
- Export historique

---

## Intégrations techniques

### 1. GitHub Integration (rare_books.txt)
**Via HTTP GET :**
```
URL: https://raw.githubusercontent.com/yannickpro7-sys/rare-book-database/main/rare_books.txt
Response: Text file
Parse: Split par newlines, cherche ISBN
```

**Flutter Flow :**
- HTTP Request API call
- Response type: Plain text
- Parse: Custom (regex ou split)
- Cache: Local storage (refresh hebdo)

### 2. Rakuten API Integration
**Authentification :** Clé API en header

**Exemple appel :**
```
GET https://api.rakuten.co.jp/services/api/Product/Search/20170707
?applicationId=YOUR_API_KEY
&isbn=9782253031963
```

**Response :**
```json
{
  "Product": {
    "productName": "Le Seigneur des Anneaux",
    "salesPrice": 18.99,
    "medianPrice": 16.50,
    "affiliateUrl": "..."
  }
}
```

**Flutter Flow :**
- HTTP GET API call
- Headers: Auth + API key
- Response type: JSON
- Parse: Extract price, availability

### 3. Scanner ISBN (Caméra)
**Widget Flutter Flow :** Built-in Camera widget
- Détection code-barres automatique
- Retour ISBN en string
- Input pour écran 2

---

## Flux détaillé (Pseudocode)

```
ÉCRAN 1 : Utilisateur appuie sur "Scanner"
  ↓
CAMÉRA : Capture ISBN
  ↓
ÉCRAN 2 : ISBN détecté
  
  // Recherche dans rare_books.txt
  GET rare_books.txt from GitHub
  IF ISBN in file:
    isRareBook = TRUE
    raretyLevel = "Très Recherché"
  ELSE:
    isRareBook = FALSE
    raretyLevel = "Commun"
  
  // Recherche prix Rakuten
  CALL Rakuten.ProductSearch(ISBN)
  IF response:
    price = response.salesPrice
    medianPrice = response.medianPrice
    availability = response.availability
  ELSE:
    price = "N/A"
  
  // Calcul "Bon achat ?"
  IF isRareBook AND price < medianPrice * 0.8:
    goodDeal = TRUE  // Rouge/Vert
  ELSE:
    goodDeal = FALSE
  
  // Afficher résultats
  DISPLAY: Titre, Auteur, Prix, Rareté, Indicateur
  
  // Utilisateur peut ajouter à collection
  ON "Ajouter":
    SAVE {ISBN, Titre, Prix, Date} to Local DB
    SHOW "Ajouté ✅"
```

---

## Données locales (SQLite / Firebase)

**Table : UserCollection**
```
- id (PK)
- isbn (string, unique)
- titre (string)
- auteur (string)
- prix_achat (float)
- prix_marche (float)
- date_scan (datetime)
- notes (string)
```

**Table : PriceHistory** (optionnel)
```
- id (PK)
- isbn (FK)
- prix (float)
- date (datetime)
- source (Rakuten / autre)
```

---

## Cas d'usage en brocante

**Scénario :** Tu trouves un livre à 2€

1. **Scan rapide :** Pointe caméra sur code-barres
2. **Détection immédiate :** 
   - ✅ "C'est dans rare_books.txt" (Recherché!)
   - 💵 "Prix marché : 25€"
   - 🎯 "Bon achat? OUI" (vert)
3. **Action rapide :** Tap "Ajouter" → Continuer au prochain livre
4. **Résultat :** Après 10 scans, tu vois la liste des bons coups

**Mode hors-ligne :** 
- rare_books.txt téléchargé localement
- Pas besoin d'Internet en brocante
- Sync quand tu rentres

---

## Checklist implémentation

- [ ] Clé Rakuten API obtenue
- [ ] rare_books.txt enrichi avec rareté
- [ ] Écran 1 : UI accueil + bouton camera
- [ ] Écran 2 : Integration GitHub + Rakuten
- [ ] Écran 3 : Stockage local + affichage collection
- [ ] Écran 4 : Paramètres + export
- [ ] Tests en brocante réelle
- [ ] Optimisation : performance, UX
- [ ] Publication Play Store (optionnel)

---

## Prochaines étapes

1. ✅ **Confirmer Rakuten API gratuite** (clé + limites)
2. ✅ **Enrichir rare_books.txt** (ajouter rareté)
3. ✅ **Créer project Flutter Flow**
4. ✅ **Intégrer GitHub + Rakuten**
5. ✅ **Tester en local**
6. ✅ **Déployer sur Play Store**

