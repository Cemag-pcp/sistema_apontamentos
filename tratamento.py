import pandas as pd

df = pd.read_csv("base_pecas.csv")

df = df.fillna('')
df['codigo_pintura'] = ''
df['descricao_pintura'] = ''

df = df.sort_values(by=['Recurso','Célula'], ascending=False).reset_index(drop=True)

df[df['Recurso'] == 'CBHM5000 CA SS RD MM M17'] # CBHM8000 SS T M20 ; CBH7-2E FO-1M SS RS/RD M21

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

df_ = df[df['codigo_pintura'] != '']

df1 = pd.read_csv('base_nova.csv',dtype={'codigo': str,'conjunto':str,'Recurso_x':str,'Recurso_y':str})

df_ = df_.rename(columns={'Código':'conjunto'})

df_ = df_[['conjunto','codigo_pintura']].drop_duplicates()

teste_df = pd.merge(df1,df_,how='left',on='conjunto')
teste_df.to_csv('df_final.csv',index=False)

teste_df[teste_df['codigo_pintura'] == '030588']
