# Santa secret : fiche de reprise (20.11.2026)

## But
Tirage au sort du Secret Santa entre collègues (une dizaine), révélation le 04.12.2026 au repas de fin d'année, thème Noël CFF. Objectif : prêt le lundi 23.11.2026 au matin.

## État
- App construite et testée (iPhone simulé et paysage) : `index.html` + `data.json`.
- Écran 1 : texte d'annonce de Driss. Écran 2 : tableau à palettes (design validé dans OneSpace, page « Tableau du tirage », collection `tableau`) avec bouton rouge « Toucher pour lancer le tirage au sort », cliquetis, tampon « Voyage confirmé », confettis, son activé par défaut.
- Lien d'essai avec nom bidon : artefact « Santa secret (essai) » (https://claude.ai/artifact/JGxHL6u74pb4gnb6FTui9Y).
- Publié provisoirement dans un sous-dossier du dépôt du calendrier de Nath (https://ara-maker-hub.github.io/santa-secret/). Driss veut l'app SÉPARÉE du calendrier : à déplacer dans un dépôt à elle, dès qu'il aura créé le dépôt vide « santa-secret » (compte ARA-Maker-hub), puis retirer `santa/` du dépôt du calendrier.

## Fonctionnement
- Chaque participant a un lien personnel `…/#p03.<clé>`. Le résultat est chiffré (AES-GCM) ; la clé n'existe que dans le lien. Rien de lisible dans le code public.
- `outils/genere.py` fait le tirage (un seul grand cycle : pas de tirage de soi-même, pas de duo A↔B, exceptions à sens unique) et écrit `data.json` + `liens_et_tirage.md` (PRIVÉ : à garder sur le PC de Driss, jamais dans le dépôt). Config : `config.exemple.json` à copier en `config.json` (noms + exceptions ; ne jamais publier ce fichier).
- Relancer le script change toutes les clés et tout le tirage : à faire une seule fois, à la fin, avec les vrais noms, puis pousser seulement `data.json`.
- Mode démonstration : `…/santa/#demo`.

## Reste à faire
1. Voix du Père Noël (ElevenLabs) : proposer les textes d'intro et d'annonce dans OneSpace, Driss valide, puis générer les mp3 (`voix/intro.mp3`, et un fichier par participant `voix/p03.mp3` : l'app les joue s'ils existent).
2. Séparer l'app dans son propre dépôt.
3. Vrais noms + liste d'exceptions (Driss, à la toute fin), lancer le script, envoyer les liens par WhatsApp.
4. Garder la liste privée « qui offre à qui » pour Driss.
5. Ranger cette fiche dans Atelier_Maker\Santa_Secret et mettre à jour l'index (PC non lié lors de cette séance).
