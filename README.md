## Tinder Insights
:warning: The current version is only available in French.

:warning: `python3` et `pip` sont nécessaires :snake:

### How to
1. **Récupérer ses données Tinder**. Il suffit de se rendre [ici](https://account.gotinder.com/login?from=%2Fdata). Un email est envoyé en quelques jours avec le lien pour télécharger l'archive contenant les données. Elle contient un dossier avec les médias, un fichier `index.html` et un fichier `data.json`. Décompresser l'archive et remplacer le fichier `data.json` qui se trouve à la racine du repo.

:thought_balloon: un dummy dataset est cependant intégré au repo afin de pouvoir tester sans avoir à demander ses données.
 
2. Ouvrir un terminal et lancer `pip install -r requirements.txt`
3. Lancer `python app.py`
3. Ouvrir un navigateur et entrer l'adresse `http://127.0.0.1:8050/`
4. Enjoy :fire:
