import streamlit as st
import requests
import logging
from datetime import datetime

st.set_page_config(layout="wide")

# Configurando o logger
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Função para buscar dados com cache
@st.cache_resource
def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"https://rickandmortyapi.com/api/{endpoint}", params=params)
        response.raise_for_status()  # Raises HTTPError for bad requests
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"Request error: {e}")
        return None

def format_date(date_str):
    try:
        # Tente primeiro o formato do episódio
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return date_obj.strftime("%d/%m/%Y")
    except ValueError:
        try:
            # Se falhar, tente o formato do personagem
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            return "Data inválida"

def main():
    st.title("Rick and Morty API Viewer")
    
    option = st.sidebar.radio("Selecione o tipo de informação:", ("Personagem", "Episódio"))
    
    if option == "Personagem":
        endpoint = "character"
    else:
        endpoint = "episode"

    # Paginação
    page_number = st.sidebar.number_input("Número da página", value=1, min_value=1)
    params = {"page": page_number}
    data = fetch_data(endpoint, params=params)

    if data is not None:
        if option == "Personagem":
            st.write(f"Total de personagens: {data['info']['count']}")
            st.write(f"Total de páginas: {data['info']['pages']}")
            st.write("## Personagens:")
            results = data['results']
        else:
            if data['info']['pages'] >= page_number:
                st.write(f"Total de episódios: {data['info']['count']}")
                st.write(f"Total de páginas: {data['info']['pages']}")
                st.write("## Episódios:")
                results = data['results']
            else:
                st.write("Não existem mais episódios disponíveis.")
                page_number = 1  # Voltar para a primeira página
                params = {"page": page_number}
                data = fetch_data(endpoint, params=params)
                results = data['results']
        
        num_columns = 3
        cols = st.columns(num_columns)
        for i, item in enumerate(results):
            col_index = i % num_columns
            with cols[col_index]:
                with st.expander(label=item['name'], expanded=False):
                    if option == "Personagem":
                        st.write(f"**Status:** {item['status']}")
                        st.write(f"**Espécie:** {item['species']}")
                        st.write(f"**Tipo:** {item.get('type', 'Desconhecido')}")
                        st.write(f"**Gênero:** {item['gender']}")
                        st.write(f"**Origem:** {item['origin']['name']}")
                        st.write(f"**Localização:** {item['location']['name']}")
                        st.write(f"**Criado:** {format_date(item['created'])}")
                    else:
                        st.write(f"**Data de Lançamento:** {format_date(item['air_date'])}")
                        st.write(f"**Episódio:** {item['episode']}")
                        st.write(f"**Número do Episódio:** {item['episode']}")
                if 'image' in item:
                    try:
                        st.image(item['image'], caption=item['name'], width=250, use_column_width='auto')
                    except Exception as e:
                        st.warning(f"Falha ao exibir imagem para {item['name']}. Por favor, tente novamente mais tarde.")
                st.write("---")

if __name__ == "__main__":
    main()
