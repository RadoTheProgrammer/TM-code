
# ============================================================================
# Configuration des chemins et paramètres
# ============================================================================


import os
import random
import pandas as pd
import shutil
import numpy as np
import json

with open("settings.json", "r") as f:
    settings_data = json.load(f)
# ============================================================================
# Initialisation des données
# ============================================================================
rng = np.random.default_rng(settings_data["RANDOM_SEED"])  # Générateur aléatoire
np.random.seed(settings_data["RANDOM_SEED"])
df_grid_orig = pd.read_csv(settings_data["GRID_FILE"], index_col=0)  # Charger la grille originale
df_grid_orig.index = df_grid_orig.index.astype(str)  # Convertir les indices en chaînes
if os.path.exists(settings_data["NPROBLEMS_ELEVES_FILE"]):
    nproblems_eleves = pd.read_csv(settings_data["NPROBLEMS_ELEVES_FILE"], index_col=0).iloc[:,0]
    nproblems_eleves.index = nproblems_eleves.index.astype(str)
else:
    nproblems_eleves = pd.Series(0.0, index=df_grid_orig.index)  # Initialiser le compteur de problèmes pour chaque élève

default_df = pd.DataFrame()  # DataFrame vide pour les cas d'erreur

# Charger les travaux de maturité et supprimer le dernier (TM libre)
df_tm = pd.read_csv(settings_data["TM_FILE"], index_col=0)
#df_tm.index = df_tm.index.astype(str)
df_tm = df_tm.drop(df_tm[df_tm["Langue"]=="Libre"].index)  # Enlever les TMs libres


if os.path.exists(settings_data["NPROBLEMS_TM_FILE"]):
    nproblems_tm = pd.read_csv(settings_data["NPROBLEMS_TM_FILE"], index_col=0)

else:
    nproblems_tm = pd.DataFrame(0.0, index=df_tm.index, columns=["tropnombreux","pasassez"])
# Charger les binômes et traiter les données
df_duo = pd.read_csv(settings_data["DUO_FILE"])
df_duo["Eleves"] = df_duo["Eleves"].str.split(r" \+ ")  # Séparer les élèves en liste
df_duo["Repr"] = df_duo["Eleves"].str[0]  # Représentant = premier élève du binôme

# Initialiser les résultats

# Créer ou nettoyer le répertoire de résultats
if os.path.exists(settings_data["OUTPUT_DIR"]):
    i_try = len(os.listdir(settings_data["OUTPUT_DIR"]))-1
    
else:
    i_try = 0
    os.mkdir(settings_data["OUTPUT_DIR"])
if os.path.exists(settings_data["OUTPUT_FILE"]):
    results = pd.read_csv(settings_data["OUTPUT_FILE"])
else:
    results = None

def numpy_sample(population, weights, k, random_state):
    """
    Échantillonne k éléments de la population en utilisant les poids donnés.

    Args:
        population (list): Liste des éléments à échantillonner.
        weights (list): Liste des poids correspondants à chaque élément.
        k (int): Nombre d'éléments à échantillonner.
        random_state (int): Graine pour la reproductibilité.

    Returns:
        list: Liste des éléments échantillonnés.
    """
    return np.random.choice(population, size=k, replace=False, p=weights/np.sum(weights))
