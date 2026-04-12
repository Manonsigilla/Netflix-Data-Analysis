"""
Netflix Dashboard - Application Streamlit

Affiche des visualisations interactives du catalogue Netflix
avec KPIs, analyses exploratoires et graphiques avancés.
"""

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from difflib import SequenceMatcher
from data_processing import load_and_clean_data, explode_column

# ==========================================
# FONCTIONS DE VISUALISATION RÉUTILISABLES
# ==========================================

def create_bar_chart(data, x, y, title, xlabel=None, ylabel=None, color_map=None, text_visible=True):
    """
    Graphique en barres simple
    
    Args:
        data : DataFrame
        x, y : Colonnes
        title : Titre du graphique
        xlabel, ylabel : Labels des axes
        color_map : Dictionnaire de couleurs
        text_visible : Afficher les valeurs sur les barres
    """
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        color=y if not color_map else x,
        text=y if text_visible else None,
        title=title
    )
    fig.update_layout(
        xaxis_title=xlabel if xlabel else x,
        yaxis_title=ylabel if ylabel else y,
        hovermode='x unified'
    )
    return fig

def create_grouped_bar_chart(data, x, y, color, title, xlabel=None, ylabel=None, color_map=None):
    """Graphique en barres groupées"""
    fig = px.bar(
        data, 
        x=x, 
        y=y, 
        color=color,
        barmode='group',
        title=title,
        color_discrete_map=color_map
    )
    fig.update_layout(
        xaxis_title=xlabel if xlabel else x,
        yaxis_title=ylabel if ylabel else y,
        hovermode='x unified'
    )
    return fig

def create_histogram(data, column, title, nbins=50, xlabel=None, ylabel=None):
    """Histogramme avec boîte à moustaches"""
    fig = px.histogram(
        data, 
        x=column, 
        nbins=nbins,
        marginal="box",
        title=title
    )
    fig.update_layout(
        xaxis_title=xlabel if xlabel else column,
        yaxis_title=ylabel if ylabel else "Fréquence"
    )
    return fig

# ==========================================
# CONFIGURATION ET CHARGEMENT
# ==========================================

