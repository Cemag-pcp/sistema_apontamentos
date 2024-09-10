import psycopg2  # pip install psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_HOST_REPRESENTANTE = "database-2.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"

def atualizar_saldo(itens_json):
    
    codigo = itens_json['codigo']
    descricao = itens_json['descricao']
    almoxarifado = itens_json['almoxarifado']
    quantidade = float(itens_json['quantidade'])
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Verifica se o item já existe no saldo_recurso
    cur.execute("""
        SELECT saldo FROM pcp.saldo_recurso 
        WHERE codigo = %s AND almoxarifado = %s
    """, (codigo, almoxarifado))
    
    resultado = cur.fetchone()

    if resultado:
        # Item encontrado, atualiza o saldo
        saldo_atual = resultado[0]
        novo_saldo = saldo_atual + quantidade

        cur.execute("""
            UPDATE pcp.saldo_recurso 
            SET saldo = %s
            WHERE codigo = %s AND almoxarifado = %s
        """, (novo_saldo, codigo, almoxarifado))

    else:

        # Item não encontrado, insere um novo registro
        cur.execute("""
            INSERT INTO pcp.saldo_recurso (almoxarifado, codigo, descricao, saldo)
            VALUES (%s, %s, %s, %s)
        """, (almoxarifado, codigo, descricao, quantidade))


    # Commit para salvar as mudanças no banco
    conn.commit()

def consulta_consumo_carretas():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
        SELECT * FROM pcp.consumo_carretas 
    """,)

    df_consumido = cur.fetchall()
    df_consumido = pd.DataFrame(df_consumido, columns=['id','id_carreta','carreta','conjunto','processo','quantidade_consumida','almoxarifado'])

    return df_consumido

def consulta_saldo_estoque(almoxarifado='Almox Mont Carretas'):

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
        SELECT codigo, saldo FROM pcp.saldo_recurso WHERE almoxarifado = %s
    """,(almoxarifado,))

    df_estoque = cur.fetchall()
    df_estoque =pd.DataFrame(df_estoque, columns=['conjunto','saldo'])

    return df_estoque

def consulta_saldo_batch(conn, almoxarifado, conjuntos):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Consulta todos os saldos de uma vez
    cur.execute("""
        SELECT codigo, saldo FROM pcp.saldo_recurso 
        WHERE codigo = ANY(%s) AND almoxarifado = %s
    """, (conjuntos, almoxarifado))

    # cur.execute("""
    #     SELECT codigo, saldo FROM pcp.saldo_recurso 
        
    # """,)

    # df_estoque = cur.fetchall()
    # df_estoque =pd.DataFrame(df_estoque, columns=['conjunto','saldo'])

    saldos = {row['codigo']: row['saldo'] for row in cur.fetchall()}
    cur.close()
    return saldos

def verificar_consumo_previo_batch(conn, id_carreta, almoxarifado, conjuntos):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Verificar consumo de todos os itens de uma vez
    cur.execute("""
        SELECT conjunto, quantidade_consumida FROM pcp.consumo_carretas 
        WHERE id_carreta = %s AND conjunto = ANY(%s) AND almoxarifado = %s
    """, (id_carreta, conjuntos, almoxarifado))
    
    consumos = {row['conjunto']: row['quantidade_consumida'] for row in cur.fetchall()}
    cur.close()
    return consumos

def abater_saldo_batch(conn, atualizacoes):
    cur = conn.cursor()
    
    # Executa atualização em batch para saldos
    cur.executemany("""
        UPDATE pcp.saldo_recurso 
        SET saldo = saldo - %s 
        WHERE codigo = %s AND almoxarifado = %s
    """, atualizacoes)
    
    conn.commit()
    cur.close()

def registrar_consumo_batch(conn, atualizacoes):
    cur = conn.cursor()
    
    # Inserir ou atualizar registros de consumo em batch
    cur.executemany("""
        INSERT INTO pcp.consumo_carretas (id_carreta, carreta, conjunto, processo, quantidade_consumida, almoxarifado)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_carreta, conjunto, processo, almoxarifado) 
        DO UPDATE SET quantidade_consumida = pcp.consumo_carretas.quantidade_consumida + EXCLUDED.quantidade_consumida;
    """, atualizacoes)
    
    conn.commit()
    cur.close()

