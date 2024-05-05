import streamlit as st
import requests
import logging
from datetime import datetime
import time

# Configurações da página
st.set_page_config(
    page_title="Rick and Morty", 
    page_icon="🤪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "`Página inicial:`🌍 https://hagliberto.streamlit.app/"}  
)

# Configurando o logger
logging.basicConfig(filename='error.log', level=logging.ERROR)

# Função para buscar dados com cache
@st.cache_resource
def fetch_data(endpoint, page_number):
    try:
        response = requests.get(f"https://rickandmortyapi.com/api/{endpoint}?page={page_number}")
        response.raise_for_status()  # Raises HTTPError for bad requests
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            error_message = st.empty()
            error_message.error("Página não encontrada. Redirecionando para a página 1.")
            time.sleep(3)  # Espera 3 segundos
            error_message.empty()  # Limpa a mensagem de erro
            return fetch_data(endpoint, 1)  # Redireciona para a página 1 em caso de erro 404
        else:
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
    st.success("Rick and Morty")
    
    option = st.sidebar.radio("Selecione o tipo de informação:", ("Personagem", "Episódio"))
    
    if option == "Personagem":
        endpoint = "character"
        # Sempre voltar para a página 1 ao mudar para personagens
        page_number = 1
    else:
        endpoint = "episode"
        page_number = 1  # Sempre voltar para a página 1 ao mudar para episódios
        
    page_number = st.session_state.get(f"{endpoint}_page", page_number)  # Recupera o número da página da sessão ou inicializa com 1

    # Paginação
    data = fetch_data(endpoint, page_number)

    if data is not None:
        num_pages = data['info']['pages']  # Armazena o número total de páginas
        
        if option == "Personagem":
            if num_pages >= page_number:
                st.sidebar.info(f"Total de personagens: {data['info']['count']}")
                st.sidebar.info(f"Total de páginas: {num_pages}")
                results = data['results']
            else:
                page_number = 1  # Voltar para a primeira página
                data = fetch_data(endpoint, page_number)
                results = data['results']
        else:
            if num_pages >= page_number:
                st.sidebar.info(f"Total de episódios: {data['info']['count']}")
                st.sidebar.info(f"Total de páginas: {num_pages}")
                results = data['results']
            else:
                page_number = 1  # Voltar para a primeira página
                data = fetch_data(endpoint, page_number)
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
        
        # Recalcular número da página atual
        current_page = (num_pages - 1) * 20 + len(results) + 1
        
        # Selecionar método de mudança de página
        navigation_method = st.sidebar.selectbox("Escolha o método de navegação de página:", ("Botões", "Input number", "Slider"))
        
        # Adicionar navegação para os episódios
        if option == "Episódio":
            col1, col2 = st.sidebar.columns([1, 1])  # Divide a barra lateral em duas colunas
        
            if navigation_method == "Botões":
                if page_number > 1:
                    if col1.button("Página anterior", key="prev_page"):
                        page_number -= 1
            
                if num_pages >= page_number:
                    if col2.button("Próxima página", key="next_page"):
                        page_number += 1
            
                if st.sidebar.button("Voltar para a primeira página", key="first_page"):
                    page_number = 1
            elif navigation_method == "Input number":
                new_page_number = st.sidebar.number_input("Número da página:", min_value=1, max_value=num_pages, value=page_number)
                if new_page_number != page_number:
                    page_number = new_page_number
            else:  # Slider
                page_number = st.sidebar.slider("Selecione a página:", 1, num_pages, page_number)
        
        # Atualizar dados com a nova página
        st.session_state[f"{endpoint}_page"] = page_number
        
        # Adicionar navegação para os personagens
        if option == "Personagem":
            col1, col2 = st.sidebar.columns([1, 1])  # Divide a barra lateral em duas colunas
        
            if navigation_method == "Botões":
                if page_number > 1:
                    if col1.button("Página anterior", key="prev_page_personagem"):
                        page_number -= 1
            
                if num_pages >= page_number:
                    if col2.button("Próxima página", key="next_page_personagem"):
                        page_number += 1
            
                if st.sidebar.button("Voltar para a primeira página", key="first_page_personagem"):
                    page_number = 1
            elif navigation_method == "Input number":
                new_page_number = st.sidebar.number_input("Número da página:", min_value=1, max_value=num_pages, value=page_number)
                if new_page_number != page_number:
                    page_number = new_page_number
            else:  # Slider
                page_number = st.sidebar.slider("Selecione a página:", 1, num_pages, page_number)
        
        # Atualizar dados com a nova página
        st.session_state[f"{endpoint}_page"] = page_number
    
    # Informar em qual página se encontra
    st.sidebar.success(f"Você está na página {page_number}/{num_pages}")

if __name__ == "__main__":
    main()
