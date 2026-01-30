from itertools import cycle

serveurs = cycle(["S1", "S2", "S3"])

def attribuer_tache(tache):
    serveur = next(serveurs)
    print(f"{tache} → {serveur}")