def consumir_db(id_carreta, carreta, almoxarifado='Almox Mont Carretas'):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    
    cur = conn.cursor()
    
    # Consulta todos os conjuntos necessários para a carreta de uma vez
    cur.execute("""
        SELECT distinct(conjunto), processo, qt_conjunto 
        FROM pcp.tb_base_carretas_explodidas 
        WHERE carreta = %s
    """, (carreta,))
    
    necessidade = cur.fetchall()
    cur.close()

    conjuntos = [item[0] for item in necessidade]

    # Verificar consumo e saldo de todos os itens
    saldos = consulta_saldo_batch(conn, almoxarifado, conjuntos)
    consumos = verificar_consumo_previo_batch(conn, id_carreta, almoxarifado, conjuntos)

    atualizacoes_saldo = []
    atualizacoes_consumo = []
    resultado_faltante = {}

    # Itera sobre os itens necessários e consome do estoque
    for item in necessidade:
        conjunto = item[0]
        processo = item[1]
        qt_conjunto = item[2]

        consumo_previo = consumos.get(conjunto, 0)
        qt_restante = qt_conjunto - consumo_previo

        if qt_restante <= 0:
            # Se já foi totalmente consumido, não fazer nada
            continue

        saldo_disponivel = saldos.get(conjunto, 0)

        if saldo_disponivel >= qt_restante:
            # Se houver saldo suficiente, consome a quantidade necessária
            atualizacoes_saldo.append((qt_restante, conjunto, almoxarifado))
            atualizacoes_consumo.append((id_carreta, carreta, conjunto, processo, qt_restante, almoxarifado))
        else:
            # Se o saldo for insuficiente, consome o que for possível
            if saldo_disponivel > 0:
                atualizacoes_saldo.append((saldo_disponivel, conjunto, almoxarifado))
                atualizacoes_consumo.append((id_carreta, carreta, conjunto, processo, saldo_disponivel, almoxarifado))

            faltante = qt_restante - saldo_disponivel
            if processo not in resultado_faltante:
                resultado_faltante[processo] = []
            resultado_faltante[processo].append(f"Falta {faltante} do conjunto {conjunto}")

    # Atualiza o saldo e o consumo em batch
    abater_saldo_batch(conn, atualizacoes_saldo)
    registrar_consumo_batch(conn, atualizacoes_consumo)

    conn.close()

    # Retorna apenas o que ainda falta por processo
    return resultado_faltante

# Exemplo de uso:
resultado = consumir_db(id_carreta='A-41498/0824', carreta='FTC6500 SS RS/RS BB P750(I) M22')
for processo, faltantes in resultado.items():
    print(f"Processo {processo}:")
    for item in faltantes:
        print(f"  {item}")

import pandas as pd

def buscar_necessidade(df_agrupado_carretas, setor):

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()

    # Transformar as carretas em uma lista para o WHERE IN
    carretas = tuple(df_agrupado_carretas['carreta'].drop_duplicates())

    # Certifique-se de que a lista tem ao menos 2 itens, caso contrário o SQL terá erro de sintaxe
    if len(carretas) == 1:
        carretas = (carretas[0], carretas[0])  # Duplicar o único item para evitar erro

    # Executar a consulta
    cur.execute("""
        SELECT DISTINCT carreta, conjunto, conjunto_desc, processo, qt_conjunto 
        FROM pcp.tb_base_carretas_explodidas 
        WHERE carreta IN %s and setor = %s
    """, (carretas,setor))

    necessidade = cur.fetchall()
    df_necessidade = pd.DataFrame(necessidade, columns=['carreta', 'conjunto', 'conjunto_desc' ,'processo', 'qt_conjunto'])
    df_necessidade = df_necessidade.merge(df_agrupado_carretas, how='left', on='carreta')
    df_necessidade['necessidade_total'] = df_necessidade['qt_conjunto'] * df_necessidade['quantidade']
    df_necessidade = df_necessidade[['carreta','conjunto','conjunto_desc','processo','necessidade_total']]

    return df_necessidade

df_consumido = consulta_consumo_carretas()