st.set_page_config(page_title="Netflix Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data(ttl=3600)
def load_data():
    return load_and_clean_data('netflix_titles.csv')

df = load_data()

# ==========================================
# HEADER ET KPIs
# ==========================================

st.title("🍿 Netflix Insights : Analyse du Catalogue")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total des œuvres", value=f"{len(df):,}".replace(',', ' '))
with col2:
    nb_movies = len(df[df['type'] == 'Movie'])
    st.metric(label="Films", value=f"{nb_movies:,}".replace(',', ' '))
with col3:
    nb_tvshows = len(df[df['type'] == 'TV Show'])
    st.metric(label="Séries", value=f"{nb_tvshows:,}".replace(',', ' '))

st.markdown("---")

# ==========================================
# BARRE DE RECHERCHE INTELLIGENTE V2 - FINAL
# ==========================================

def calculate_similarity(a, b):
    """Calcule la similarité entre deux chaînes (0 à 1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_suggestions(search_term, df, max_suggestions=5):
    """Trouve les meilleures suggestions basées sur la recherche"""
    all_items = []
    
    # Chercher dans les titres
    for title in df['title'].unique():
        similarity = calculate_similarity(search_term, title)
        if similarity > 0.3:
            all_items.append({
                'type': 'Titre',
                'value': title,
                'similarity': similarity,
                'icon': '🎬'
            })
    
    # Chercher dans les réalisateurs
    directors = []
    for dir_list in df['director'].dropna():
        for director in str(dir_list).split(', '):
            if director not in directors:
                directors.append(director)
    
    for director in directors:
        similarity = calculate_similarity(search_term, director)
        if similarity > 0.3:
            all_items.append({
                'type': 'Réalisateur',
                'value': director,
                'similarity': similarity,
                'icon': '👤'
            })
    
    # Chercher dans les pays
    countries_set = set()
    for country in df['country'].dropna().unique():
        if pd.isna(country):
            continue
        for c in str(country).split(', '):
            countries_set.add(c)
    
    for country in countries_set:
        similarity = calculate_similarity(search_term, country)
        if similarity > 0.3:
            all_items.append({
                'type': 'Pays',
                'value': country,
                'similarity': similarity,
                'icon': '🌍'
            })
    
    # Chercher dans les genres
    genres = []
    for genre_list in df['listed_in'].dropna():
        for genre in str(genre_list).split(', '):
            if genre not in genres:
                genres.append(genre)
    
    for genre in genres:
        similarity = calculate_similarity(search_term, genre)
        if similarity > 0.3:
            all_items.append({
                'type': 'Genre',
                'value': genre,
                'similarity': similarity,
                'icon': '🎭'
            })
    
    # Trier par similarité
    all_items = sorted(all_items, key=lambda x: x['similarity'], reverse=True)
    return all_items[:max_suggestions]

# Interface de recherche
st.subheader("🔍 Rechercher une œuvre")

# Appliquer la suggestion si une a été cliquée
if 'new_search' in st.session_state and st.session_state.new_search:
    st.session_state.search_input = st.session_state.new_search
    st.session_state.new_search = ''

# Ligne 1 : Barre de recherche
col1, col2 = st.columns([3, 1])

with col1:
    search_input = st.text_input(
        "Entrez le titre, réalisateur, pays ou genre...",
        placeholder="Ex: Stranger Things, Spielberg, France, Drama",
        label_visibility="collapsed",
        key="search_input"
    )

with col2:
    st.caption("💡 Conseil : recherche fuzzy")

# Ligne 2 : Filtres
st.markdown("**Filtres (optionnels) :**")
fcol1, fcol2, fcol3, fcol4 = st.columns(4)

with fcol1:
    filter_type = st.multiselect(
        "Type",
        options=["Movie", "TV Show"] if "type" in df.columns else [],
        default=None,
        label_visibility="collapsed"
    )

with fcol2:
    filter_rating = st.multiselect(
        "Rating",
        options=sorted(df['rating'].dropna().unique()),
        default=None,
        label_visibility="collapsed"
    )

with fcol3:
    filter_year_range = st.slider(
        "Année de sortie",
        min_value=int(df['release_year'].min()),
        max_value=int(df['release_year'].max()),
        value=(int(df['release_year'].min()), int(df['release_year'].max())),
        label_visibility="collapsed"
    )

with fcol4:
    search_type = st.selectbox(
        "Chercher dans",
        options=["Tous", "Titres", "Réalisateurs", "Pays", "Genres"],
        label_visibility="collapsed"
    )

st.markdown("---")

# TRAITEMENT PRINCIPAL
if search_input and len(search_input) > 2:
    
    # Initialiser le dataframe filtrés
    results_df = df.copy()
    
    # Appliquer les filtres
    if filter_type:
        results_df = results_df[results_df['type'].isin(filter_type)]
    
    if filter_rating:
        results_df = results_df[results_df['rating'].isin(filter_rating)]
    
    results_df = results_df[
        (results_df['release_year'] >= filter_year_range[0]) &
        (results_df['release_year'] <= filter_year_range[1])
    ]
    
    # Recherche multi-colonnes avec OR logique
    if search_type == "Tous":
        title_matches = results_df[
            (results_df['title'].str.contains(search_input, case=False, na=False)) |
            (results_df['director'].str.contains(search_input, case=False, na=False)) |
            (results_df['country'].str.contains(search_input, case=False, na=False)) |
            (results_df['listed_in'].str.contains(search_input, case=False, na=False))
        ]
    elif search_type == "Titres":
        title_matches = results_df[results_df['title'].str.contains(search_input, case=False, na=False)]
    elif search_type == "Réalisateurs":
        title_matches = results_df[results_df['director'].str.contains(search_input, case=False, na=False)]
    elif search_type == "Pays":
        title_matches = results_df[results_df['country'].str.contains(search_input, case=False, na=False)]
    elif search_type == "Genres":
        title_matches = results_df[results_df['listed_in'].str.contains(search_input, case=False, na=False)]
    else:
        title_matches = pd.DataFrame()
    
    # Afficher les résultats
    if len(title_matches) > 0:
        st.success(f"✅ {len(title_matches)} résultat(s) trouvé(s)")
        st.markdown("---")
        
        for idx, row in title_matches.iterrows():
            # Créer 4 colonnes
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            # Colonne 1 : Titre et description
            with col1:
                st.write(f"**{row['title']}**")
                with st.expander("📖 Voir la description"):
                    st.write(row['description'])
            
            # Colonne 2 : Type
            with col2:
                st.write(f"**Type**")
                st.write(row['type'])
            
            # Colonne 3 : Année
            with col3:
                st.write(f"**Année**")
                st.write(int(row['release_year']))
            
            # Colonne 4 : Rating
            with col4:
                st.write(f"**Rating**")
                st.write(row['rating'] if pd.notna(row['rating']) else "N/A")
            
            st.markdown("---")
    
    else:
        # Pas de résultat, afficher suggestions
        suggestions = find_suggestions(search_input, df, max_suggestions=5)
        
        if suggestions:
            st.warning(f"⚠️ Aucune œuvre trouvée pour '{search_input}'")
            st.info("💡 **Suggestions** (cliquez sur le bouton pour rechercher) :")
            st.markdown("---")
            
            for i, suggestion in enumerate(suggestions, 1):
                similarity_percent = int(suggestion['similarity'] * 100)
                
                scol1, scol2 = st.columns([4, 1])
                
                with scol1:
                    st.write(f"{suggestion['icon']} **{suggestion['type']}** : `{suggestion['value']}` ({similarity_percent}% similaire)")
                
                with scol2:
                    if st.button("🔍 Chercher", key=f"suggestion_{i}_{suggestion['value']}"):
                        st.session_state.new_search = suggestion['value']
                        st.rerun()
            
            st.markdown("---")
        else:
            st.error(f"❌ Aucun résultat trouvé pour '{search_input}'")
            st.info("Essayez avec des termes moins spécifiques ou vérifiez l'orthographe")

elif search_input and len(search_input) <= 2:
    st.caption("⏳ Tapez au moins 3 caractères pour rechercher...")

st.markdown("---")

# ==========================================
# ONGLETS PRINCIPAUX
# ==========================================

tab1, tab2, tab3 = st.tabs(["📈 Évolution des ajouts", "🎭 Top Genres", "📊 Analyses de l'exercice"])

# --- ONGLET 1 : ÉVOLUTION DES AJOUTS ---
with tab1:
    st.subheader("Dynamique d'ajout au catalogue")
    df_trend = df.groupby(['year_added', 'type']).size().reset_index(name='count')
    
    fig_trend = px.line(
        df_trend, 
        x='year_added', 
        y='count', 
        color='type',
        labels={'year_added': "Année d'ajout", 'count': "Nombre d'œuvres", 'type': "Catégorie"},
        markers=True,
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'} 
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- ONGLET 2 : TOP GENRES ---
with tab2:
    st.subheader("Les 10 genres les plus représentés")
    
    plt.style.use('dark_background') 
    
    df_genres = explode_column(df, 'listed_in', 'genre')
    top_genres = df_genres['genre'].value_counts().head(10)
    
    fig_genres, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_genres.index, y=top_genres.values, color='mediumpurple', ax=ax)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Nombre d'occurrences")
    
    st.pyplot(fig_genres)

# ==========================================
# ONGLET 3 : ANALYSES OBLIGATOIRES
# ==========================================

with tab3:
    st.header("📊 Analyses obligatoires de l'exercice")
    st.write("Survolez les graphiques pour voir les détails exacts !")
    st.markdown("---")
    
    tab_a, tab_b, tab_c, tab_d, tab_e, tab_f, tab_h, tab_i, tab_j, tab_k = st.tabs([
    "🅰️ Type", 
    "🅱️ Pays", 
    "🅲 Années",
    "🅳 Ratings",
    "🅴 Durée Films", 
    "🅵 Saisons",
    "🅷 Top 5 Séries",
    "🅸 Top 5 Films",
    "🅹 Directors FR",
    "🅺 Évolution"
])

# --- TAB A : Type ---
with tab_a:
    st.subheader("a. Répartition du type d'œuvres")
    df_type = df['type'].value_counts().reset_index()
    df_type.columns = ['type', 'count']
    fig_a = create_bar_chart(df_type, x='type', y='count', title="Films vs Séries")
    st.plotly_chart(fig_a, use_container_width=True)

# --- TAB B : Pays ---
with tab_b:
    st.subheader("b. Top 10 des pays producteurs")
    df_pays = df.dropna(subset=['country'])['country'].value_counts().head(10).reset_index()
    df_pays.columns = ['country', 'count']
    fig_b = create_bar_chart(df_pays, x='country', y='count', title="Top 10 Pays")
    st.plotly_chart(fig_b, use_container_width=True)

# --- TAB C : Années (NOUVEAU) ---
with tab_c:
    st.subheader("c. Répartition des années (d'ajout au catalogue)")
    df_years = df['year_added'].dropna().value_counts().sort_index().reset_index()
    df_years.columns = ['year_added', 'count']
    fig_c = create_bar_chart(df_years, x='year_added', y='count', title="Années d'ajout")
    st.plotly_chart(fig_c, use_container_width=True)
    st.info("**Analyse :** Le catalogue a connu une croissance exponentielle entre 2015 et 2019.")

# --- TAB D : Ratings (NOUVEAU) ---
with tab_d:
    st.subheader("d. Répartition des ratings")
    df_ratings = df.dropna(subset=['rating'])['rating'].value_counts().reset_index()
    df_ratings.columns = ['rating', 'count']
    fig_d = create_bar_chart(df_ratings, x='rating', y='count', title="Distribution des ratings")
    st.plotly_chart(fig_d, use_container_width=True)
    st.info("**Analyse :** Netflix propose du contenu pour tous les publics, avec dominance des ratings adultes.")

# --- TAB E : Durée films ---
with tab_e:
    st.subheader("e. Répartition de la durée des films")
    df_movies = df[df['type'] == 'Movie'].copy()
    fig_e = create_histogram(df_movies, column='duration_num', title="Durée films", nbins=50)
    st.plotly_chart(fig_e, use_container_width=True)

# --- TAB F : Saisons ---
with tab_f:
    st.subheader("f. Répartition du nombre de saisons")
    df_shows = df[df['type'] == 'TV Show'].copy()
    df_shows_counts = df_shows['duration_num'].value_counts().reset_index().sort_values('duration_num')
    df_shows_counts.columns = ['saisons', 'count']
    fig_f = create_bar_chart(df_shows_counts, x='saisons', y='count', title="Saisons")
    st.plotly_chart(fig_f, use_container_width=True)

# --- TAB H : Top 5 séries (NOUVEAU) ---
with tab_h:
    st.subheader("h. Top 5 des séries les plus longues")
    df_tv = df[df['type'] == 'TV Show'].copy()
    top_5_shows = df_tv.nlargest(5, 'duration_num')[['title', 'duration_num']]
    fig_h = px.bar(top_5_shows, x='duration_num', y='title', orientation='h', title="Top 5 séries")
    st.plotly_chart(fig_h, use_container_width=True)

# --- TAB I : Top 5 films (NOUVEAU) ---
with tab_i:
    st.subheader("i. Top 5 des films les plus longs")
    df_mov = df[df['type'] == 'Movie'].copy()
    top_5_movies = df_mov.nlargest(5, 'duration_num')[['title', 'duration_num']]
    fig_i = px.bar(top_5_movies, x='duration_num', y='title', orientation='h', title="Top 5 films")
    st.plotly_chart(fig_i, use_container_width=True)

# --- TAB J : Directors français (NOUVEAU) ---
with tab_j:
    st.subheader("j. Top réalisateurs français")
    df_fr = df[df['country'].str.contains('France', na=False, case=False)].copy()
    df_fr_dir = df_fr.dropna(subset=['director']).copy()
    df_fr_dir['director'] = df_fr_dir['director'].str.split(', ')
    df_fr_dir = df_fr_dir.explode('director')
    top_fr = df_fr_dir['director'].value_counts().head(10).reset_index()
    top_fr.columns = ['director', 'count']
    fig_j = create_bar_chart(top_fr, x='count', y='director', title="Top réalisateurs FR")
    st.plotly_chart(fig_j, use_container_width=True)

# --- TAB K : Évolution ---
with tab_k:
    st.subheader("k. Évolution des ajouts par année")
    df_year = df.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig_k = create_grouped_bar_chart(df_year, x='year_added', y='count', color='type',
        title="Évolution", xlabel="Année d'ajout", ylabel="Nombre d'œuvres",
        color_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'})
    st.plotly_chart(fig_k, use_container_width=True)