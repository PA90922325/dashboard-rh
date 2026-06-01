#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet démo - Tableau de bord social (RH)
=========================================
Génère un jeu de données RH FICTIF mais réaliste pour une entreprise type
(~320 salariés, 24 mois), puis calcule les indicateurs clés d'un bilan social :
effectif, turnover, absentéisme, accidents du travail, ancienneté, pyramide des âges.

Sorties :
  - donnees_rh.csv      : table salariés (1 ligne / salarié)
  - suivi_mensuel.csv   : série mensuelle (effectif, flux, absences, AT)
  - agregats.json       : indicateurs prêts à afficher dans le tableau de bord

Tout est commenté pour être compris, expliqué et maintenu.
"""
import json
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)           # graine fixe = résultats reproductibles
N = 320                                    # effectif de référence
SERVICES = ["Production", "Logistique", "Commercial", "R&D", "Support & Admin", "Maintenance"]
POIDS_SERVICE = [0.34, 0.18, 0.14, 0.12, 0.14, 0.08]   # répartition réaliste
MOIS = pd.date_range("2024-01-01", "2025-12-01", freq="MS")   # 24 mois

# ---------------------------------------------------------------------------
# 1) Table salariés (niveau individuel)
# ---------------------------------------------------------------------------
service = rng.choice(SERVICES, size=N, p=POIDS_SERVICE)
sexe = rng.choice(["F", "H"], size=N, p=[0.46, 0.54])
age = np.clip(rng.normal(40, 10, N).round().astype(int), 19, 64)
anciennete = np.clip(rng.gamma(2.2, 2.6, N), 0.2, 35).round(1)   # années
statut = rng.choice(["CDI", "CDD"], size=N, p=[0.86, 0.14])

salaries = pd.DataFrame({
    "id": [f"S{1000+i}" for i in range(N)],
    "service": service, "sexe": sexe, "age": age,
    "anciennete_ans": anciennete, "statut": statut,
})
salaries.to_csv("donnees_rh.csv", index=False)

# ---------------------------------------------------------------------------
# 2) Série mensuelle (effectif, flux, absences, accidents du travail)
# ---------------------------------------------------------------------------
# Saisonnalité de l'absentéisme : plus fort en hiver (grippe), creux l'été.
mois_num = np.array([m.month for m in MOIS])
saison = 1 + 0.45 * np.cos((mois_num - 1) / 12 * 2 * np.pi)   # ~1.45 en janv, ~0.55 en juil

effectif, entrees, sorties = [], [], []
abs_maladie, abs_at, abs_maternite, abs_autres, at_count = [], [], [], [], []
eff = 305                                     # effectif de départ
JOURS_OUVRES = 21                             # base mensuelle moyenne

for i, m in enumerate(MOIS):
    e = int(rng.poisson(6))                   # entrées du mois
    s = int(rng.poisson(5 + (1 if mois_num[i] in (1, 9) else 0)))  # sorties (+ janv/sept)
    eff = max(280, eff + e - s)
    jours_theoriques = eff * JOURS_OUVRES

    # jours d'absence par motif (l'absentéisme maladie suit la saison)
    j_mal = rng.normal(jours_theoriques * 0.030 * saison[i], 40)
    j_at = rng.normal(jours_theoriques * 0.006, 12)
    j_mat = rng.normal(jours_theoriques * 0.008, 15)
    j_aut = rng.normal(jours_theoriques * 0.004, 8)
    nb_at = int(max(0, rng.poisson(1.0 + (0.6 if i in (2, 14) else 0))))  # 2 pics

    effectif.append(eff); entrees.append(e); sorties.append(s)
    abs_maladie.append(max(0, j_mal)); abs_at.append(max(0, j_at))
    abs_maternite.append(max(0, j_mat)); abs_autres.append(max(0, j_aut))
    at_count.append(nb_at)

suivi = pd.DataFrame({
    "mois": [m.strftime("%Y-%m") for m in MOIS],
    "effectif": effectif, "entrees": entrees, "sorties": sorties,
    "abs_maladie_j": np.round(abs_maladie).astype(int),
    "abs_at_j": np.round(abs_at).astype(int),
    "abs_maternite_j": np.round(abs_maternite).astype(int),
    "abs_autres_j": np.round(abs_autres).astype(int),
    "accidents_travail": at_count,
})
suivi["jours_theoriques"] = suivi["effectif"] * JOURS_OUVRES
suivi["abs_total_j"] = suivi[["abs_maladie_j", "abs_at_j", "abs_maternite_j", "abs_autres_j"]].sum(axis=1)
suivi["taux_absenteisme"] = (suivi["abs_total_j"] / suivi["jours_theoriques"] * 100).round(2)
suivi.to_csv("suivi_mensuel.csv", index=False)

# ---------------------------------------------------------------------------
# 3) Indicateurs clés (KPI)
# ---------------------------------------------------------------------------
eff_fin = int(suivi["effectif"].iloc[-1])
eff_moyen = float(suivi["effectif"].mean())
sorties_12m = int(suivi["sorties"].iloc[-12:].sum())
turnover = round(sorties_12m / eff_moyen * 100, 1)            # turnover annuel %
taux_abs_global = round(suivi["abs_total_j"].sum() / suivi["jours_theoriques"].sum() * 100, 2)
at_total = int(suivi["accidents_travail"].sum())
heures_travaillees = suivi["jours_theoriques"].sum() * 7      # ~7h/jour
tf_at = round(at_total * 1_000_000 / heures_travaillees, 1)   # taux de fréquence (norme FR)
anciennete_moy = round(float(salaries["anciennete_ans"].mean()), 1)
part_f = round((salaries["sexe"] == "F").mean() * 100)

# Répartitions
par_service = salaries["service"].value_counts().reindex(SERVICES).fillna(0).astype(int)
tranches = pd.cut(salaries["age"], [18, 29, 39, 49, 100],
                  labels=["< 30 ans", "30-39 ans", "40-49 ans", "50 ans et +"])
par_age = tranches.value_counts().reindex(["< 30 ans", "30-39 ans", "40-49 ans", "50 ans et +"]).astype(int)

# Entrées / sorties par trimestre
suivi["trim"] = pd.PeriodIndex(pd.to_datetime(suivi["mois"]), freq="Q").astype(str)
flux_trim = suivi.groupby("trim")[["entrees", "sorties"]].sum()

motifs = {
    "Maladie": int(suivi["abs_maladie_j"].sum()),
    "Accident du travail": int(suivi["abs_at_j"].sum()),
    "Maternité / Paternité": int(suivi["abs_maternite_j"].sum()),
    "Autres": int(suivi["abs_autres_j"].sum()),
}

# Quelques lectures d'analyste (data-driven, donc cohérentes avec les chiffres)
mois_pic = suivi.loc[suivi["taux_absenteisme"].idxmax(), "mois"]
insights = [
    f"Le taux d'absentéisme global s'établit à {taux_abs_global:.2f} %, avec un pic en {mois_pic} "
    f"porté par les arrêts maladie (saisonnalité hivernale).",
    f"Le turnover annuel atteint {turnover:.1f} % ; les départs se concentrent en début d'année et en septembre.",
    f"{at_total} accidents du travail sur la période (taux de fréquence {tf_at}), à suivre via un plan de prévention ciblé.",
    f"Pyramide des âges marquée par les 40-49 ans : anticiper les départs et la transmission des compétences.",
]

agregats = {
    "entreprise": "ACME Industries (données fictives)",
    "periode": "Janvier 2024 – Décembre 2025",
    "kpi": {
        "effectif": eff_fin, "turnover": turnover, "absenteisme": taux_abs_global,
        "at_total": at_total, "tf_at": tf_at, "anciennete": anciennete_moy,
        "part_femmes": int(part_f), "part_hommes": int(100 - part_f),
    },
    "effectif_mensuel": {"mois": suivi["mois"].tolist(), "valeurs": suivi["effectif"].tolist()},
    "absenteisme_mensuel": {"mois": suivi["mois"].tolist(), "valeurs": suivi["taux_absenteisme"].tolist()},
    "flux_trim": {"trim": flux_trim.index.tolist(),
                  "entrees": flux_trim["entrees"].tolist(), "sorties": flux_trim["sorties"].tolist()},
    "par_service": {"labels": par_service.index.tolist(), "valeurs": par_service.tolist()},
    "par_age": {"labels": par_age.index.tolist(), "valeurs": par_age.tolist()},
    "motifs_absence": {"labels": list(motifs.keys()), "valeurs": list(motifs.values())},
    "insights": insights,
}
with open("agregats.json", "w", encoding="utf-8") as f:
    json.dump(agregats, f, ensure_ascii=False, indent=2)

print("Données générées.")
print(f"  Effectif fin de période : {eff_fin}")
print(f"  Turnover annuel        : {turnover} %")
print(f"  Absentéisme global     : {taux_abs_global} %")
print(f"  Accidents du travail   : {at_total} (TF {tf_at})")
print(f"  Ancienneté moyenne     : {anciennete_moy} ans")
print(f"  Répartition F/H        : {part_f} % / {100-part_f} %")
