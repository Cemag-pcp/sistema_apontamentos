import pandas as pd

base5roda = pd.read_csv('base-5roda.csv')
base5roda = base5roda[base5roda['setor_novo'] == '5ª RODA'].reset_index(drop=True)

base_sequenciamento = pd.read_csv('Bases para sequenciamento.csv')
base_sequenciamento = base_sequenciamento[base_sequenciamento['setor_novo'] == '5ª RODA'].reset_index(drop=True)

base_incluir = base5roda.merge(base_sequenciamento[['Recurso','Peca','Qtde','Código']], how='left', left_on='REFERENTE AO', right_on='Código')
base_incluir.columns

base_incluir['codigo_pintura'] = ''
base_incluir['descricao_pintura'] = ''

base_incluir = base_incluir.rename(columns={'setor_novo':'processo',
                                            'REFERENTE AO':'conjunto',
                                            'Recurso_x':'codigo',
                                            'Descrição':'descricao',
                                            'Matéria Prima':'materia_prima',
                                            'Compr':'comprimento',
                                            'Largu':'largura',
                                            'Quant':'quantidade',
                                            'Etapa Seguinte':'etapa_seguinte',
                                            'Recurso_y':'carreta',
                                            'Qtde':'qt_conjunto',
                                            'Peca':'conjunto_desc'})

base_incluir = base_incluir[['processo', 'conjunto', 'codigo', 'descricao', 'materia_prima',
                    'comprimento', 'largura', 'quantidade', 'etapa_seguinte', 'carreta',
                    'qt_conjunto', 'codigo_pintura', 'descricao_pintura', 'conjunto_desc']]

base_incluir['codigo'] = base_incluir['codigo'].astype(str)

for i in range(len(base_incluir)):
    if len(base_incluir['codigo'][i]) == 5:
        base_incluir['codigo'][i] = '0' + base_incluir['codigo'][i]

base_incluir.to_csv('base_incluir.csv', index=False)


# ----------------------------------------------------------------------------------------------------------------



base_sistema = pd.read_csv('base_sistema.csv') # O correto deveria ser a consulta da tabela pcp.tb_base_carretas_explodidas
base_pecas_novas = pd.read_csv('base_pecas.csv') # conjunto de peças novas

df_tratado = base_sistema.merge(base_pecas_novas, how='right', left_on='conjunto', right_on='Código')
df_tratado['carreta'] = df_tratado['Recurso']
df_tratado = df_tratado.drop_duplicates()
df_tratado = df_tratado[['processo', 'conjunto', 'codigo', 'descricao', 'materia_prima',
                    'comprimento', 'largura', 'quantidade', 'etapa_seguinte', 'carreta',
                    'qt_conjunto', 'codigo_pintura', 'descricao_pintura', 'conjunto_desc']]

df_tratado['conjunto'] = df_tratado['conjunto'].astype(str)
df_tratado['conjunto'] = df_tratado['conjunto'].apply(lambda x: x.replace(".0",""))
df_tratado['conjunto'] = df_tratado['conjunto'].apply(lambda x: "0" + x.replace(".0","") if len(x) == 5 else x)

df_tratado['codigo'] = df_tratado['codigo'].astype(str)
df_tratado['codigo'] = df_tratado['codigo'].apply(lambda x: x.replace(".0",""))
df_tratado['codigo'] = df_tratado['codigo'].apply(lambda x: "0" + x.replace(".0","") if len(x) == 5 else x)

df_tratado.to_csv("novos_dados.csv", index=False)

# df = pd.read_csv("base_pecas.csv")

# df = df.fillna('')
# df['codigo_pintura'] = ''
# df['descricao_pintura'] = ''

# df = df.sort_values(by=['Recurso','Célula'], ascending=False).reset_index(drop=True)

# df[df['Recurso'] == 'CBHM5000 CA SS RD MM M17'] # CBHM8000 SS T M20 ; CBH7-2E FO-1M SS RS/RD M21

# for i in range(1,len(df)):
#     try:
#         if df['Recurso'][i] == df['Recurso'][i-1] and df['Célula'][i] == 'CHASSI':
#             if df['Etapa'][i] == '' and (df['Etapa2'][i] == '' or df['Etapa2'][i] == 'Pintura')  and df['Célula'][i-1] == df['Célula'][i]:
#                 df['codigo_pintura'][i-1] = df['Código'][i]
#                 df['descricao_pintura'][i-1] = df['Peca'][i]
#             elif df['Etapa'][i - 1] == '' and (df['Etapa2'][i] == '' or df['Etapa2'][i] == 'Pintura') and df['Célula'][i] == df['Célula'][i - 1]:
#                 df['codigo_pintura'][i-1] = df['Código'][i]
#                 df['descricao_pintura'][i-1] = df['Peca'][i]
#     except:
#         continue

# df_ = df[df['codigo_pintura'] != '']

# df1 = pd.read_csv('base_nova.csv',dtype={'codigo': str,'conjunto':str,'Recurso_x':str,'Recurso_y':str})

# df_ = df_.rename(columns={'Código':'conjunto'})

# df_ = df_[['conjunto','codigo_pintura']].drop_duplicates()

# teste_df = pd.merge(df1,df_,how='left',on='conjunto')
# teste_df.to_csv('df_final.csv',index=False)

# teste_df[teste_df['codigo_pintura'] == '030588']

