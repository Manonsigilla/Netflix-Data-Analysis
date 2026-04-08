# 🎬 Netflix Data Analysis

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Manipulation-orange.svg)
![Seaborn](https://img.shields.io/badge/Seaborn-Data_Visualization-lightgrey.svg)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626.svg)

## 📌 Contexte du projet
Ce projet consiste en une analyse exploratoire de données (EDA) du catalogue Netflix. L'objectif est de nettoyer, transformer et analyser un jeu de données contenant les films et séries de la plateforme afin d'en extraire des tendances (types de contenus, pays producteurs, évolution des ajouts, etc.).

## 🛠️ Stack Technique
- **Langage :** Python 3
- **Environnement :** Jupyter Notebook (Anaconda)
- **Librairies :** Pandas, NumPy, Matplotlib, Seaborn, Missingno

## 🚀 Installation & Exécution

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone [https://github.com/TonPseudo/Netflix-Data-Analysis.git](https://github.com/TonPseudo/Netflix-Data-Analysis.git)
   cd Netflix-Data-Analysis
   ```

2. Assurez-vous d'avoir les dépendances requises installées :
  ```bash
  pip install pandas numpy matplotlib seaborn missingno
  ```
   
3. Lancez Jupyter Notebook et ouvrez le fichier d'analyse :

   ```bash
   jupyter notebook NetflixDataAnalysis.ipynb
   ```

## 📊 Principaux Résultats & Visualisations

Suite au nettoyage des données (traitement des valeurs manquantes, formatage des dates et durées), plusieurs axes ont été explorés.
1. Répartition du type de contenu

Le catalogue est historiquement et majoritairement orienté vers les formats longs (Films) au détriment des Séries.
2. Évolution des ajouts sur la plateforme

On observe une croissance exponentielle des ajouts au catalogue à partir de 2017/2018, marquant le changement de stratégie de Netflix vers la production de contenu original.
3. Top des pays producteurs

Les États-Unis et l'Inde dominent largement la production des œuvres présentes sur la plateforme.

## 📂 Structure du projet

```text
📦 Netflix-Data-Analysis
 ┣ 📜 NetflixDataAnalysis.ipynb  # Notebook principal contenant l'EDA
 ┣ 📜 netflix_titles.csv         # Dataset original
 ┣ 📜 README.md                  # Documentation du projet
 ┣ 🖼️ Assets                     # Export graphique
```

