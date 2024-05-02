import pandas as pd

df = pd.read_csv("base_pecas.csv")

df = df.fillna('')
df['codigo_pintura'] = ''
df['descricao_pintura'] = ''

df = df.sort_values(by=['Recurso','Célula'], ascending=False).reset_index(drop=True)

df[df['Recurso'] == 'CBHM8000 SS T M20'] # CBHM8000 SS T M20 ; CBH7-2E FO-1M SS RS/RD M21
df[df['Recurso'] == 'CBHM8000 SS RD P700(R) M17'] # CBHM8000 SS T M20 ; CBH7-2E FO-1M SS RS/RD M21

for i in range(1,len(df)):
    try:
        if df['Recurso'][i] == df['Recurso'][i-1] and df['Célula'][i] == 'CHASSI':
            if df['Etapa'][i] == '' and (df['Etapa2'][i] == '' or df['Etapa2'][i] == 'Pintura')  and df['Célula'][i-1] == df['Célula'][i]:
                df['codigo_pintura'][i-1] = df['Código'][i]
                df['descricao_pintura'][i-1] = df['Peca'][i]
            elif df['Etapa'][i - 1] == '' and (df['Etapa2'][i] == '' or df['Etapa2'][i] == 'Pintura') and df['Célula'][i] == df['Célula'][i - 1]:
                df['codigo_pintura'][i-1] = df['Código'][i]
                df['descricao_pintura'][i-1] = df['Peca'][i]
    except:
        continue

df[(df['Célula'] == 'CHASSI') & (df['Peca'] == 'CHASSI CBH7-2E RS/RD SS')]

df_ = df[df['codigo_pintura'] != '']

df1 = pd.read_csv('tb_base_carretas_explodidas_202404151521.csv',dtype={'codigo': str,'conjunto':str})

df_ = df_[['Código','codigo_pintura','descricao_pintura']].drop_duplicates()

teste_df = pd.merge(df1,df_,how='left',left_on='conjunto',right_on='Código')
teste_df.to_csv('df_final.csv')

teste_df[teste_df['codigo_pintura'] == '030588']

teste_df = teste_df.drop_duplicates()
teste_df[teste_df['conjunto'] == '030347'][['codigo_pintura','descricao_pintura']]


teste_df[(teste_df['carreta'] == 'CBH3,5 UG SS RS M21') & (teste_df['processo'] == 'CHASSI')]