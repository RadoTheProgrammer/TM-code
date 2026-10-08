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
