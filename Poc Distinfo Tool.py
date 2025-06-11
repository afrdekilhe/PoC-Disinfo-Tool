import streamlit as st
import json
import re
import pandas as pd
import os
import matplotlib.pyplot as plt

# Fonction pour charger les données
@st.cache_data # Mise en cache des données
def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Titre de l'application Streamlit
st.title("Analyse de comptes (à adapter)") # Vous pouvez changer ce titre

# Sidebar pour l'upload du fichier
uploaded_file = st.sidebar.file_uploader("Chargez votre fichier JSON", type="json")

if uploaded_file is not None:
    # Sauvegarder temporairement le fichier pour le lire
    with open("uploaded_dataset.json", "wb") as f:
        f.write(uploaded_file.getbuffer())
    file_path = "uploaded_dataset.json"

    data = load_data(file_path)

    # Section "Suspicious accounts"
    st.header("Comptes suspects")

    # Analyse des handles suspects
    st.subheader("Handles suspects")
    screen_names = [item['author']['screen_name'] for item in data]
    suspicious_handles = [name for name in screen_names if re.fullmatch(r'[a-zA-Z]+\d+', name)]
    handle_counts = pd.Series(suspicious_handles).value_counts().reset_index()
    handle_counts.columns = ['screen_name', 'count']

    suspicious_data_with_metadata = []
    for item in data:
        screen_name = item['author']['screen_name']
        if screen_name in suspicious_handles:
            suspicious_data_with_metadata.append({
                'screen_name': screen_name,
                'date': item['author'].get('date'),
                'description': item['author'].get('description'),
                'geolocation': item['author'].get('geolocation')
            })

    suspicious_df = pd.DataFrame(suspicious_data_with_metadata)
    final_table = pd.merge(suspicious_df, handle_counts, on='screen_name')
    final_table = final_table.drop_duplicates()
    final_table_sorted = final_table.sort_values(by='count', ascending=False)

    st.write("Handles suspects avec métadonnées (triés par nombre) :")
    st.dataframe(final_table_sorted) # Affichage du DataFrame dans Streamlit

    # Possibilité de télécharger la table
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(final_table_sorted)
    st.download_button(
        label="Télécharger la table en CSV",
        data=csv,
        file_name='suspicious_handles_with_metadata_no_duplicates.csv',
        mime='text/csv',
    )


    # Section "Account creation date"
    st.subheader("Date de création des comptes")

    author_dates = [item['author'].get('date') for item in data if item['author'].get('date')]
    df_dates = pd.DataFrame(author_dates, columns=['creation_date'])
    df_dates['creation_date'] = pd.to_datetime(df_dates['creation_date'])
    df_dates = df_dates.drop_duplicates(subset=['creation_date'])
    df_dates['year_month'] = df_dates['creation_date'].dt.to_period('M')
    creation_counts_monthly = df_dates['year_month'].value_counts().sort_index()
    creation_counts_monthly.index = creation_counts_monthly.index.astype(str)

    st.write("Frise chronologique de la création des comptes (par mois) - Doublons exacts supprimés :")
    # Utiliser Streamlit pour afficher le graphique
    fig, ax = plt.subplots(figsize=(18, 7))
    plt.style.use('dark_background')
    ax.plot(creation_counts_monthly.index, creation_counts_monthly.values, color='#00FFFF', linestyle='-', marker='o', markersize=5, linewidth=2)
    ax.set_title('Frise chronologique de la création des comptes (par mois) - Doublons exacts supprimés', color='white', fontsize=16)
    ax.set_xlabel('Mois', color='white', fontsize=12)
    ax.set_ylabel('Nombre de comptes créés (sans doublons exacts)', color='white', fontsize=12)
    ax.tick_params(axis='x', rotation=45, colors='white', labelsize=10)
    ax.tick_params(axis='y', colors='white', labelsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig) # Affichage du graphique dans Streamlit

    # Top 3 semaines de création
    df_dates['year_week'] = df_dates['creation_date'].dt.to_period('W')
    creation_counts_weekly = df_dates['year_week'].value_counts()
    top_3_weeks = creation_counts_weekly.head(3)

    st.write("\nLes 3 semaines durant lesquelles le plus de comptes a été créé (sans doublons exacts à la seconde près) :")
    st.write(top_3_weeks) # Affichage du Series dans Streamlit

else:
    st.write("Veuillez charger un fichier JSON pour commencer l'analyse.")

# Ajoutez les sections "Followings - Followers ratio" et "Profile picture" ici
# en utilisant les composants Streamlit appropriés (st.subheader, st.write, st.dataframe, st.pyplot, etc.)
