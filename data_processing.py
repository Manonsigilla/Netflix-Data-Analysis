import pandas as pd
import sys

def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """
    Charge le dataset Netflix, nettoie les dates et crée de nouvelles features.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {filepath} n'a pas été trouvé.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de la lecture du CSV : {e}")
        sys.exit(1)
    
    try:
        # Traitement des dates avec gestion d'erreur
        df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), errors='coerce')
        
        # Garder les NaN pour les lignes sans date_added
        df['year_added'] = df['date_added'].dt.year
        # year_added reste en float64 (avec NaN pour les valeurs manquantes)
        
        df['wait_time_years'] = df['year_added'] - df['release_year']
        df.loc[df['wait_time_years'] < 0, 'wait_time_years'] = 0
        
        # Extraction durée
        df['duration_num'] = df['duration'].str.extract(r'(\d+)', expand=False).astype(float)
        
        # Assertions de validation
        assert len(df) > 0, "Le dataset est vide"
        assert 'type' in df.columns, "Colonne 'type' manquante"
        assert df['type'].isin(['Movie', 'TV Show']).all(), "Valeurs inattendues dans 'type'"
    
        return df
    except Exception as e:
        print(f"Erreur lors du nettoyage des données : {e}")
        sys.exit(1)

def explode_column(df: pd.DataFrame, column_name: str, new_column_name: str) -> pd.DataFrame:
    """
    Sépare les chaînes de caractères contenant des virgules en plusieurs lignes.
    
    Exemple :
    - Input : 'Action, Drama, Thriller'
    - Output : 3 lignes avec 'Action', 'Drama', 'Thriller' séparément
    
    Args:
        df : DataFrame source
        column_name : Colonne à exploser
        new_column_name : Nom de la colonne résultante
    
    Returns:
        DataFrame avec les valeurs explosées et NaN supprimés
    """
    df_exploded = df.dropna(subset=[column_name]).copy()
    # Séparation de la chaîne de caractères en une liste Python
    df_exploded[new_column_name] = df_exploded[column_name].str.split(', ')
    # La fonction magique de Pandas qui crée une ligne par élément de la liste
    return df_exploded.explode(new_column_name)