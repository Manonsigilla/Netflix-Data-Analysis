import pandas as pd

def load_and_clean_data(filepath: str) -> pd.DataFrame:
    """
    Charge le dataset Netflix, nettoie les dates et crée de nouvelles features.
    """
    df = pd.read_csv(filepath)
    
    # 1. Traitement des dates
    # On utilise .str.strip() pour enlever les espaces avant de convertir la date
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip())
    
    df['year_added'] = df['date_added'].dt.year
    
    # 2. Feature Engineering : Temps d'attente avant disponibilité sur Netflix
    df['wait_time_years'] = df['year_added'] - df['release_year']
    
    # Nettoyage basique (retrait des valeurs absurdes si la date d'ajout est antérieure à la sortie)
    df.loc[df['wait_time_years'] < 0, 'wait_time_years'] = 0 
    
    return df

def explode_column(df: pd.DataFrame, column_name: str, new_column_name: str) -> pd.DataFrame:
    """
    Sépare les chaînes de caractères contenant des virgules en plusieurs lignes.
    Idéal pour les colonnes 'listed_in' (genres) et 'cast' (acteurs).
    """
    df_exploded = df.dropna(subset=[column_name]).copy()
    # Séparation de la chaîne de caractères en une liste Python
    df_exploded[new_column_name] = df_exploded[column_name].str.split(', ')
    # La fonction magique de Pandas qui crée une ligne par élément de la liste
    return df_exploded.explode(new_column_name)