# Trazer através do botão de "simular"
df_carretas = pd.DataFrame({
    'id': [0, 1, 2, 3, 4, 5],
    'data': ['2024-09-05', '2024-09-05', '2024-09-05', '2024-09-06', '2024-09-06', '2024-09-06'],
    'carreta': ['F4 SS RS/RS A45 M23', 'F4 SS RS/RS A45 M23', 'CBHM5000 GR SS RD M17', 'F4 SS RS/RS A45 M23', 'F4 SS RS/RS A45 M23', 'CBHM5000 GR SS RD M17'],
    'quantidade': [1, 1, 1, 1, 1, 1],
    'id_carreta': ['A-41493/0824', 'A-41494/0824', 'T-25324/0724', 'teste', 'teste2', 'teste3'],
    'Intermed.': ['', '', '', '', '', ''],
    'Traseira': ['', '', '', '', '', ''],
    'Plataforma': ['', '', '', '', '', ''],
    'Chassi': ['', '', '', '', '', ''],
    'Macaco': ['', '', '', '', '', ''],
    'Fueiro': ['', '', '', '', '', ''],
    'Dianteira': ['', '', '', '', '', ''],
    'Lateral': ['', '', '', '', '', ''],
    'Eixo': ['', '', '', '', '', ''],
    'Içamento': ['', '', '', '', '', '']
})

df_agrupado_carretas = df_carretas.groupby('carreta').agg({'quantidade': 'sum'}).reset_index()

df_necessidade = buscar_necessidade(df_agrupado_carretas,'Montagem')

df_estoque = consulta_saldo_estoque()

# def simular_consumo_acumulado_progresso(df_carretas, df_necessidade, df_estoque, df_agrupado_carretas, df_consumido):
#     saldo_estoque_acumulado = df_estoque.set_index('conjunto')['saldo'].to_dict()
#     resultado_por_carreta = []

#     # Iterar por cada carreta no DataFrame
#     for index, row_carreta in df_carretas.iterrows():
        
#         faltas_por_processo = {}

#         # Quantidade de carretas iguais
#         ajuste_quantidade = df_agrupado_carretas[df_agrupado_carretas['carreta'] == row_carreta['carreta']]['quantidade'].iloc[0]

#         # Filtrar os conjuntos usados pela carreta atual
#         df_necessidade_carreta = df_necessidade[df_necessidade['carreta'] == row_carreta['carreta']]

#         # Verificar o que já foi consumido por essa carreta
#         df_consumido_carreta = df_consumido[df_consumido['id_carreta'] == row_carreta['id_carreta']]

#         # Processar cada conjunto da carreta
#         for index, row_necessidade in df_necessidade_carreta.iterrows():
#             conjunto = row_necessidade['conjunto']
#             processo = row_necessidade['processo']
#             necessidade = row_necessidade['necessidade_total']/ajuste_quantidade

#             # Verificar se já foi consumido por essa carreta
#             consumido = df_consumido_carreta[df_consumido_carreta['conjunto'] == conjunto]['quantidade_consumida'].sum()

#             # Subtrair o que já foi consumido da necessidade
#             if consumido >= necessidade:
#                 necessidade_restante = 0
#             else:
#                 necessidade_restante = necessidade - consumido

#             # Se a necessidade já foi atendida pelo consumo anterior, não calcular déficit
#             if necessidade_restante == 0:
#                 resultado = f"Já consumido - {conjunto}"
#             else:
#                 # Garantir que o conjunto está no estoque (saldo inicializado com zero, se não existir)
#                 if conjunto not in saldo_estoque_acumulado:
#                     saldo_estoque_acumulado[conjunto] = 0

#                 saldo_estoque = saldo_estoque_acumulado[conjunto]

#                 # Verificar o saldo disponível e calcular o déficit progressivo
#                 if saldo_estoque >= necessidade_restante:
#                     # Consumo completo, saldo suficiente
#                     saldo_estoque_acumulado[conjunto] -= necessidade_restante
#                     resultado = f"Necessidade em estoque - {necessidade_restante} - {conjunto}"
#                 else:
#                     # Consumo parcial ou déficit
#                     falta = necessidade_restante - saldo_estoque
#                     saldo_estoque_acumulado[conjunto] -= necessidade_restante  # Atualiza o saldo acumulado, permitindo saldo negativo
                    
#                     # Arredondar para baixo, não mostrar frações
#                     # falta_ajustada = falta
#                     resultado = f"Falta {falta} - {conjunto}"

#             # Registrar o resultado no processo correspondente
#             if processo not in faltas_por_processo:
#                 faltas_por_processo[processo] = []
#             faltas_por_processo[processo].append(resultado)

