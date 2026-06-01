# Tableau de bord social — Bilan RH (projet de démonstration)

Projet personnel illustrant une démarche complète d'analyse de données RH, **de la donnée brute à la restitution visuelle**. Le jeu de données est **entièrement fictif**, généré pour démontrer la méthode (aucune donnée réelle, aucune confidentialité en jeu).

## Ce que ça démontre
- Génération et traitement de données en **Python** (pandas / numpy)
- Calcul d'indicateurs RH : effectif, **turnover**, **taux d'absentéisme**, **accidents du travail** (taux de fréquence), ancienneté, pyramide des âges
- **Nettoyage / structuration** et agrégation de données
- **Restitution** : tableau de bord clair, lisible et autonome (HTML/CSS/JS, graphiques en SVG)
- **Lecture analytique** : passer du chiffre à la décision (panneau « Lecture de l'analyste »)

## Contenu du dossier
| Fichier | Rôle |
|---|---|
| `generer_analyse.py` | Génère les données fictives, calcule tous les indicateurs, écrit les CSV + `agregats.json` |
| `donnees_rh.csv` | Table salariés (1 ligne par salarié) |
| `suivi_mensuel.csv` | Série mensuelle (effectif, flux, absences, AT) |
| `agregats.json` | Indicateurs prêts à afficher |
| `build_dashboard.py` | Injecte les agrégats dans le tableau de bord |
| `tableau_de_bord_rh.html` | **Le livrable visible** — à ouvrir dans un navigateur |

## Reproduire
```bash
pip install pandas numpy
python3 generer_analyse.py      # données + indicateurs
python3 build_dashboard.py      # tableau de bord
# puis ouvrir tableau_de_bord_rh.html
```

## Comment en parler (pour le posséder vraiment)
Si un client ou un recruteur te questionne, tu peux dire, en vérité :
- « J'ai simulé des données RH réalistes (effectif, mouvements, absences) sur 24 mois, puis j'ai calculé les indicateurs d'un bilan social et construit un tableau de bord pour les restituer. »
- Le **turnover** = sorties sur 12 mois / effectif moyen. Le **taux d'absentéisme** = jours d'absence / jours théoriques travaillés. Le **taux de fréquence AT** = (nombre d'AT × 1 000 000) / heures travaillées — la norme française.
- La **saisonnalité** de l'absentéisme (pic hivernal) est volontairement intégrée pour rendre la démo réaliste.

> Règle d'honnêteté : ne présente comme acquis que ce que tu peux expliquer et refaire. Prends le temps de relire `generer_analyse.py` ligne par ligne — c'est court et commenté — pour pouvoir en parler sans hésiter.

## Idées d'extensions (prochaines versions)
- Filtre interactif par service / par année
- Version **Excel** du même tableau de bord (pour les clients qui veulent éditer)
- Comparaison à des repères de secteur
- Déclinaison **ventes** ou **finance** sur la même structure
