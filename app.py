import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard 2025 na Música", layout="wide")

def carregar_dados():
    url = "https://raw.githubusercontent.com/nicolascaseiro/2025-na-Musica/refs/heads/main/2025%20na%20M%C3%BAsica.csv"
    df = pd.read_csv(url, encoding='utf-8')
    return df

df = carregar_dados()

generos_lista = df['Gêneros'].dropna().apply(lambda x: [g.strip() for g in x.split(',')])
artistas_lista = df['Artista'].dropna().apply(lambda x: [a.strip() for a in x.split(',')])

df_temp = df.copy()
df_temp = df_temp.loc[generos_lista.index]
df_temp = df_temp.assign(Gêneros_lista=generos_lista)
df_temp = df_temp.explode('Gêneros_lista')

artistas_lista_temp = artistas_lista.loc[df_temp.index]
df_temp = df_temp.assign(Artistas_lista=artistas_lista_temp)
df_temp = df_temp.explode('Artistas_lista')

meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

df_temp['Data do Álbum'] = pd.to_datetime(df_temp['Data do Álbum'], errors='coerce')
df_temp['Mês'] = df_temp['Data do Álbum'].dt.month.apply(lambda x: meses_pt[x-1] if pd.notna(x) else None)

st.sidebar.header("Filtros")

def ordenar_meses(meses_selecionados):
    return sorted(meses_selecionados, key=lambda m: meses_pt.index(m))

def ordenar_pt(series):
    s = pd.Series(series).dropna().unique()
    return pd.Series(s).sort_values(
        key=lambda x: x.str.normalize('NFKD')
                        .str.encode('ascii', errors='ignore')
                        .str.decode('utf-8')
                        .str.lower()
    ).tolist()

meses_disponiveis = ordenar_meses(df_temp['Mês'].dropna().unique())
generos_disponiveis = sorted(df_temp['Gêneros_lista'].dropna().unique())
artistas_disponiveis = ordenar_pt(df_temp['Artistas_lista'])

mes_selecionado = st.sidebar.multiselect('Filtrar por Mês:', meses_disponiveis)
genero_selecionado = st.sidebar.multiselect('Filtrar por Gênero:', generos_disponiveis)
artista_selecionado = st.sidebar.multiselect('Filtrar por Artista:', artistas_disponiveis)

df_filtrado = df_temp.copy()

if mes_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Mês'].isin(mes_selecionado)]

if genero_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Gêneros_lista'].isin(genero_selecionado)]

if artista_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Artistas_lista'].isin(artista_selecionado)]

indices_filtrados = df_filtrado.index.unique()
df_tabela = df.loc[indices_filtrados].copy()
df_tabela['Data do Álbum'] = pd.to_datetime(df_tabela['Data do Álbum'], errors='coerce')
df_tabela['Mês'] = df_tabela['Data do Álbum'].dt.month.apply(lambda x: meses_pt[x-1] if pd.notna(x) else None)
total_musicas_filtradas = df_tabela['Música'].nunique()

st.title("Dashboard 2025 na Música")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de músicas", total_musicas_filtradas)
col2.metric("Média Popularidade", f"{df_filtrado['Popularidade'].mean():.2f}")
col3.metric("Total de Artistas", df_filtrado['Artistas_lista'].nunique())
col4.metric("Total de Gêneros", df_filtrado['Gêneros_lista'].nunique())

st.markdown("---")

df_grafico = df_filtrado.groupby('Gêneros_lista')['Popularidade'].mean().reset_index()

fig = px.bar(df_grafico,
             x='Gêneros_lista',
             y='Popularidade',
             title='Popularidade Média por Gênero Musical (2025)',
             labels={'Gêneros_lista': 'Gênero', 'Popularidade': 'Popularidade Média'},
             color='Popularidade',
             color_continuous_scale='Viridis',
             text=df_grafico['Popularidade'].round(2)
            )

fig.update_traces(textposition='outside', marker_line_width=1.5, marker_line_color='black')
fig.update_layout(
    plot_bgcolor='white',
    title_font=dict(size=24, family='Verdana', color='darkblue'),
    xaxis_title_font=dict(size=18, family='Verdana'),
    yaxis_title_font=dict(size=18, family='Verdana'),
    xaxis_tickangle=-45,
    xaxis_tickfont=dict(size=12, family='Verdana'),
    yaxis=dict(range=[0, 100]),
    margin=dict(l=40, r=40, t=80, b=100)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

colunas_exibir = ['Música', 'Artista', 'Gêneros', 'Popularidade', 'Mês']
st.dataframe(df_tabela[colunas_exibir])