#         # Concatenar faltas por processo e registrar apenas processos consumidos
#         faltas_concatenadas = {proc: '\n'.join(faltas_por_processo.get(proc, [])) for proc in faltas_por_processo}
#         resultado_por_carreta.append(faltas_concatenadas)

#     return resultado_por_carreta, saldo_estoque_acumulado

# # Executar a simulação com o estoque consumido
# resultado_carreta_deficit_progresso, saldo_final_deficit_progresso = simular_consumo_acumulado_progresso(df_carretas, df_necessidade, df_estoque, df_agrupado_carretas, df_consumido)

# # Adicionar as faltas acumuladas ao DataFrame de carretas, apenas para os processos consumidos
# for processo in df_necessidade['processo'].unique():
#     df_carretas[processo] = [result.get(processo, '') for result in resultado_carreta_deficit_progresso]

# print(df_carretas)
    
import streamlit as st

############################################

def simular_consumo_unitario(df_carretas, df_necessidade, df_estoque, df_agrupado_carretas, df_consumido):
    resultado_por_carreta = []

    # Iterar por cada carreta no DataFrame
    for index, row_carreta in df_carretas.iterrows():
        
        faltas_por_processo = {}

        # Criar uma cópia do saldo do estoque para tratar cada carreta de forma independente
        saldo_estoque = df_estoque.set_index('conjunto')['saldo'].to_dict()

        # Quantidade de carretas iguais
        ajuste_quantidade = df_agrupado_carretas[df_agrupado_carretas['carreta'] == row_carreta['carreta']]['quantidade'].iloc[0]

        # Filtrar os conjuntos usados pela carreta atual
        df_necessidade_carreta = df_necessidade[df_necessidade['carreta'] == row_carreta['carreta']]

        # Verificar o que já foi consumido por essa carreta
        df_consumido_carreta = df_consumido[df_consumido['id_carreta'] == row_carreta['id_carreta']]

        # Processar cada conjunto da carreta no almox de montagem
        for index, row_necessidade in df_necessidade_carreta.iterrows():
            conjunto = row_necessidade['conjunto']
            descricao = row_necessidade['conjunto_desc']
            processo = row_necessidade['processo']
            necessidade = row_necessidade['necessidade_total'] / ajuste_quantidade

            # Verificar se já foi consumido por essa carreta
            consumido = df_consumido_carreta[df_consumido_carreta['conjunto'] == conjunto]['quantidade_consumida'].sum()

            # Subtrair o que já foi consumido da necessidade
            if consumido >= necessidade:
                necessidade_restante = 0
            else:
                necessidade_restante = necessidade - consumido

            # Se a necessidade já foi atendida pelo consumo anterior, não calcular déficit
            if necessidade_restante == 0:
                resultado = f"Já consumido - {conjunto} - {descricao}"
            else:
                # Garantir que o conjunto está no estoque
                saldo_atual = saldo_estoque.get(conjunto, 0)

                # Verificar o saldo disponível e calcular o déficit progressivo
                if saldo_atual >= necessidade_restante:
                    # Consumo completo, saldo suficiente
                    resultado = f"Em estoque - {necessidade_restante} - {conjunto} - {descricao}"
                else:
                    # Consumo parcial ou déficit
                    falta = necessidade_restante - saldo_atual
                    resultado = f"Falta {falta} - {conjunto} - {descricao}"

            # Registrar o resultado no processo correspondente
            if processo not in faltas_por_processo:
                faltas_por_processo[processo] = []
            faltas_por_processo[processo].append(resultado)

        # Processar cada conjunto da carreta no almox de pintura


        # Concatenar faltas por processo e registrar apenas processos consumidos
        faltas_concatenadas = {proc: '\n'.join(faltas_por_processo.get(proc, [])) for proc in faltas_por_processo}
        resultado_por_carreta.append(faltas_concatenadas)

    return resultado_por_carreta

# Executar a simulação sem acumular déficit de estoque
resultado_carreta_unitario = simular_consumo_unitario(df_carretas, df_necessidade, df_estoque, df_agrupado_carretas, df_consumido)

# Adicionar os resultados ao DataFrame de carretas, apenas para os processos consumidos
for processo in df_necessidade['processo'].unique():
    df_carretas[processo] = [result.get(processo, '') for result in resultado_carreta_unitario]

st.write("Sem criar deficit de estoque (Apenas para montagem)")
st.dataframe(df_carretas)

# resumo completo

# Mostrar as peças que faltam por carreta conjunto de forma agrupada

