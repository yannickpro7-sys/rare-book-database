# Rare Book Database

Base de données des livres recherchés du site Le Bouquin Français, extraite automatiquement via un scraper Python.

## Contenu du projet

- scrape_bf.py — Script Python qui récupère les livres recherchés
- rare_books.txt — Liste propre au format Titre | Auteur | ISBN
- requirements.txt — Dépendances Python nécessaires au scraper

## Installation

Installer les dépendances Python :

pip install -r requirements.txt

## Utilisation

Lancer le scraper pour mettre à jour la base :

python scrape_bf.py

Le fichier rare_books.txt sera automatiquement mis à jour avec les données les plus récentes.

## Objectif du projet

Ce projet sert de base pour une application Android permettant :

- de scanner un livre via son ISBN
- de récupérer son prix du marché
- de détecter s’il est recherché
- d’afficher les offres disponibles
- d’aider à l’arbitrage de revente de livres rares

## Licence

Projet open-source, libre d’utilisation et d’amélioration.


