# TM Allocator
## exécuter le code en développement
Installer python et git si pas déjà fait.

Lancer dans le terminal
```
git clone https://github.com/RadoTheProgrammer/TM-code -b main2
```

Installer les modules nécessaire
```
cd TM-code
pip install -r requirements.txt
```

Executer le fichier `interface.py`
```
python ./interface.py
```

## Créer l'exécutable Windows

Installez Python 3 et vérifiez que le lanceur Windows `py` (ou la commande
`python`) est disponible. Ensuite, double-cliquez sur `build_exe.bat` à la
racine du projet.git clone https://github.com/RadoTheProgrammer/TM-code -b 

Le script installe les dépendances de l'application et PyInstaller, puis crée
`dist\TM-Allocator.exe`. Une connexion Internet est nécessaire pour installer
les dépendances. Relancez le même script après toute modification du code pour
reconstruire l'exécutable.

Pour chaque tentative, l'algorithme enregistre aussi un fichier `rN.txt` dans
le répertoire de résultats, à côté du `rN.csv` correspondant. Ce rapport indique
l'ordre de mélange des TMs et leurs poids, puis détaille pour chaque TM les
valeurs `a`, `b`, le calcul des poids des élèves (y compris les binômes), et
les sélections avec leur ordre et leur raison.

## Générer le graphe des préférences

Exécutez `python create_graph.py` pour créer `grid.dot` à côté du fichier de
grille configuré dans `settings_data` (`GRID_FILE`). Le fichier DOT contient
les élèves, les TMs, leurs relations colorées selon l'envie (1 vert, 2 bleu,
3 rouge), ainsi qu'un noeud spécial pour chaque duo et une légende des
capacités minimales et maximales de chaque TM.
