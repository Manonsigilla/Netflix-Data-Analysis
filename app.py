import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from data_processing import load_and_clean_data, explode_column

# 1. Configuration de la page (Doit toujours être en premier)
st.set_page_config(page_title="Netflix Dashboard", layout="wide", initial_sidebar_state="expanded")

# 2. Chargement des données
@st.cache_data
def load_data():
    return load_and_clean_data('netflix_titles.csv')

df = load_data()

# ==========================================
# HEADER ET KPIs (Pour le look "Dashboard")
# ==========================================
st.title("🍿 Netflix Insights : Analyse du Catalogue")
st.markdown("---")

# Création de 3 colonnes pour afficher des chiffres clés
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total des œuvres", value=f"{len(df):,}")
with col2:
    nb_movies = len(df[df['type'] == 'Movie'])
    st.metric(label="Films", value=f"{nb_movies:,}")
with col3:
    nb_tvshows = len(df[df['type'] == 'TV Show'])
    st.metric(label="Séries", value=f"{nb_tvshows:,}")

st.markdown("---")

# ==========================================
# ONGLETS DE NAVIGATION (Le côté "Moderne")
# ==========================================
tab1, tab2, tab3 = st.tabs(["📈 Évolution des ajouts", "🎭 Top Genres", "📊 Analyses de l'exercice"])

# --- ONGLET 1 : PLOTLY (Graphique interactif) ---
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
        # On remplace le noir par un gris très clair pour le Dark Mode
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'} 
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- ONGLET 2 : SEABORN / MATPLOTLIB ---
with tab2:
    st.subheader("Les 10 genres les plus représentés")
    
    # On force matplotlib à utiliser un thème compatible avec le dark mode
    plt.style.use('dark_background') 
    
    df_genres = explode_column(df, 'listed_in', 'genre')
    top_genres = df_genres['genre'].value_counts().head(10)
    
    # On crée une figure Matplotlib explicite
    fig_genres, ax = plt.subplots(figsize=(10, 5))
    
    # On dessine avec Seaborn sur cette figure
    sns.barplot(x=top_genres.index, y=top_genres.values, color='mediumpurple', ax=ax)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Nombre d'occurrences")
    
    # Au lieu de plt.show(), on l'envoie à Streamlit
    st.pyplot(fig_genres)

# ==========================================
# --- ONGLET 3 : ANALYSES OBLIGATOIRES ---
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
    
    # --- SOUS-ONGLET A : Répartition type ---
    with tab_a:
        st.subheader("a. Répartition du type d'œuvres (Films vs Séries)")
        
        df_type = df['type'].value_counts().reset_index()
        df_type.columns = ['type', 'count']
        
        fig_a = px.bar(df_type, x='type', y='count', color='type', text='count',
                        color_discrete_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'})
        st.plotly_chart(fig_a, use_container_width=True)
        
        st.info("**Interprétation :** Le catalogue de Netflix est historiquement et majoritairement composé de films (environ 70%). Bien que Netflix produise de plus en plus de séries originales, l'achat de droits de diffusion pour les films maintient cette domination.")

    # --- SOUS-ONGLET B : Top 10 pays ---
    with tab_b:
        st.subheader("b. Top 10 des pays producteurs")
        
        df_pays = df['country'].value_counts().head(10).reset_index()
        df_pays.columns = ['country', 'count']
        
        fig_b = px.bar(df_pays, x='country', y='count', color='count', color_continuous_scale='Reds')
        st.plotly_chart(fig_b, use_container_width=True)
        
        st.info("**Interprétation :** Sans surprise, les États-Unis dominent largement le marché. La deuxième place de l'Inde est remarquable et souligne la stratégie d'expansion de Netflix sur le marché très prolifique de Bollywood.")

    # --- SOUS-ONGLET E : Durée films ---
    with tab_e:
        st.subheader("e. Répartition de la durée des films")
        
        df_movies = df[df['type'] == 'Movie'].copy()
        df_movies['duration_num'] = df_movies['duration'].astype(str).str.extract(r'(\d+)').astype(float)
        
        fig_e = px.histogram(df_movies, x='duration_num', nbins=50, 
                            color_discrete_sequence=['#5DADE2'], marginal="box")
        fig_e.update_layout(xaxis_title="Durée (minutes)", yaxis_title="Nombre de films")
        st.plotly_chart(fig_e, use_container_width=True)
        
        st.info("**Interprétation :** La distribution suit une courbe en cloche (normale) très classique. La grande majorité des films durent entre 90 et 110 minutes (1h30 à 1h50), ce qui correspond au format standard de l'industrie cinématographique.")

    # --- SOUS-ONGLET F : Saisons séries ---
    with tab_f:
        st.subheader("f. Répartition du nombre de saisons des séries")
        
        df_shows = df[df['type'] == 'TV Show'].copy()
        df_shows['duration_num'] = df_shows['duration'].astype(str).str.extract(r'(\d+)').astype(float)
        
        df_shows_counts = df_shows['duration_num'].value_counts().reset_index().sort_values('duration_num')
        df_shows_counts.columns = ['saisons', 'count']
        
        fig_f = px.bar(df_shows_counts, x='saisons', y='count', color='count', color_continuous_scale='Viridis')
        fig_f.update_layout(xaxis_title="Nombre de saisons", yaxis_title="Nombre de séries")
        # On force les abscisses à afficher tous les nombres proprement (1, 2, 3...)
        fig_f.update_xaxes(tickmode='linear') 
        st.plotly_chart(fig_f, use_container_width=True)
        
        st.info("**Interprétation :** On observe une chute drastique après la saison 1. Cela s'explique par deux facteurs : l'abondance de 'mini-séries' conçues pour une seule saison, et la politique stricte de Netflix qui annule rapidement les séries si les audiences de la première saison ne sont pas au rendez-vous.")

    # --- SOUS-ONGLET K : Évolution ajouts ---
    with tab_k:
        st.subheader("k. Évolution des ajouts au catalogue par année")
        
        df_year = df.groupby(['year_added', 'type']).size().reset_index(name='count')
        
        fig_k = px.bar(df_year, x='year_added', y='count', color='type', barmode='group',
                        color_discrete_map={'Movie': '#E50914', 'TV Show': '#F5F5F1'})
        fig_k.update_layout(xaxis_title="Année d'ajout", yaxis_title="Nombre d'œuvres ajoutées")
        st.plotly_chart(fig_k, use_container_width=True)
        
        st.info("**Interprétation :** On observe une croissance exponentielle des ajouts de 2015 à 2019, marquant l'âge d'or de l'expansion mondiale de Netflix. La légère baisse amorcée après 2019/2020 peut s'expliquer par les retards de production liés au COVID-19 et par un changement de stratégie privilégiant la qualité à la quantité face à une concurrence accrue (Disney+, Prime, etc.).")