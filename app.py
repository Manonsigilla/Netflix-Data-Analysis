"""
Netflix Dashboard - Application Streamlit

Affiche des visualisations interactives du catalogue Netflix
avec KPIs, analyses exploratoires et graphiques avancés.
"""

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
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
    
    tab_a, tab_b, tab_e, tab_f, tab_k = st.tabs([
        "🅰️ Répartition Type", 
        "🅱️ Top Pays", 
        "🅴 Durée Films", 
        "🅵 Saisons Séries", 
        "🅺 Évolution Ajouts"
    ])
    
    # --- TAB A : Répartition type ---
    with tab_a:
        st.subheader("a. Répartition du type d'œuvres (Films vs Séries)")
        
        df_type = df['type'].value_counts().reset_index()
        df_type.columns = ['type', 'count']
        
        fig_a = create_bar_chart(
            df_type,
            x='type',
            y='count',
            title="Répartition Films vs Séries",
            xlabel="Type",
            ylabel="Nombre d'œuvres",
            color_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'}
        )
        st.plotly_chart(fig_a, use_container_width=True)
        
        st.info("**Interprétation :** Le catalogue de Netflix est historiquement et majoritairement composé de films (environ 70%). Bien que Netflix produise de plus en plus de séries originales, l'achat de droits de diffusion pour les films maintient cette domination.")

    # --- TAB B : Top pays ---
    with tab_b:
        st.subheader("b. Top 10 des pays producteurs")
        
        df_pays = df.dropna(subset=['country'])['country'].value_counts().head(10).reset_index()
        df_pays.columns = ['country', 'count']
        
        fig_b = create_bar_chart(
            df_pays,
            x='country',
            y='count',
            title="Top 10 Pays Producteurs",
            xlabel="Pays",
            ylabel="Nombre d'œuvres"
        )
        st.plotly_chart(fig_b, use_container_width=True)
        
        st.info("**Interprétation :** Sans surprise, les États-Unis dominent largement le marché. La deuxième place de l'Inde est remarquable et souligne la stratégie d'expansion de Netflix sur le marché très prolifique de Bollywood.")

    # --- TAB E : Durée films ---
    with tab_e:
        st.subheader("e. Répartition de la durée des films")
        
        df_movies = df[df['type'] == 'Movie'].copy()
        
        fig_e = create_histogram(
            df_movies,
            column='duration_num',
            title="Distribution de la durée des films",
            nbins=50,
            xlabel="Durée (minutes)",
            ylabel="Nombre de films"
        )
        st.plotly_chart(fig_e, use_container_width=True)
        
        st.info("**Interprétation :** La distribution suit une courbe en cloche (normale) très classique. La grande majorité des films durent entre 90 et 110 minutes (1h30 à 1h50), ce qui correspond au format standard de l'industrie cinématographique.")

    # --- TAB F : Saisons séries ---
    with tab_f:
        st.subheader("f. Répartition du nombre de saisons des séries")
        
        df_shows = df[df['type'] == 'TV Show'].copy()
        
        df_shows_counts = df_shows['duration_num'].value_counts().reset_index().sort_values('duration_num')
        df_shows_counts.columns = ['saisons', 'count']
        
        fig_f = create_bar_chart(
            df_shows_counts,
            x='saisons',
            y='count',
            title="Distribution du nombre de saisons",
            xlabel="Nombre de saisons",
            ylabel="Nombre de séries"
        )
        fig_f.update_xaxes(tickmode='linear')
        st.plotly_chart(fig_f, use_container_width=True)
        
        st.info("**Interprétation :** On observe une chute drastique après la saison 1. Cela s'explique par deux facteurs : l'abondance de 'mini-séries' conçues pour une seule saison, et la politique stricte de Netflix qui annule rapidement les séries si les audiences de la première saison ne sont pas au rendez-vous.")

    # --- TAB K : Évolution ajouts ---
    with tab_k:
        st.subheader("k. Évolution des ajouts au catalogue par année")
        
        df_year = df.groupby(['year_added', 'type']).size().reset_index(name='count')
        
        fig_k = create_grouped_bar_chart(
            df_year,
            x='year_added',
            y='count',
            color='type',
            title="Évolution des ajouts par année",
            xlabel="Année d'ajout",
            ylabel="Nombre d'œuvres ajoutées",
            color_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'}
        )
        st.plotly_chart(fig_k, use_container_width=True)
        
        st.info("**Interprétation :** On observe une croissance exponentielle des ajouts de 2015 à 2019, marquant l'âge d'or de l'expansion mondiale de Netflix. La légère baisse amorcée après 2019/2020 peut s'expliquer par les retards de production liés au COVID-19 et par un changement de stratégie privilégiant la qualité à la quantité face à une concurrence accrue.")