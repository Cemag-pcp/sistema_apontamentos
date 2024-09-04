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

def consulta_saldo(conjunto='411528', almoxarifado='Almox Mont Carretas'):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT saldo FROM pcp.saldo_recurso 
        WHERE codigo = %s AND almoxarifado = %s
    """, (conjunto, almoxarifado))

    saldo = cur.fetchone()
    cur.close()
    conn.close()

    return saldo['saldo'] if saldo else 0

def abater_saldo(conjunto='411528', almoxarifado='Almox Mont Carretas', quantidade=1):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        UPDATE pcp.saldo_recurso 
        SET saldo = saldo - %s 
        WHERE codigo = %s AND almoxarifado = %s
    """, (quantidade, conjunto, almoxarifado))

    conn.commit()
    cur.close()
    conn.close()

    return 'Saldo abatido'

def registrar_consumo(carreta, conjunto, processo, quantidade_consumida, almoxarifado='Almox Mont Carretas'):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Inserir ou atualizar o registro de consumo
    cur.execute("""
        INSERT INTO pcp.consumo_carretas (carreta, conjunto, processo, quantidade_consumida, almoxarifado)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (carreta, conjunto, processo, almoxarifado) 
        DO UPDATE SET quantidade_consumida = pcp.consumo_carretas.quantidade_consumida + EXCLUDED.quantidade_consumida;
    """, (carreta, conjunto, processo, quantidade_consumida, almoxarifado))

    conn.commit()
    cur.close()
    conn.close()

def verificar_consumo_previo(carreta, conjunto, processo, almoxarifado):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Verificar se o conjunto já teve parte consumida
    cur.execute("""
        SELECT quantidade_consumida FROM pcp.consumo_carretas 
        WHERE carreta = %s AND conjunto = %s AND processo = %s AND almoxarifado = %s
    """, (carreta, conjunto, processo, almoxarifado))

    consumo_previo = cur.fetchone()
    cur.close()
    conn.close()

    return consumo_previo['quantidade_consumida'] if consumo_previo else 0

def consumir(carreta='FTC6500 SS RS/RS BB P750(I) M22'):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Consulta os conjuntos e processos necessários para a carreta
    cur.execute("""
        SELECT distinct(conjunto), processo, qt_conjunto 
        FROM pcp.tb_base_carretas_explodidas 
        WHERE carreta = %s
    """, (carreta,))
    
    necessidade = cur.fetchall()

    # Armazena o que ainda falta após o consumo
    resultado_faltante = {}

    almoxarifado = 'Almox Mont Carretas'

    # Itera sobre os itens necessários e consome do estoque
    for item in necessidade:
        conjunto = item[0]
        processo = item[1]
        qt_conjunto = item[2]

        # Verificar se já houve consumo prévio para esse conjunto e processo
        consumo_previo = verificar_consumo_previo(carreta, conjunto, processo, almoxarifado)
        qt_restante = qt_conjunto - consumo_previo

        if qt_restante <= 0:
            # Se já foi totalmente consumido, não fazer nada
            continue

        # Consulta o saldo disponível no almoxarifado
        saldo_disponivel = consulta_saldo(conjunto, almoxarifado)

        if saldo_disponivel >= qt_restante:
            # Se houver saldo suficiente, consome a quantidade necessária
            abater_saldo(conjunto, almoxarifado, qt_restante)
            registrar_consumo(carreta, conjunto, processo, qt_restante, almoxarifado)
        else:
            # Se o saldo for insuficiente, abate o que for possível e registra o que falta
            if saldo_disponivel > 0:
                abater_saldo(conjunto, almoxarifado, saldo_disponivel)
                registrar_consumo(carreta, conjunto, processo, saldo_disponivel, almoxarifado)

            faltante = qt_restante - saldo_disponivel
            if processo not in resultado_faltante:
                resultado_faltante[processo] = []
            resultado_faltante[processo].append(f"Falta {faltante} do conjunto {conjunto}")

    # Retorna apenas o que ainda falta por processo
    return resultado_faltante

resultado = consumir(carreta)
for processo, faltantes in resultado.items():
    print(f"Processo {processo}:")
    for item in faltantes:
        print(f"  {item}")

        