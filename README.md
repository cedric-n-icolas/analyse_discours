Analyses des fréquences des mots dans les discours et interviews des présidents de la république française
En utilisant le site open data https://www.vie-publique.fr/ qui contient sur cette page, la liste de toutes les interventions publiques orales ou écrites des 6 derniers présidents de la république française, soit près de 150 000 discours, articles, conférences, interviews, etc.



Usage : 
python scrap_discours.py <nom président> <taille max à analyser>  #va créer un fichier contenant une sélection de conférences de presse, interviews, déclarations dont l'auteur est le nom d'un des présidents de la république française depuis 1974.

python count_french_words.py <nom du fichier à analyser> #va lemmatiser et compter les mots français présents dans le fichier passé en paramètre. Affiche les 100 premiers mots utilisés.

Exemple :

Emmanuel Macron (2017-2024)
Nombre de mots français différents: 8785
+----------------+-----------+
|      Mot       | Fréquence |
+----------------+-----------+
|     faire      |   2190    |
|     aller      |   1550    |
|    pouvoir     |   1422    |
|    vouloir     |    973    |
|     devoir     |    961    |
|    beaucoup    |    918    |
|      pays      |    788    |
|    européen    |    787    |
|   permettre    |    711    |
|    français    |    711    |
|     année      |    669    |
