
# ============================================================================
# Configuration des chemins et paramètres
# ============================================================================


import os
import random
import pandas as pd
import shutil
import numpy as np
import json
from utils import settings_data
from tqdm import tqdm
# ============================================================================
# Initialisation des données
# ============================================================================
TM_WEIGHTS_MODE = False  # Mode de calcul des poids pour les TMs
ELEVES_WEIGHTS_MODE = False  # Mode de calcul des poids pour les élèves


data = {}

if settings_data["RANDOM_SEED"] is not None:
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

def numpy_sample(population, weights, k):
    """
    Échantillonne k éléments de la population en utilisant les poids donnés.

    Args:
        population (list): Liste des éléments à échantillonner.
        weights (list): Liste des poids correspondants à chaque élément.
        k (int): Nombre d'éléments à échantillonner.

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
    trace_sections = []

    # Parcourir les TMs dans un ordre aléatoire en utilisant le générateur fixe.
    # i_tm: int
    #print(nproblems_tm+1)

    def shuffle_tm():

        # u = np.random.random(len(df_tm))
        # keys = -np.log(u) / (nproblems_tm+1).to_numpy()

        # df_tm_shuffled = df_tm.iloc[np.argsort(keys)]
        # return df_tm_shuffled
        df_tm["weights"] = (nproblems_tm.sum(axis=1)+1)**settings_data["PUISSANCE_TM"]

        shuffled_indices = numpy_sample(df_tm.index, df_tm["weights"], len(df_tm))
        shuffled_tms = df_tm.loc[shuffled_indices]
        tm_trace = df_tm.copy()
        tm_trace["initial_shuffle_probability"] = tm_trace["weights"] / tm_trace["weights"].sum()
        tm_trace = tm_trace.rename(columns={"weights": "shuffle_weight"})
        tm_trace = tm_trace.loc[shuffled_indices].reset_index()
        tm_trace.insert(0, "shuffle_order", range(1, len(tm_trace) + 1))
        trace_sections.append(
            "TM shuffle weights (in actual shuffle order):\n"
            f"TM weight formula: {'(nproblems_tm.sum(axis=1) + 1) ** PUISSANCE_TM' if TM_WEIGHTS_MODE else '1 (TM weighting disabled)'}\n"
            "initial_shuffle_probability is the first-draw probability; draws are without replacement, "
            "so probabilities change after each TM is removed.\n"
            f"{tm_trace.to_string(index=False)}"
        )
        return shuffled_tms
    def select_candidates():
        #selected_index = numpy_sample(candidats.index, weights, max(0, int(minimum-len(forced))), rng)
        #print(weights.values)
        candidats["weights"] = weights**settings_data["PUISSANCE_ELEVE"]
        if i_tm==20:
            pass
        candidats2 =candidats.sort_values("weights",ascending=False)
        candidats2 = candidats2[candidats2["weights"]>0]
        #return candidats2.head(int(maximum-len(§forced)))
        selected_index = numpy_sample(candidats.index, candidats["weights"],int(maximum-len(forced)))
        

        if list(selected_index) == ['PERS_0141']:
                pass
        return candidats.loc[selected_index]
    student_trace_columns = [
        "candidate", "student", "duo_members", "a", "b", "a/b",
        "nproblems_eleves", "student_weight", "duo_weight", "candidate_weight", "sampling_weight",
        "sampling_probability", "isSelected", "selection_order", "reason",
    ]
    i = 0
    for i_tm,tm in shuffle_tm().iterrows():
        # Colonne du TM courant et masque des candidats ayant une préférence positive.
        i_tm = int(i_tm) # type: ignore
        #print(list(df_grid.columns))

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
        if settings_data["ELEVES_NPROBLEMS_MODE"] is None:
            weights = a/b
        elif settings_data["ELEVES_NPROBLEMS_MODE"].startswith("+"):
            weights = a/b+float(settings_data["ELEVES_NPROBLEMS_MODE"][1:])*(nproblems_eleves[candidats.index])
        elif settings_data["ELEVES_NPROBLEMS_MODE"].startswith("*"):
            weights = a/b*(nproblems_eleves[candidats.index]+1)**float(settings_data["ELEVES_NPROBLEMS_MODE"][1:])
        else:
            raise ValueError(f"Invalid ELEVES_NPROBLEMS_MODE: {settings_data['ELEVES_NPROBLEMS_MODE']}")
        individual_weights = weights.copy()
        duo_members_by_repr = {}
        duo_weights_by_repr = {}
        maximum = int(tm["Nombre maximal travaux"])

        # Gérer les poids des binômes et garantir que les membres sont affectés ensemble.
        for i_duo, duo in duos.iterrows():
            eleves = duo["Eleves"]

            weights_duo = weights.reindex(eleves,fill_value=0)
            duo_members_by_repr[duo["Repr"]] = eleves
            if i_tm==2 and eleves==['PERS_0164', 'PERS_0031']:
                pass
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
            duo_weights_by_repr[duo["Repr"]] = duo_weight

            # Retirer les membres du binôme de la pool d'affectation individuelle.
            weights[weights.index.intersection(eleves)] = 0
            if list(weights.index)!=list(candidats.index):
                assert 0
            if duo_weight:
                # Attribuer le poids combiné du binôme au représentant.
                weights[duo["Repr"]] = duo_weight

        candidate_weights = weights.copy()
        n_candidats = len(weights[weights!=0]) 

        # Choisir les candidats selon les contraintes minimum/maximum.
        minimum = tm["Nombre minimal travaux"]
        if pd.isna(minimum):
            minimum = 0
        forced_candidate_ids = set()
        sampled_weights = pd.Series(dtype=float)
        sampled_probabilities = pd.Series(dtype=float)
        selection_mode = ""
        if n_candidats<minimum:
            forced = candidats[weights==np.inf]
            forced_candidate_ids = set(forced.index)
            if i_tm==16:
                pass
            if forced.empty:
                selected = default_df
                TM_non_ouverts.append(i_tm)
                selection_mode = "TM not opened: minimum not met and no forced candidates"
            else:
                selected = forced
                selection_mode = "Only forced candidates selected: minimum not met"
                problems["pasassez"].append((i_tm,f"Pas assez : {len(forced)}<{minimum}"))
                nproblems_tm.loc[i_tm, "pasassez"] = (
                    pd.to_numeric(nproblems_tm.loc[i_tm, "pasassez"], errors="coerce") + 1
                )
        elif maximum<n_candidats:
            forced_bool = weights==np.inf
            forced = candidats[forced_bool]
            forced_candidate_ids = set(forced.index)
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
                sampled_weights = candidats["weights"].copy()
                sampled_probabilities = sampled_weights / sampled_weights.sum()
                selected = pd.concat([forced,selected2])
                selection_mode = f"Forced candidates plus weighted random draw of {n_to_assign}"
            else:
                problems["tropnombreux"].append((i_tm,f"Trop nombreux : {len(forced)}>{maximum}"))
                weights_tm = nproblems_tm.sum(axis=1)+1
                prob = weights_tm[i_tm]/np.sum(weights_tm)
                #print(problems["tropnombreux"][-1],i/len(df_tm),prob)
                selected = forced
                selection_mode = "Forced candidates exceed maximum; all forced candidates selected"
                nproblems_tm.loc[i_tm, "tropnombreux"] = (
                    pd.to_numeric(nproblems_tm.loc[i_tm, "tropnombreux"], errors="coerce") + 1
                )
        else:
            if i_tm==4:
                pass
            selected = candidats[weights!=0]
            selection_mode = "All candidates with non-zero weight selected (within maximum)"

        # Supprimer les éventuels doublons de candidats sélectionnés.
        selected = selected[~selected.index.duplicated(keep="first")]
        selection_order = {candidate: order for order, candidate in enumerate(selected.index, start=1)}
        if i_tm==2:
            pass
        # Pour chaque candidat, indiquer s'il est sélectionné ou non et mettre à jour la grille.
        repr = duos["Repr"].values
        if 54 in duos["Repr"]:
            pass
        tm_student_trace = {}
        for nom_eleve_repr,eleve in candidats.iterrows():
            sel_duos = duos[duos["Repr"]==nom_eleve_repr]
            if sel_duos.empty:
                eleves = [nom_eleve_repr]
            else:
                if len(sel_duos)!=1:
                    print(f"Attention : {len(sel_duos)} duos pour {nom_eleve_repr} TM {i_tm}")

                    eleves = [eleve for groupe in sel_duos["Eleves"] for eleve in groupe]
                duo = sel_duos.iloc[0]
                eleves = duo["Eleves"]
            is_selected = nom_eleve_repr in selected.index.values
            for nom_eleve in eleves:
                if (nom_eleve=="33") and (i_tm==7):
                    pass
                if is_selected:
                    choice_weight = candidats.at[nom_eleve,str(i_tm)]
                    if choice_weight==1:
                        #print(df_grid.loc[nom_eleve])
                        pass
                    decision_data["Id"].append(nom_eleve)
                    decision_data["Choice"].append(i_tm)
                    decision_data["ChoiceWeight"].append(choice_weight)
                    df_grid.loc[nom_eleve] = np.nan # type: ignore
                    df_grid.at[nom_eleve,str(i_tm)] = choice_weight
                else:
                    df_grid.at[nom_eleve,str(i_tm)] = np.nan
                trace_candidate = next(
                    (
                        repr_id
                        for repr_id, members in duo_members_by_repr.items()
                        if nom_eleve in members
                    ),
                    nom_eleve_repr,
                )
                student_a = a.get(nom_eleve, np.nan)
                student_b = b.get(nom_eleve, np.nan)
                student_is_selected = trace_candidate in selected.index
                is_forced = trace_candidate in forced_candidate_ids
                if student_is_selected:
                    if is_forced:
                        selection_reason = "Selected as a forced candidate (infinite weight)"
                    elif trace_candidate in sampled_weights.index:
                        selection_reason = "Selected by weighted random draw"
                    else:
                        selection_reason = selection_mode
                elif selection_mode.startswith("TM not opened"):
                    selection_reason = selection_mode
                elif selection_mode.startswith("Forced candidates exceed"):
                    selection_reason = "Not selected: forced candidates exceeded the maximum"
                elif selection_mode.startswith("Only forced"):
                    selection_reason = "Not selected: only forced candidates could be assigned"
                elif sampled_weights.size:
                    if candidate_weights.get(trace_candidate, 0) == 0:
                        selection_reason = "Not selected: zero effective weight (excluded from weighted draw)"
                    else:
                        selection_reason = "Not selected by weighted random draw (capacity limit)"
                elif candidate_weights.get(trace_candidate, 0) == 0:
                    selection_reason = "Not selected: zero effective weight"
                else:
                    selection_reason = selection_mode
                tm_student_trace[nom_eleve] = {
                    "candidate": trace_candidate,
                    "student": nom_eleve,
                    "duo_members": " + ".join(duo_members_by_repr.get(trace_candidate, [])),
                    "a": student_a,
                    "b": student_b,
                    "a/b": student_a / student_b if student_b != 0 else np.inf,
                    "nproblems_eleves": nproblems_eleves.get(nom_eleve, np.nan),
                    "student_weight": individual_weights.get(nom_eleve, 0),
                    "duo_weight": duo_weights_by_repr.get(trace_candidate, ""),
                    "candidate_weight": candidate_weights.get(trace_candidate, 0),
                    "sampling_weight": sampled_weights.get(trace_candidate, ""),
                    "sampling_probability": sampled_probabilities.get(trace_candidate, ""),
                    "isSelected": student_is_selected,
                    "selection_order": selection_order.get(trace_candidate, ""),
                    "reason": selection_reason,
                }
        trace_sections.append(
            f"\nTM {i_tm} - {tm.get('Maître c', '')} - {tm.get('Langue', '')}\n"
            f"Selection rule: {selection_mode}; minimum={minimum}, maximum={maximum}, "
            f"candidates with non-zero weight={n_candidats}, forced={len(forced_candidate_ids)}.\n"
            "For each student: a = current TM preference; b = sum of remaining TM preferences; "
            "a/b = base ratio. student_weight is a/b, optionally multiplied by "
            "(nproblems_eleves[student] + 1) when student weighting is enabled. "
            "For a duo, duo_weight is the product of member weights and candidate_weight is "
            "assigned to the representative; sampling_weight is candidate_weight raised to "
            "PUISSANCE_ELEVE when a weighted draw is used. sampling_probability is the "
            "initial probability for that draw; selected candidates are sampled without "
            "replacement, so later probabilities change. selection_order shows assignment order.\n"
            f"{pd.DataFrame.from_records(list(tm_student_trace.values()), columns=student_trace_columns).to_string(index=False)}"
        )
        i += 1
    # Construire le DataFrame des décisions à partir des choix collectés.
    df_decision_data = pd.DataFrame(decision_data)
    for nom_eleve in df_grid.index:
        if nom_eleve not in decision_data["Id"]:
            print(f"Nom eleve: {nom_eleve}")

    result_number = 0 if results is None else len(results)
    trace_path = os.path.join(settings_data["OUTPUT_DIR"], f"r{result_number}.txt")
    with open(trace_path, "w", encoding="utf-8") as trace_file:
        trace_file.write("\n\n".join(trace_sections))

    if len(df_grid)==len(df_decision_data):
        # Affectation réussie : enregistrer les résultats et mettre à jour les métriques.
        df_decision_data.to_csv(f"{settings_data['OUTPUT_DIR']}/r{result_number}.csv",index=False)
        mean = df_decision_data["ChoiceWeight"].mean()
        std = df_decision_data["ChoiceWeight"].std()
        data["Mean"]=(mean)
        data["Std"]=(std)
        data["Problems_nonattribue"]=(len(problems["nonattribue"]))
        data["Problems_pasassez"]=(len(problems["pasassez"]))
        data["Problems_tropnombreux"]=(len(problems["tropnombreux"]))
        data["TMnonouverts"]=(TM_non_ouverts)
        for n_envie in [1,2,3]:
            
            data[f"NbEnvie{n_envie}"] = (df_decision_data["ChoiceWeight"]==n_envie).mean()
        #print(f"Try {i_try}: mean={mean}, std={std}, non ouverts={TM_non_ouverts}, non attribués={len(problems['nonattribue'])}, pas assez={len(problems['pasassez'])}, trop nombreux={len(problems['tropnombreux'])}")

    else:
        # Si l'affectation est incomplète, afficher les diagnostics.
        raise ValueError(f"Erreur : le nombre d'élèves dans la grille ({len(df_grid)}) ne correspond pas au nombre d'élèves dans les décisions ({len(df_decision_data)}).")
        print(len(df_grid))
        print(len(df_decision_data))

    return pd.Series(data)
def generate_puissance_eleve(interface_object=None):
    global results
    data_params = {"PUISSANCE_ELEVE": [], "Mean": [], "Std": [], "Problems_nonattribue": [], "Problems_pasassez": [], "Problems_tropnombreux": [], "NEnvie1": [], "NEnvie2": [], "NEnvie3": []}
    for puissance_eleve in np.linspace(10,30,5):
        print(f"Puissance élève: {puissance_eleve}")
        settings_data["PUISSANCE_ELEVE"] = puissance_eleve
        results = None
        for i_try in range(100):
            
            random_seed = len(results) if results is not None else 0
            #random_seed = 25731
            print(f"Essai {i_try} avec random_seed={random_seed}")
            np.random.seed(random_seed)
            data_single = generate_single()
            data_framed =  data_single.to_frame().T
            if results is None:
                results = data_framed
            else:
                results = pd.concat([results, data_framed], ignore_index=True)
            results.to_csv(settings_data["OUTPUT_FILE"],index=False)
            nproblems_eleves.to_csv(settings_data["NPROBLEMS_ELEVES_FILE"])
            nproblems_tm.to_csv(settings_data["NPROBLEMS_TM_FILE"])
            if interface_object is not None:
                interface_object.update_progress(data_single)
                if interface_object.stop_requested:
                    print("Arrêt demandé par l'utilisateur.")
                    interface_object.stop_requested=False
                    break
        assert results is not None
        data_params["PUISSANCE_ELEVE"].append(puissance_eleve)
        data_params["Mean"].append(results["Mean"].mean())
        data_params["Std"].append(results["Std"].mean())
        data_params["Problems_nonattribue"].append(results["Problems_nonattribue"].mean())
        data_params["Problems_pasassez"].append(results["Problems_pasassez"].mean())
        data_params["Problems_tropnombreux"].append(results["Problems_tropnombreux"].mean())
        data_params["NEnvie1"].append(results["NbEnvie1"].mean())
        data_params["NEnvie2"].append(results["NbEnvie2"].mean())
        data_params["NEnvie3"].append(results["NbEnvie3"].mean())  

        df = pd.DataFrame(data_params)
        df.to_csv(f"{settings_data['OUTPUT_DIR']}/summary.csv",index=False) 

def generate_puissance_tm(interface_object=None):
    global results
    data_params = {"PUISSANCE_TM": [], "PUISSANCE_ELEVE": [], "Mean": [], "Std": [], "Problems_nonattribue": [], "Problems_pasassez": [], "Problems_tropnombreux": [], "NEnvie1": [], "NEnvie2": [], "NEnvie3": []}
    
    for puissance_tm in np.linspace(0,2,10):
        for puissance_eleve in np.linspace(15,30,15):
            print(f"Puissance TM: {puissance_tm}, Puissance élève: {puissance_eleve}")
            settings_data["PUISSANCE_TM"] = puissance_tm
            settings_data["PUISSANCE_ELEVE"] = puissance_eleve
            results = None
            for i_try in tqdm(range(100), desc="Generating data"):
                
                random_seed = len(results) if results is not None else 0
                #random_seed = 25731
                #print(f"Essai {i_try} avec random_seed={random_seed}")
                np.random.seed(random_seed)
                data_single = generate_single()
                data_framed =  data_single.to_frame().T
                if results is None:
                    results = data_framed
                else:
                    results = pd.concat([results, data_framed], ignore_index=True)
                results.to_csv(settings_data["OUTPUT_FILE"],index=False)
                nproblems_eleves.to_csv(settings_data["NPROBLEMS_ELEVES_FILE"])
                nproblems_tm.to_csv(settings_data["NPROBLEMS_TM_FILE"])
                if interface_object is not None:
                    interface_object.update_progress(data_single)
                    if interface_object.stop_requested:
                        print("Arrêt demandé par l'utilisateur.")
                        interface_object.stop_requested=False
                        break
            assert results is not None
            data_params["PUISSANCE_TM"].append(puissance_tm)
            data_params["PUISSANCE_ELEVE"].append(puissance_eleve)
            data_params["Mean"].append(results["Mean"].mean())
            data_params["Std"].append(results["Std"].mean())
            data_params["Problems_nonattribue"].append(results["Problems_nonattribue"].mean())
            data_params["Problems_pasassez"].append(results["Problems_pasassez"].mean())
            data_params["Problems_tropnombreux"].append(results["Problems_tropnombreux"].mean())
            data_params["NEnvie1"].append(results["NbEnvie1"].mean())
            data_params["NEnvie2"].append(results["NbEnvie2"].mean())
            data_params["NEnvie3"].append(results["NbEnvie3"].mean())  

    df = pd.DataFrame(data_params)
    df.to_csv(f"puissances-params.csv",index=False) 

def generate_nproblems(interface_object=None):
    global results
    settings_data["OUTPUT_DIR"] = "results-nproblems"
    settings_data["OUTPUT_FILE"] = "results-nproblems/o.csv"
    for nproblems_eleves_mode in [None,"*0","*1"]:
        settings_data["ELEVES_NPROBLEMS_MODE"] = nproblems_eleves_mode
        for i_try in tqdm(range(20), desc="Generating data"):
            
            random_seed = i_try
            #random_seed = 25731
            #print(f"Essai {i_try} avec random_seed={random_seed}")
            np.random.seed(random_seed)
            data_single = generate_single()
            data_single["ELEVES_NPROBLEMS_MODE"] = nproblems_eleves_mode
            data_framed =  data_single.to_frame().T
            
            if results is None:
                results = data_framed
            else:
                results = pd.concat([results, data_framed], ignore_index=True)
            results.to_csv(settings_data["OUTPUT_FILE"],index=False)
            nproblems_eleves.to_csv(settings_data["NPROBLEMS_ELEVES_FILE"])
            nproblems_tm.to_csv(settings_data["NPROBLEMS_TM_FILE"])
            if interface_object is not None:
                interface_object.update_progress(data_single)
                if interface_object.stop_requested:
                    print("Arrêt demandé par l'utilisateur.")
                    interface_object.stop_requested=False
                    break
        assert results is not None

generate = generate_nproblems
if __name__ == "__main__":
    generate()