def generate_single():
    global max_l2,best_mean,best_std
    
    """Génère une tentative d'attribution pour tous les TMs.

    Cette fonction effectue un passage unique sur tous les travaux de maturité (TMs).
    Elle construit une liste de candidats pour chaque TM, calcule des poids, gère
    les affectations de binômes, sélectionne les élèves et enregistre les données.
    """

    # Copie de travail de la grille de préférences originale pour cette tentative.
    df_grid = df_grid_orig.copy()
    
    problems = {"nonattribue": [], "pasassez": [], "tropnombreux": []}
    TM_non_ouverts = []
    decision_data = {"Id": [], "Choice": [], "ChoiceWeight": []}

    # Parcourir les TMs dans un ordre aléatoire en utilisant le générateur fixe.
    # i_tm: int
    #print(nproblems_tm+1)

    def shuffle_tm():

        # u = np.random.random(len(df_tm))
        # keys = -np.log(u) / (nproblems_tm+1).to_numpy()

        # df_tm_shuffled = df_tm.iloc[np.argsort(keys)]
        # return df_tm_shuffled
        return df_tm.loc[numpy_sample(df_tm.index, nproblems_tm.sum(axis=1)+1, len(df_tm), rng)]
    def select_candidates():
        #selected_index = numpy_sample(candidats.index, weights, max(0, int(minimum-len(forced))), rng)
        selected_index = numpy_sample(candidats.index, weights, max(0, int(maximum-len(forced))), rng)
        # try:
        #     selected = numpy_sample(candidats.index, weights, max(0, int(minimum-len(forced))), rng)
        # # selected_unique = selected[~selected.index.duplicated(keep="first")]
        # # if len(selected_unique)<minimum-len(forced):
        # #     pass
        # #     problems.append((i_tm,f"Pas assez après duplication : {len(selected_unique)}<{minimum-len(forced)}"))
        # #     nproblems_tm[i_tm] += 1
        # except ValueError as e:
        #     if settings_data["FORCE_MIN"]:
        #         u = np.random.random(len(candidats))
        #         keys = -np.log(u) / (nproblems_tm+1).to_numpy()

        #         df_tm_shuffled = df_tm.iloc[np.argsort(keys)]
        #     problems.append((i_tm,"Impossible de sélectionner le nombre requis de candidats"))
        #     nproblems_tm[i_tm] += 1
        #     selected = default_df
        return candidats.loc[selected_index]
    i = 0

    # indexes = []
    # for eleve in df_grid.index:
    #     indexes.append(f"{eleve}_TM")
    #     indexes.append(f"{eleve}_Envie")
    data = pd.Series()
    for i_tm,tm in shuffle_tm().iterrows():

        # Colonne du TM courant et masque des candidats ayant une préférence positive.
        i_tm = int(i_tm) # type: ignore
        mask = df_grid[str(i_tm)] > 0

        candidats = df_grid[mask]
        
        # a: Score de préférence pour le TM courant
        # b: Somme des autres scores de TM.
        a = candidats[str(i_tm)]
        result1 = candidats.drop(columns=[str(i_tm)])
        b = result1.sum(axis=1)

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
                    problems["nonattribue"].append(f"{eleve} non attribué")
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
        if pd.isna(minimum):
            minimum = 0
        if n_candidats<minimum:
            forced = candidats[weights==np.inf]
            if i_tm==16:
                pass
            if forced.empty:
                selected = default_df
                TM_non_ouverts.append(i_tm)
            else:
                selected = forced
                problems["pasassez"].append((i_tm,f"Pas assez : {len(forced)}<{minimum}"))
                nproblems_tm.loc[i_tm, "pasassez"] = (
                    pd.to_numeric(nproblems_tm.loc[i_tm, "pasassez"], errors="coerce") + 1
                )
        elif maximum<n_candidats:
            forced_bool = weights==np.inf
            forced = candidats[forced_bool]
            if i_tm==4:
                pass
            if len(forced):
                pass
            weights[forced_bool] = 0 
            n_to_assign = maximum-len(forced)
            n_min_to_assign = minimum-len(forced)
            #print(maximum-len(forced))
            if n_to_assign>=0:
                selected2 = select_candidates()
                selected = pd.concat([forced,selected2])
            else:
                problems["tropnombreux"].append((i_tm,f"Trop nombreux : {len(forced)}>{maximum}"))
                weights_tm = nproblems_tm.sum(axis=1)+1
                prob = weights_tm[i_tm]/np.sum(weights_tm)
                print(problems["tropnombreux"][-1],i/len(df_tm),prob)
                selected = forced
                nproblems_tm.loc[i_tm, "tropnombreux"] = (
                    pd.to_numeric(nproblems_tm.loc[i_tm, "tropnombreux"], errors="coerce") + 1
                )
        else:
            if i_tm==4:
                pass
            selected = candidats[weights!=0]

        # Supprimer les éventuels doublons de candidats sélectionnés.
        selected = selected[~selected.index.duplicated(keep="first")]

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
                    envie = candidats.at[nom_eleve,str(i_tm)]
                    data[f"{nom_eleve}_TM"] = i_tm
                    data[f"{nom_eleve}_Envie"] = envie

                    df_grid.loc[nom_eleve] = np.nan # type: ignore
                    df_grid.at[nom_eleve,str(i_tm)] = envie
                else:
                    df_grid.at[nom_eleve,str(i_tm)] = np.nan
        i += 1
    # Construire le DataFrame des décisions à partir des choix collectés.

    if True:
        # Affectation réussie : enregistrer les résultats et mettre à jour les métriques.
        data_envie = data.filter(like="_Envie")
        mean = data_envie.mean()
        std = data_envie.std()
        data = data.sort_index()
        data["Idx"] = i_try
        data["Mean"] = mean
        data["Std"] = std
        data["Problems_nonattribue"] = len(problems["nonattribue"])
        data["Problems_pasassez"] = len(problems["pasassez"])
        data["Problems_tropnombreux"] = len(problems["tropnombreux"])
        data["TMnonouverts"] = TM_non_ouverts

        for n_envie in [1,2,3]:
            
            data[f"NbEnvie{n_envie}"] = (data[f"{n_envie}_Envie"]==n_envie).sum()
        print(f"Try {i_try}: mean={mean}, std={std}, non ouverts={TM_non_ouverts}, non attribués={len(problems['nonattribue'])}, pas assez={len(problems['pasassez'])}, trop nombreux={len(problems['tropnombreux'])}")

    else:
        # Si l'affectation est incomplète, afficher les diagnostics.
        print(len(df_grid))
        print(len(df_decision_data))

    return data
def generate(interface_object=None):
    global i_try,results
    try:
        max_l2 = 0
        while True:
            data = generate_single()
            data_framed = data.to_frame().T
            if results is None:
                results = data_framed
            else:
                results = pd.concat([results, data.to_frame().T], ignore_index=True)
            i_try += 1
            if interface_object is not None:
                interface_object.update_progress(i_try)
                if interface_object.stop_requested:
                    print("Arrêt demandé par l'utilisateur.")
                    break
    finally:
        if results is not None:
            results.to_csv(settings_data["OUTPUT_FILE"],index=False)
        nproblems_eleves.to_csv(settings_data["NPROBLEMS_ELEVES_FILE"])
        nproblems_tm.to_csv(settings_data["NPROBLEMS_TM_FILE"])
        print("Résultats sauvegardés dans les fichiers de sortie.")
        if interface_object is not None:
            interface_object.stop_requested = False
if __name__ == "__main__":
    generate()
