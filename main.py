
# ============================================================================
# Configuration des chemins et paramètres
# ============================================================================
DIR = "Donnees_TMs/Annee_1"
INPUT_FILE = f"{DIR}/grid.csv"  # Fichier CSV contenant la grille des préférences
OUTPUT_DIR = f"{DIR}/results2"  # Répertoire pour les résultats
OUTPUT_FILE = f"{OUTPUT_DIR}/o2.csv"  # Fichier de résumé des résultats
TM_FILE = f"{DIR}/liste_sujets.csv"  # Fichier liste des travaux de maturité
DUO_FILE = f"{DIR}/duo.csv"  # Fichier des binômes d'élèves
NPROBLEMS_ELEVES_FILE = f"{DIR}/nproblems_eleves2.csv"  # Fichier pour enregistrer les problèmes rencontrés
NPROBLEMS_TM_FILE = f"{DIR}/nproblems_tm2.csv"  # Fichier pour enregistrer les problèmes par TM
N_TRIES = 1000  # Nombre de tentatives d'allocation

RANDOM_SEED = 67  # Graine pour la reproductibilité

import os
import random
import pandas as pd
import shutil
import numpy as np

# ============================================================================
# Initialisation des données
# ============================================================================
rng = np.random.default_rng(RANDOM_SEED)  # Générateur aléatoire
df_grid_orig = pd.read_csv(INPUT_FILE, index_col=0)  # Charger la grille originale
df_grid_orig.index = df_grid_orig.index.astype(str)  # Convertir les indices en chaînes
if os.path.exists(NPROBLEMS_ELEVES_FILE):
    nproblems_eleves = pd.read_csv(NPROBLEMS_ELEVES_FILE, index_col=0).iloc[:,0]
    nproblems_eleves.index = nproblems_eleves.index.astype(str)
else:
    nproblems_eleves = pd.Series(0.0, index=df_grid_orig.index)  # Initialiser le compteur de problèmes pour chaque élève

default_df = pd.DataFrame()  # DataFrame vide pour les cas d'erreur

# Charger les travaux de maturité et supprimer le dernier (TM libre)
df_tm = pd.read_csv(TM_FILE, index_col=0)
#df_tm.index = df_tm.index.astype(str)
df_tm = df_tm.drop(df_tm[df_tm["Langue"]=="Libre"].index)  # Enlever les TMs libres


if os.path.exists(NPROBLEMS_TM_FILE):
    nproblems_tm = pd.read_csv(NPROBLEMS_TM_FILE, index_col=0).iloc[:,0]

else:
    nproblems_tm = pd.Series(0.0, index=df_tm.index)  # Initialiser le compteur de problèmes pour chaque TM
# Charger les binômes et traiter les données
df_duo = pd.read_csv(DUO_FILE)
df_duo["Eleves"] = df_duo["Eleves"].str.split(r" \+ ")  # Séparer les élèves en liste
df_duo["Repr"] = df_duo["Eleves"].str[0]  # Représentant = premier élève du binôme

# Initialiser les résultats

# Créer ou nettoyer le répertoire de résultats
if os.path.exists(OUTPUT_DIR):
    i_try = len(os.listdir(OUTPUT_DIR))-1
    results = pd.read_csv(OUTPUT_FILE).to_dict(orient="list")
else:
    i_try = 0
    results = {"Id": [], "Mean": [], "Std": [], "Problems": [], "TMnonouverts": []}
    os.mkdir(OUTPUT_DIR)

def generate():
    global max_l2,best_mean,best_std
    
    """Génère une tentative d'attribution pour tous les TMs.

    Cette fonction effectue un passage unique sur tous les travaux de maturité (TMs).
    Elle construit une liste de candidats pour chaque TM, calcule des poids, gère
    les affectations de binômes, sélectionne les élèves et enregistre les données.
    """

    # Copie de travail de la grille de préférences originale pour cette tentative.
    df_grid = df_grid_orig.copy()
    
    problems = []
    TM_non_ouverts = []
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}

    # Parcourir les TMs dans un ordre aléatoire en utilisant le générateur fixe.
    # i_tm: int
    #print(nproblems_tm+1)
    for i_tm,tm in df_tm.sample(frac=1,weights=nproblems_tm+1,random_state=rng).iterrows():

        # Colonne du TM courant et masque des candidats ayant une préférence positive.
        mask = df_grid[str(i_tm)] > 0

        candidats = df_grid[mask]
        
        # a: Score de préférence pour le TM courant
        # b: Somme des autres scores de TM.
        a = candidats[str(i_tm)]
        result1 = candidats.drop(columns=[str(i_tm)])
        b = result1.sum(axis=1)

        # Binômes qui ont choisi ce TM.

        # Binômes qui ont choisi ce TM.
        duos = df_duo[df_duo["Choix"]==i_tm]

        # Calculer les poids comme le rapport entre le score du choix courant et
        # les autres scores disponibles.
        weights = a/b*(nproblems_eleves[candidats.index]+1)
        maximum = int(tm["Nombre maximal travaux"])

        # Gérer les poids des binômes et garantir que les membres sont affectés ensemble.
        for i_duo, duo in duos.iterrows():
            eleves = duo["Eleves"]
            weights_duo = weights.reindex(eleves,fill_value=0)
            weights_duo = weights.reindex(eleves,fill_value=0)
            if 0 in weights_duo.values and np.inf in weights_duo.values:
                # Si un membre n'a pas d'alternative disponible et l'autre est forcé,
                # enregistrer le problème et marquer le binôme comme non affecté.
                for eleve in weights_duo[weights_duo==np.inf].index:
                    problems.append(f"{eleve} non attribué")
                    nproblems_eleves[eleve] += 1
                    decision_data["Id"].append(eleve)
                    decision_data["Choice"].append(0)
                    decision_data["ChoiceWeight"].append(0)
                    duo_weight = 0
            else:
                duo_weight = weights_duo.product()

            # Retirer les membres du binôme de la pool d'affectation individuelle.
            weights[weights.index.intersection(eleves)] = 0
            if list(weights.index)!=list(candidats.index):
                assert 0
            if duo_weight:
                # Attribuer le poids combiné du binôme au représentant.
                weights[duo["Repr"]] = duo_weight

        n_candidats = len(weights[weights!=0]) 

        # Choisir les candidats selon les contraintes minimum/maximum.
        minimum = tm["Nombre minimal travaux"]
        if not pd.isna(minimum) and n_candidats<minimum:
            forced = candidats[weights==np.inf]
            if i_tm==16:
                pass
            if forced.empty:
                selected = default_df
                TM_non_ouverts.append(i_tm)
            else:
                selected = forced
                problems.append((i_tm,f"Pas assez : {len(forced)}<{minimum}"))
                nproblems_tm[i_tm] += 1
        elif maximum<n_candidats:
            forced_bool = weights==np.inf
            forced = candidats[forced_bool]
            if i_tm==4:
                pass
            if len(forced):
                pass
            weights[forced_bool] = 0 
            n_to_assign = maximum-len(forced)

            if n_to_assign>=0:
                selected2 = candidats.sample(maximum-len(forced),weights=weights,random_state=rng)
                selected = pd.concat([forced,selected2])
            else:
                problems.append((i_tm,f"Trop nombreux : {len(forced)}>{maximum}"))
                selected = forced
                nproblems_tm[i_tm] += 1
        else:
            if i_tm==4:
                pass
            selected = candidats[weights!=0]

        # Pour chaque candidat, indiquer s'il est sélectionné ou non et mettre à jour la grille.
        repr = duos["Repr"].values
        if 54 in duos["Repr"]:
            pass
        for nom_eleve_repr,eleve in candidats.iterrows():
            sel_duos = duos[duos["Repr"]==nom_eleve_repr]
            if sel_duos.empty:
                eleves = [nom_eleve_repr]
            else:
                assert len(sel_duos)==1,f"{len(sel_duos)} duos pour {nom_eleve_repr} TM {i_tm}"
                duo = sel_duos.iloc[0]
                eleves = duo["Eleves"]
            is_selected = nom_eleve_repr in selected.index.values
            for nom_eleve in eleves:
                if (nom_eleve=="33") and (i_tm==7):
                    pass
                if is_selected:
                    choice_weight = candidats.at[nom_eleve,str(i_tm)]
                    decision_data["Id"].append(nom_eleve)
                    decision_data["Choice"].append(i_tm)
                    decision_data["ChoiceWeight"].append(choice_weight)
                    df_grid.loc[nom_eleve] = np.nan # type: ignore
                    df_grid.at[nom_eleve,str(i_tm)] = choice_weight
                else:
                    df_grid.at[nom_eleve,str(i_tm)] = np.nan

    # Construire le DataFrame des décisions à partir des choix collectés.
    df_decision_data = pd.DataFrame(decision_data)
    for nom_eleve in df_grid.index:
        if nom_eleve not in decision_data["Id"]:
            print(f"Nom eleve: {nom_eleve}")

    if len(df_grid)==len(df_decision_data):
        # Affectation réussie : enregistrer les résultats et mettre à jour les métriques.
        df_decision_data.to_csv(f"{OUTPUT_DIR}/r{i_try}.csv",index=False)
        mean = df_decision_data["ChoiceWeight"].mean()
        std = df_decision_data["ChoiceWeight"].std()
        results["Id"].append(i_try)
        results["Mean"].append(mean)
        results["Std"].append(std)
        results["Problems"].append(problems)
        results["TMnonouverts"].append(TM_non_ouverts)
        print(f"Try {i_try}: mean={mean}, std={std}, problems={problems}, non ouverts={TM_non_ouverts}")
    else:
        # Si l'affectation est incomplète, afficher les diagnostics.
        print(len(df_grid))
        print(len(df_decision_data))
try:
    max_l2 = 0

    for _ in range(N_TRIES):
        l2 = generate()
        i_try += 1
finally:
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_FILE,index=False)
    nproblems_eleves.to_csv(NPROBLEMS_ELEVES_FILE)
    nproblems_tm.to_csv(NPROBLEMS_TM_FILE)
