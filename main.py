import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime


def criar_dashboard():
    st.set_page_config(page_title='Abastecimento braveo', layout='wide')
    st.markdown(
        """
        <style>
        .main {
            max-width: 80vw;
            margin: auto    ;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('Consumo combustível')


class Relatorio:

    def __init__(self, path):
        self.path = path
        criar_dashboard()

    @staticmethod
    @st.cache_data
    def importar_relatorio(path):
        df = pd.read_excel(path, index_col=False)
        return df

    def tratar_dados(self):
        dataset = self.importar_relatorio(self.path).copy()

        dataset.drop(columns=['CODIGO TRANSACAO', 'FORMA DE PAGAMENTO', 'CODIGO CLIENTE', 'TIPO FROTA', 'NUMERO FROTA',
                              'ANO', 'CODIGO ESTABELECIMENTO', 'TIPO ESTABELECIMENTO', 'ENDERECO', 'BAIRRO', 'CIDADE',
                              'UF', 'INFORMACAO ADIDIONAL 1', 'INFORMACAO ADIDIONAL 2', 'INFORMACAO ADIDIONAL 3',
                              'INFORMACAO ADIDIONAL 4', 'INFORMACAO ADIDIONAL 5', 'FORMA TRANSACAO',
                              'CODIGO LIBERACAO RESTRICAO', 'SERIE POS', 'NUMERO CARTAO', 'FAMILIA VEICULO',
                              'GRUPO RESTRICAO', 'CODIGO EMISSORA', 'RESPONSAVEL', 'TIPO ENTRADA HODOMETRO'],
                     inplace=True)

        dataset = dataset.astype(dtype={'NOME REDUZIDO': 'string', 'PLACA': 'string', 'MODELO VEICULO': 'string',
                                        'NOME MOTORISTA': 'string', 'SERVICO': 'string', 'TIPO COMBUSTIVEL': 'string',
                                        'NOME ESTABELECIMENTO': 'string'})

        #   Column                           Non-Null Count  Dtype
        # ---  ------                           --------------  -----
        # 0   NOME REDUZIDO                    3770 non-null   object
        # 1   DATA TRANSACAO                   3770 non-null   datetime64[ns]
        # 2   PLACA                            3770 non-null   object
        # 3   MODELO VEICULO                   3770 non-null   object
        # 4   MATRICULA                        3770 non-null   int64
        # 5   NOME MOTORISTA                   3770 non-null   object
        # 6   SERVICO                          3770 non-null   object
        # 7   TIPO COMBUSTIVEL                 3770 non-null   object
        # 8   LITROS                           3770 non-null   float64
        # 9   VL/LITRO                         3770 non-null   float64
        # 10  HODOMETRO OU HORIMETRO           3770 non-null   int64
        # 11  KM RODADOS OU HORAS TRABALHADAS  3770 non-null   int64
        # 12  KM/LITRO OU LITROS/HORA          3766 non-null   float64
        # 13  VALOR EMISSAO                    3770 non-null   float64
        # 14  NOME ESTABELECIMENTO             3770 non-null   object

        dataset['MES_ANO'] = dataset['DATA TRANSACAO'].dt.strftime('%m/%Y')

        return dataset


class Dashboard:

    def __init__(self):
        self.df = Relatorio(path='Abastecimentos 2025.xlsx').tratar_dados()

    def criar_filtros(self):

        df = self.df

        opcoes = {
            'Mês': ['Todos'] + sorted(df['MES_ANO'].unique()),
            'Empresa': ['Todos'] + sorted(df['NOME REDUZIDO'].unique())
        }

        return opcoes

    def mostrar_filtros(self, opcoes_dict):
        st.sidebar.title("Filtros")
        selecoes = {}

        for nome, opcao in opcoes_dict.items():
            selecoes[nome] = st.sidebar.selectbox(nome, opcao, key=f"select_{nome}")

        return selecoes

    def aplicar_filtros(self):
        df_filtrado = self.df.copy()
        filtros = self.criar_filtros()
        selecoes = self.mostrar_filtros(filtros)

        for chave, valor in selecoes.items():

            if valor != 'Todos':
                if chave == 'Mês':
                    df_filtrado = df_filtrado[df_filtrado['MES_ANO'] == valor]
                else:
                    df_filtrado = df_filtrado[df_filtrado['NOME REDUZIDO'] == valor]

        return df_filtrado

    def mostrar_cards(self, df_filtrado):
        col1, col2, col3, col4 = st.columns(4)

        # Dados para o cálculo
        valor_gasto = df_filtrado['VALOR EMISSAO'].sum()
        valor_litros = df_filtrado['LITROS'].sum()
        custo_por_litro = valor_gasto / valor_litros
        custo_por_veiculo = valor_gasto / df_filtrado['PLACA'].nunique()

        # Dados formatados para o card
        valor_gasto = (f'R$ {valor_gasto:,.2f}'.replace(',', 'X').replace('.', ',').
                       replace('X', '.'))
        valor_litros = (f'{valor_litros:,.2f}'.replace(',', 'X').replace('.', ',').
                        replace('X', '.'))
        custo_por_litro = (f'R$ {custo_por_litro:,.2f}'.replace(',', 'X').replace('.', ',').
                        replace('X', '.'))
        custo_por_veiculo = (f'R$ {custo_por_veiculo:,.2f}'.replace(',', 'X').replace('.', ',').
                           replace('X', '.'))

        with col1:
            st.markdown(f"""
                <div style="background-color:#e9f7fd; height: 150px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h5>Consumo total em R$</h5>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{valor_gasto}</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="background-color:#e9f7fd; height: 150px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h5>Custo médio/veículo</h5>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{custo_por_veiculo}</p>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style="background-color:#e9f7fd; height: 150px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h5>Custo médio/litro</h5>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{custo_por_litro}</p>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div style="background-color:#e9f7fd; height: 150px; padding:20px; border-radius:10px;
                border: 1.5px solid #94a8b0; box-shadow:0 2px 4px #6a787e;">
                    <h5>Consumo em litros</h5>
                    <p style="font-size:28px; font-weight:bold; color:#e98d2c;">{valor_litros}</p>
                </div>
            """, unsafe_allow_html=True)

    def apresentar_grafico(self, df_filtrado):
        st.markdown('---')
        col1, col2 = st.columns(2, border=True)

        with st.container(border=True):
            with col1:
                st.subheader('Custo mensal')
                df_litro_mes = df_filtrado.groupby('MES_ANO')['VALOR EMISSAO'].sum().reset_index()
                df_litro_mes['VALOR_FMT'] = df_litro_mes['VALOR EMISSAO'].apply(
                    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
                fig = px.bar(df_litro_mes, x='MES_ANO', y='VALOR EMISSAO', text='VALOR_FMT')
                fig.update_traces(textposition='outside', textfont=dict(color='black'))
                fig.update_layout(
                    xaxis_title='Mês',
                    yaxis_title='Valor',
                    xaxis_title_font=dict(size=12),
                    xaxis_tickfont=dict(size=12),
                    xaxis=dict(
                        tickmode='array',
                        tickvals=df_litro_mes['MES_ANO'].tolist(),
                        ticktext=df_litro_mes['MES_ANO'].tolist()
                    ),
                    yaxis=dict(
                        visible=False,
                        tickvals=df_litro_mes['VALOR EMISSAO'],
                        ticktext=df_litro_mes['VALOR EMISSAO'].apply(
                            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        )
                    )
                )
                st.plotly_chart(fig)

            with col2:
                st.subheader('Consumo mensal em litros')
                df_litro_mes = df_filtrado.groupby('MES_ANO')['LITROS'].sum().reset_index()
                fig = px.bar(df_litro_mes, x='MES_ANO', y='LITROS', text='LITROS')
                fig.update_layout(xaxis_title='Mês', yaxis_title='Litros',
                                  xaxis=dict(tickmode='array', tickvals=df_litro_mes['MES_ANO'].tolist(),
                                             ticktext=df_litro_mes['MES_ANO'].tolist()), yaxis=dict(visible=False))
                fig.update_traces(textposition='outside', textfont=dict(color='black'))
                st.plotly_chart(fig)

        col3, col4 = st.columns(2, border=True)

        with st.container(border=True):
            with col3:
                st.subheader('Litros/tipo de combustível')
                df_litro_tipo = df_filtrado.groupby('TIPO COMBUSTIVEL')['LITROS'].sum().reset_index()
                fig = px.pie(df_litro_tipo, names='TIPO COMBUSTIVEL', values='LITROS')
                fig.update_layout(xaxis_title='Mês', yaxis_title='Litros')
                st.plotly_chart(fig)

            with col4:
                st.subheader('% custo por empresa')
                df_litro_tipo = df_filtrado.groupby('NOME REDUZIDO')['VALOR EMISSAO'].sum().reset_index()
                fig = px.pie(df_litro_tipo, names='NOME REDUZIDO', values='VALOR EMISSAO')
                fig.update_layout(xaxis_title='Mês', yaxis_title='Litros')
                st.plotly_chart(fig)

    def apresentar_tabela(self, df_filtrado):

        df_filtrado.rename(columns={
            'NOME REDUZIDO': 'Empresa',
            'DATA TRANSACAO': 'Data',
            'PLACA': 'Placa',
            'MODELO VEICULO': 'Modelo',
            'MATRICULA': 'Matrícula',
            'NOME MOTORISTA': 'Motorista',
            'SERVICO': 'Produto',
            'TIPO COMBUSTIVEL': 'Combustível',
            'LITROS': 'Litros',
            'VL/LITRO': 'Vl/Litro',
            'HODOMETRO OU HORIMETRO': 'Hodômetro',
            'KM RODADOS OU HORAS TRABALHADAS': 'Km rodado',
            'KM/LITRO OU LITROS/HORA': 'KM/Litro',
            'VALOR EMISSAO': 'Valor',
            'NOME ESTABELECIMENTO': 'Posto'
        }, inplace=True)

        df_filtrado = df_filtrado[['Data', 'Placa', 'Modelo', 'Combustível', 'Valor', 'Vl/Litro', 'Litros', 'Empresa',
                                   'Matrícula', 'Motorista', 'Hodômetro', 'Km rodado', 'KM/Litro', 'Posto']]

        df_filtrado['Data'] = df_filtrado['Data'].dt.strftime('%d/%m/%Y %H:%M:%S')
        #df_filtrado = df_filtrado.drop(columns='MES_ANO')

        lista_reais = ['Vl/Litro', 'Valor']
        for col in lista_reais:
            df_filtrado[col] = df_filtrado[col].apply(lambda x: f'R$ {x:,.2f}'.replace(',', 'X')
                                                    .replace('.', ',').replace('X', '.'))

        st.dataframe(df_filtrado, hide_index=True)

    def ativar_funcoes(self):
        df_filtrado = self.aplicar_filtros()
        self.mostrar_cards(df_filtrado)
        self.apresentar_grafico(df_filtrado)
        self.apresentar_tabela(df_filtrado)


dash = Dashboard()
dash.ativar_funcoes()
