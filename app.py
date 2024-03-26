from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Blueprint, send_file
import pandas as pd
import time
import datetime
import psycopg2  # pip install psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
import cachetools
import uuid
import gspread


app = Flask(__name__)
app.secret_key = "apontamentopintura"

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"
filename = "service_account.json"

cache_historico_pintura = cachetools.LRUCache(maxsize=128)
cache_carretas = cachetools.LRUCache(maxsize=128)

def resetar_cache(cache):

    """
    Função para limpar caches (não precisar fazer
    requisição sempre que atualizar a página).
    """
    
    cache.clear()

def ajustar_para_sexta(data):
    while data.weekday() >= 5:  # 5 representa sábado e 6 representa domingo
        data -= timedelta(1)  # Subtrai um dia
    return data


def dados_finalizar_cambao():
    """
    Função para buscar os dados gerados pelo gerador de cambão
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """SELECT *
            FROM pcp.ordens_pintura
            WHERE COALESCE(status, '') = '';"""

    df = pd.read_sql_query(sql, conn)

    df['status'] = df['status'].fillna('')
    df['celula'] = df['celula'].fillna('')

    df['data_carga'] = pd.to_datetime(df['data_carga']).dt.strftime("%d/%m/%Y")

    return df


def dados_sequenciamento():
    """
    Função para buscar os dados do sequenciamento de pintura
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """select 	t3.id,
                        t3.data_carga,
                        t3.codigo,
                        t3.peca,
                        coalesce((qt_planejada - qt_apontada),qt_planejada) as restante,
                        t3.cor,
                        t3.celula
                from (
                select 	t1.id,
						t1.data_carga,
                        t1.codigo,
                        t1.peca,
                        t1.qt_planejada,
                        t1.cor,
                        t1.celula,
                        sum(qt_apontada) as qt_apontada
                from pcp.gerador_ordens_pintura as t1
                left join pcp.ordens_pintura as t2 on t1.id = t2.chave
                group by 	t1.id,
							t1.data_carga,
                            t1.codigo,
                            t1.peca,
                            t1.qt_planejada,
                            t1.cor,
                            t1.celula
                order by t1.data_carga desc limit 500) as t3"""

    df = pd.read_sql_query(sql, conn)

    return df


def dados_sequenciamento_montagem():
    """
    Função para buscar os dados do sequenciamento de montagem
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """SELECT
                gerador_ordens_montagem.*,
                COALESCE(ordens_montagem.qt_apontada, 0) as qt_apontada,
                ABS(gerador_ordens_montagem.qt_planejada - COALESCE(ordens_montagem.qt_apontada, 0)) as restante
            FROM
                pcp.gerador_ordens_montagem
            LEFT JOIN (
                SELECT
                    data_carga,
                    codigo,
                    SUM(qt_apontada) as qt_apontada
                FROM
                    pcp.ordens_montagem
                GROUP BY
                    data_carga, codigo
            ) ordens_montagem
            ON
                concat(gerador_ordens_montagem.data_carga, gerador_ordens_montagem.codigo) = concat(ordens_montagem.data_carga, ordens_montagem.codigo)
            order by id desc
            LIMIT 500;"""

    df = pd.read_sql_query(sql, conn)

    return df


def dados_planejamento_estamparia():
    """
    Função para buscar os dados de planejamento da estamparia
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """select * from pcp.planejamento_estamparia pe 
            left join pcp.tb_pecas_em_processo pp on pe.chave = pp.chave
            where pp.status isnull"""

    cur.execute(sql)
    data = cur.fetchall()

    return data


def dados_planejamento_corte():
    """
    Função para buscar os dados de planejamento da corte
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """select * from pcp.ordens_corte oc 
            left join pcp.ordens_corte_processo ocp on oc.op = ocp.op
            where ocp.status isnull limit 100"""

    cur.execute(sql)
    data = cur.fetchall()

    return data


# Função para criar a nova coluna 'codificacao'
def criar_codificacao(row):
    if row['celula'] == 'EIXO SIMPLES':
        return f"{'EIS'}{str(row['data_carga']).replace('/', '')}"
    elif row['celula'] == 'EIXO COMPLETO':
        return f"{'EIC'}{str(row['data_carga']).replace('/', '')}"
    else:
        return f"{row['celula'].replace(' ','')[:3]}{str(row['data_carga']).replace('/', '')}"


@cachetools.cached(cache_historico_pintura)
def dados_historico_pintura():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """select * from pcp.ordens_pintura where data_carga >= '2024-01-01'"""

    df = pd.read_sql_query(sql, conn)

    return df


@app.route('/', methods=['GET'])
def pagina_inicial():
    """
    Rota para página inicial
    """

    return render_template('pagina-branco.html')


@app.route('/gerar-cambao', methods=['GET', 'POST'])
def gerar_cambao():
    """
    Rota para página de gerar cambão
    """

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(
        table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)
    table['data_planejada'] = pd.to_datetime(
        table['data_carga']) - timedelta(1)

    # Aplica a função de ajuste para cada valor na coluna 'data_planejada'
    table['data_planejada'] = table['data_planejada'].apply(ajustar_para_sexta)
    table['data_planejada'] = table['data_planejada'].dt.strftime("%d/%m/%Y")

    table = table[['id', 'data_carga', 'data_planejada', 'codigo', 'peca',
                   'restante', 'cor', 'qt_produzida', 'cambao', 'tipo', 'codificacao']]
    sheet_data = table.values.tolist()

    return render_template('gerar-cambao.html', sheet_data=sheet_data)


@app.route('/gerar-cambao-pintura', methods=['POST'])
def gerar_planilha():
    """
    Rota para receber a resposta da geração de cambão
    """

    # dados = request.get_json()

    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    # conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
    #                 password=DB_PASS, host=DB_HOST)
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # # Lista de tuplas contendo os dados a serem inseridos
    # values = [(linha['codigo'], linha['descricao'], linha['qt_itens'], linha['cor'], linha['prod'], linha['cambao'], linha['tipo'], datetime.strptime(linha['data'],'%d/%m/%Y').strftime('%Y-%m-%d'), datetime.now().date(), linha['celula'], linha['chave']) for linha in dados_recebidos]

    # print(values)

    # # Sua string de consulta com marcadores de posição (%s) adequados para cada valor
    # query = """INSERT INTO pcp.ordens_pintura (codigo, peca, qt_planejada, cor, qt_apontada, cambao, tipo, data_carga, data_finalizada, celula, chave) VALUES %s"""

    # # Use execute_values para inserir várias linhas de uma vez
    # execute_values(cur, query, values)

    # # Comitar as alterações
    # conn.commit()

    # # Fechar a conexão
    # cur.close()
    # conn.close()

    # table = dados_sequenciamento()
    # table['qt_produzida'] = ''
    # table['cambao'] = ''
    # table['tipo'] = ''
    # table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    # table['codificacao'] = table.apply(criar_codificacao, axis=1)

    # table = table[['data_carga','codigo','peca','restante','cor','qt_produzida','cambao','tipo','codificacao']]
    # sheet_data = table.values.tolist()

    # return jsonify({"linhas": sheet_data})

    return ''


@app.route('/finalizar-cambao', methods=['GET', 'POST'])
def finalizar_cambao():
    """
    Rota para mostrar página de finalizar cambão
    """

    table = dados_finalizar_cambao()
    if len(table) > 0:
        table['codificacao'] = table.apply(criar_codificacao, axis=1)
    else:
        table['codificacao'] = ''

    sheet_data = table.values.tolist()

    return render_template('finalizar-cambao.html', sheet_data=sheet_data)


@app.route("/receber-dados-finalizar-cambao", methods=['POST'])
def receber_dados_finalizar_cambao():
    """
    Rota para receber informações da finalização do cambão
    """

    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)

    with conn.cursor() as cursor:
        for dado in dados_recebidos:
            # Construir e executar a consulta UPDATE

            query = ("UPDATE pcp.ordens_pintura SET status = 'OK' WHERE id = %s")
            cursor.execute(query, (str(dado['chave']),))

        # Commit para aplicar as alterações
        conn.commit()

    return redirect(url_for("finalizar_cambao"))


@app.route("/dashboard")
def dashboard():
    """
    Rota para mostrar página de dashboard
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = 'SELECT * FROM pcp.ordens_pintura WHERE status ISNULL'

    cur.execute(sql)
    data_pecas_processo = cur.fetchall()

    today = datetime.now().date().strftime("%Y-%m-%d")

    sql = 'SELECT * FROM pcp.planejamento_pintura where data_planejamento = %s'

    cur.execute(sql, (today,))
    data_pecas_planejada = cur.fetchall()

    today = datetime.now().date().strftime("%d/%m/%Y")

    return render_template("painel.html", data_pecas_processo=data_pecas_processo, data_pecas_planejada=data_pecas_planejada, today=today)


@app.route("/atualizar-dashboard")
def atualizar_dashboard():
    """
    Rota para retornar dados para atualização do dashboard
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = 'SELECT * FROM pcp.ordens_pintura WHERE status IS NULL'

    cur.execute(sql)
    data_pecas_processo = cur.fetchall()

    today = datetime.now().date().strftime("%Y-%m-%d")

    sql = 'SELECT * FROM pcp.planejamento_pintura where data_planejamento = %s'

    cur.execute(sql, (today,))
    data_pecas_planejada = cur.fetchall()

    today = datetime.now().date().strftime("%d/%m/%Y")

    return jsonify({
        'data_pecas_processo': data_pecas_processo,
        'data_pecas_planejada': data_pecas_planejada,
        'today': today
    })


@app.route('/gerar-cambao-peca-fora-do-planejamento', methods=['POST'])
def gerar_cambao_peca_fora_do_planejamento():
    """
    Rota para receber peças que estavam fora do sequenciamento
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    print(data)

    codigo = data['peca'].split(' - ')[0]
    sql_search = "select celula from pcp.gerador_ordens_pintura where codigo = %s"
    cur.execute(sql_search, (codigo,))
    registro = cur.fetchall()

    if len(registro) > 0:
        celula = registro[0][0]
    else:
        celula = ''

    today = datetime.now().date()

    data_carga_formatada = datetime.strptime(
        data['dataCarga'], '%Y-%m-%d').strftime('%d/%m/%Y')

    # Se caso o usuário informar apenas o primeiro nome do conjunto
    try:
        descricao = data['peca'].split(' - ')[1]
    except IndexError:
        descricao = ''

    sql_insert = "insert into pcp.ordens_pintura (codigo,peca,qt_planejada,cor,qt_apontada,cambao,tipo,data_carga,data_finalizada,celula) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(sql_insert, (codigo,
                             descricao,
                             data['quantidade'],
                             data['cor'],
                             data['quantidade'],
                             data['cambao'],
                             data['tipo'],
                             data_carga_formatada,
                             today,
                             celula)
                )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('gerar_cambao'))


@app.route("/sugestao-pecas")
def mostrar_sugestao_peca():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select distinct(concat(codigo,' - ', peca)) from pcp.ordens_pintura"

    cur.execute(sql)
    data = cur.fetchall()

    return jsonify(data)


@app.route('/apontar-montagem', methods=['GET', 'POST'])
def apontar_montagem():
    """
    Rota para página de apontamento de montagem
    """

    table = dados_sequenciamento_montagem()
    table['qt_produzida'] = ''
    table['data_carga'] = pd.to_datetime(
        table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)
    # Supondo que 'table' seja um DataFrame do pandas e 'data_carga' seja uma coluna contendo as datas
    table['data_planejada'] = pd.to_datetime(
        table['data_carga']) - timedelta(3)

    # Aplica a função de ajuste para cada valor na coluna 'data_planejada'
    table['data_planejada'] = table['data_planejada'].apply(ajustar_para_sexta)
    table['data_planejada'] = table['data_planejada'].dt.strftime("%d/%m/%Y")

    table = table[['data_carga', 'data_planejada', 'celula', 'codigo',
                   'peca', 'qt_planejada', 'qt_produzida', 'codificacao', 'id']]

    sheet_data = table.values.tolist()

    return render_template('apontamento-montagem.html', sheet_data=sheet_data)


@app.route('/planejamento-estamparia', methods=['GET', 'POST'])
def planejamento_estamparia():
    """
    Rota para enviar os itens do planejamento da estamparia
    """

    data = dados_planejamento_estamparia()

    return jsonify(data)


@app.route('/tela-apontamento-estamparia', methods=['GET', 'POST'])
def tela_estamparia():
    """
    Rota para tela de estamparia
    """

    return render_template('apontamento-estamparia.html')


@app.route('/salvar-apontamento-montagem', methods=['GET', 'POST'])
def salvar_apontamento_montagem():
    """
    Rota para receber a resposta do apontamento de montagem
    """

    # dados = request.get_json()

    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lista de tuplas contendo os dados a serem inseridos
    values = [(linha['celula'], linha['codigo'], linha['descricao'], linha['prod'],
               datetime.strptime(
                   linha['data'], '%d/%m/%Y').strftime('%Y-%m-%d'), datetime.now().date(),
               linha['operador'], linha['obs'], linha['codificacao'], 'Sequenciamento') for linha in dados_recebidos]

    print(values)

    for dado in values:
        # Construir e executar a consulta INSERT
        query = """INSERT INTO pcp.ordens_montagem (celula, codigo, peca, qt_apontada, data_carga, data_finalizacao, operador, observacao, codificacao, origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.execute(query, dado)

    conn.commit()

    # Sua string de consulta com marcadores de posição (%s) adequados para cada valor
    # query = """INSERT INTO pcp.ordens_montagem (celula, codigo, peca, qt_apontada, data_carga, data_finalizacao, operador, observacao, codificacao, origem) VALUES %s"""

    # # Use execute_values para inserir várias linhas de uma vez
    # execute_values(cur, query, values)

    # # Comitar as alterações
    # conn.commit()

    # # Fechar a conexão
    # cur.close()
    # conn.close()

    return redirect(url_for("gerar_cambao"))


@app.route('/gerar-apontamento-peca-fora-do-planejamento-montagem', methods=['POST'])
def gerar_apontamento_peca_fora_do_planejamento_montagem():
    """
    Rota para receber peças que estavam fora do sequenciamento de montagem
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    print(data)

    # pesquisar peça para buscar célula
    codigo = data['peca'].split(' - ')[0]
    sql_pesquisa = "select celula from pcp.gerador_ordens_montagem where codigo = %s"

    cur.execute(sql_pesquisa, (codigo,))
    celula = cur.fetchall()
    if len(celula) > 0:
        celula = celula[0][0]
    else:
        celula = ""

    today = datetime.now().date()
    print(data['dataCarga'])
    # data_carga_formatada = datetime.strptime(data['dataCarga'], '%Y-%d-%m').strftime('%d/%m/%Y')
    data_carga_formatada = datetime.strptime(data['dataCarga'], '%Y-%m-%d')

    sql_insert = "insert into pcp.ordens_montagem (celula,codigo,peca,qt_apontada,data_carga,data_finalizacao,operador,observacao,origem) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(sql_insert, (celula,
                             data['peca'].split(' - ')[0],
                             data['peca'].split(' - ')[1],
                             data['quantidade'],
                             data_carga_formatada,
                             today,
                             data['operador'],
                             data['obs'],
                             'Fora do sequenciamento'
                             )
                )

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('gerar_cambao'))


@app.route("/sugestao-pecas-montagem")
def mostrar_sugestao_peca_montagem():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select distinct(concat(codigo,' - ', peca)) from pcp.gerador_ordens_montagem"

    cur.execute(sql)
    data = cur.fetchall()

    return jsonify(data)


@app.route("/sugestao-pecas-estamparia")
def mostrar_sugestao_peca_estamparia():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select distinct(concat(codigo,' - ', peca)) from pcp.gerador_ordens_montagem"

    cur.execute(sql)
    data = cur.fetchall()

    return jsonify(data)


@app.route("/sugestao-operadores-montagem")
def mostrar_sugestao_operadores_montagem():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select distinct(concat(matricula,' - ', nome)) from pcp.operadores_montagem"

    cur.execute(sql)
    data = cur.fetchall()

    return jsonify(data)


@app.route('/historico-pintura', methods=['GET'])
def historico_pintura():
    """
    Rota para página de hisórico da pintura
    """

    table = dados_historico_pintura()
    table['data_carga'] = pd.to_datetime(
        table['data_carga']).dt.strftime("%d/%m/%Y")
    table['data_finalizada'] = pd.to_datetime(
        table['data_finalizada']).dt.strftime("%d/%m/%Y")

    sheet_data = table.values.tolist()

    return render_template('historico-pintura.html', sheet_data=sheet_data)


@app.route('/limpar-cache-historico', methods=['POST'])
def limpar_cache_historico():

    cache_historico_pintura.clear()

    return render_template('historico-pintura.html')


@app.route('/planejar-pintura', methods=['GET', 'POST'])
def planejar_pintura():
    """
    Rota para página de gerar cambão
    """

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(
        table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga', 'codigo', 'peca', 'restante',
                   'cor', 'qt_produzida', 'cambao', 'tipo', 'codificacao']]
    sheet_data = table.values.tolist()

    return render_template('planejar-pintura.html', sheet_data=sheet_data)


@app.route("/receber-dados-planejamento", methods=['POST'])
def receber_dados_planejamento():
    """
    Rota para receber informações do planejamento
    """

    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)

    with conn.cursor() as cursor:
        for dado in dados_recebidos:
            data = datetime.strptime(
                dado['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
            # Construir e executar a consulta UPDATE
            if dado['prod'] == '':
                dado['prod'] = dado['qt_itens']

            query = ("insert into pcp.planejamento_pintura (data_carga,data_planejamento,codigo,peca,cor,qt_planejada,qt_produzida,tipo,codificacao) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
            cursor.execute(query, (data,
                                   dado['dataPlanejamento'],
                                   dado['codigo'],
                                   dado['descricao'],
                                   dado['cor'],
                                   dado['qt_itens'],
                                   dado['prod'] if 'prod' in dado else None,
                                   dado['tipo'],
                                   dado['codificacao']))

        # Commit para aplicar as alterações
        conn.commit()

    return redirect(url_for("planejar_pintura"))


@app.route('/planejar-montagem', methods=['GET', 'POST'])
def planejar_montagem():
    """
    Rota para página planejamento da montagem
    """

    table = dados_sequenciamento_montagem()
    table['qt_produzida'] = ''
    table['data_carga'] = pd.to_datetime(
        table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga', 'codigo', 'peca',
                   'qt_planejada', 'qt_produzida', 'codificacao', 'celula']]
    sheet_data = table.values.tolist()

    return render_template('planejar-montagem.html', sheet_data=sheet_data)


@app.route("/receber-dados-planejamento-montagem", methods=['POST'])
def receber_dados_planejamento_montagem():
    """
    Rota para receber informações do planejamento de montagem
    """

    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)

    with conn.cursor() as cursor:
        for dado in dados_recebidos:
            data = datetime.strptime(
                dado['data'], '%d/%m/%Y').strftime('%Y-%m-%d')
            # Construir e executar a consulta UPDATE
            if dado['prod'] == '':
                dado['prod'] = dado['qt_itens']

            query = ("insert into pcp.planejamento_montagem (data_carga,data_planejamento,codigo,peca,qt_planejada,qt_produzida,codificacao,celula) values (%s,%s,%s,%s,%s,%s,%s,%s)")
            cursor.execute(query, (data,
                                   dado['dataPlanejamento'],
                                   dado['codigo'],
                                   dado['descricao'],
                                   dado['qt_itens'],
                                   dado['prod'] if 'prod' in dado else None,
                                   dado['codificacao'],
                                   dado['celula']))

        # Commit para aplicar as alterações
        conn.commit()

    return redirect(url_for("planejar_montagem"))


@app.route("/api/publica/apontamento/pintura")
def api_apontamento_pintura():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select * from pcp.ordens_pintura where data_carga > '2024-01-01' order by id asc"

    cur.execute(sql)
    data = cur.fetchall()

    for linha in data:
        linha[8] = linha[8].strftime("%d/%m/%Y")
        linha[9] = linha[9].strftime("%d/%m/%Y")

    return jsonify(data)


@app.route("/api/publica/apontamento/montagem")
def api_apontamento_montagem():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = "select * from pcp.ordens_montagem where data_carga > '2024-01-01' order by id asc"

    cur.execute(sql)
    data = cur.fetchall()

    for linha in data:
        linha[5] = linha[5].strftime("%d/%m/%Y")
        linha[6] = linha[6].strftime("%d/%m/%Y")

    return jsonify(data)


@app.route("/painel-montagem")
def painel_montagem():
    """
    Rota para mostrar página de painel de montagem
    """

    today = datetime.now().date().strftime("%d/%m/%Y")

    return render_template("painel-montagem.html", today=today)


@app.route("/atualizar-painel-montagem")
def atualizar_painel_montagem():
    """
    Rota para retornar dados para atualização do painel montagem
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    today = datetime.now().date().strftime("%Y-%m-%d")

    sql = 'SELECT * FROM pcp.planejamento_montagem where data_planejamento = %s'

    cur.execute(sql, (today,))
    data_pecas_planejada = cur.fetchall()

    today = datetime.now().date().strftime("%d/%m/%Y")

    return jsonify({
        'data_pecas_planejada': data_pecas_planejada,
        'today': today
    })


@app.route("/api/planejamento/montagem")
def api_planejamento_montagem_csv():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lógica para obter dados da tabela
    query = "SELECT * FROM pcp.gerador_ordens_montagem WHERE data_carga > '2024-02-29' ORDER BY id asc;"
    df = pd.read_sql_query(query, conn)

    df['celula'] = df['celula'].astype(str)
    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula'] else (
        'EIC' if 'EIXO COMPLETO' in row['celula'] else row['celula'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%d%m%Y").dt.strftime("%Y-%m-%d")

    # Fecha a conexão com o PostgreSQL
    conn.close()

    # Salva os dados em um arquivo CSV temporário
    temp_file_path = 'planejamento_apontamento.csv'
    df.to_csv(temp_file_path, index=False)

    # Retorna o arquivo CSV como resposta
    return send_file(temp_file_path, mimetype='text/csv', as_attachment=True, download_name='planejamento_montagem.csv')


@app.route("/api/apontamento/montagem")
def api_apontamento_montagem_csv():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lógica para obter dados da tabela
    query = "SELECT * FROM pcp.ordens_montagem WHERE data_carga > '2024-02-29' ORDER BY id asc;"
    df = pd.read_sql_query(query, conn)

    # Fecha a conexão com o PostgreSQL
    conn.close()

    # Salva os dados em um arquivo CSV temporário
    temp_file_path = 'apontamento_montagem.csv'
    df.to_csv(temp_file_path, index=False)

    # Retorna o arquivo CSV como resposta
    return send_file(temp_file_path, mimetype='text/csv', as_attachment=True, download_name='apontamento_montagem.csv')


@app.route("/api/planejamento/pintura")
def api_planejamento_pintura_csv():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lógica para obter dados da tabela
    query = """ SELECT * FROM pcp.gerador_ordens_pintura
                WHERE data_carga > '2024-02-29' ORDER BY id;
            """

    df = pd.read_sql_query(query, conn)

    df['celula'] = df['celula'].astype(str)
    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula'] else (
        'EIC' if 'EIXO COMPLETO' in row['celula'] else row['celula'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%d%m%Y").dt.strftime("%Y-%m-%d")

    # Fecha a conexão com o PostgreSQL
    conn.close()

    # Salva os dados em um arquivo CSV temporário
    temp_file_path = 'planejamento_apontamento.csv'
    df.to_csv(temp_file_path, index=False)

    # Retorna o arquivo CSV como resposta
    return send_file(temp_file_path, mimetype='text/csv', as_attachment=True, download_name='planejamento_pintura.csv')


@app.route("/api/apontamento/pintura")
def api_apontamento_pintura_csv():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lógica para obter dados da tabela
    query = """SELECT DISTINCT t1.*, t2.celula as celula_nova
                FROM pcp.ordens_pintura AS t1
                LEFT JOIN (
                    SELECT DISTINCT codigo, celula
                    FROM pcp.gerador_ordens_pintura
                    WHERE celula NOT IN ('QUALIDADE','CILINDRO')
                ) AS t2
                ON t1.codigo = t2.codigo
                WHERE t1.data_carga > '2024-02-29' ORDER BY id;
            """

    df = pd.read_sql_query(query, conn)

    df['celula_nova'] = df['celula_nova'].astype(str)
    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula_nova'] else (
        'EIC' if 'EIXO COMPLETO' in row['celula_nova'] else row['celula_nova'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(
        df['data_carga'], format="%d%m%Y").dt.strftime("%Y-%m-%d")

    # Fecha a conexão com o PostgreSQL
    conn.close()

    # Salva os dados em um arquivo CSV temporário
    temp_file_path = 'apontamento_pintura.csv'
    df.to_csv(temp_file_path, index=False)

    # Retorna o arquivo CSV como resposta
    return send_file(temp_file_path, mimetype='text/csv', as_attachment=True, download_name='apontamento_pintura.csv')


@app.route("/api/pecas-em-processo/montagem", methods=['POST'])
def api_pecas_em_processo_montagem():
    """
    rota para enviar peças para status "em processo"
    """

    data = request.json

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    chave = data['chave']
    codigo = data['peca']
    descricao = data['descricao']

    try:
        data_carga = pd.to_datetime(data['dataCarga'], format="%d/%m/%Y")
    except ValueError:
        data_carga = data['dataCarga']

    celula = data['celula']
    qt_planejada = data['qtPlanejada']
    codificacao = data['codificacao']
    setor = 'Montagem'
    status = 'Em processo'
    origem = data['origem']

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,codificacao,data_carga,setor,qt_planejada,celula,status,chave,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, codificacao, data_carga,
                setor, qt_planejada, celula, status, chave, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/consulta-pecas-em-processo/montagem", methods=['GET'])
def api_consulta_pecas_em_processo_montagem():
    """
    Api para consultar peças com status "em processo"
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select * from pcp.tb_pecas_em_processo where status = 'Em processo' and data_fim isnull and setor = 'Montagem' order by id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/api/consulta-pecas-interrompidas/montagem", methods=['GET'])
def api_consulta_pecas_interrompidas_montagem():
    """
    Api para consultar peças com status "interrompida"
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select * from pcp.tb_pecas_em_processo where status = 'Interrompida' and setor = 'Montagem' and data_fim isnull order by id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/consulta-id-em-processo", methods=['GET'])
def consulta_id_em_processo_montagem():
    """
    Api para consultar peça específica com status "em processo"
    """

    data = request.args

    id = data.get('id_peca')

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            SELECT * FROM pcp.tb_pecas_em_processo WHERE id = %s
            """

    cur.execute(query, (id,))
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/finalizar-peca-em-processo", methods=['POST'])
def finalizar_peca_em_processo_montagem():
    """
    Finalizar ordem de serviço
    """
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.get_json()

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where id = %s"""
    cur.execute(query_update, (agora, data['idPecaEmProcesso']))
    conn.commit()

    id = data['idPecaEmProcesso']
    codigo = data['codigo'].split(' - ')[0]
    descricao = data['codigo'].split(' - ')[1]
    qt_planejada = data['qtdePlanejada']
    codificacao = data['codificacao']
    celula = data['celula']
    textAreaObservacao = data['textAreaObservacao']
    dataHoraInicio = pd.to_datetime(
        data['dataHoraInicio']).strftime("%Y-%m-%d %H:%M:%S")
    operadorInputModal_1 = data['operadorInputModal_1']
    inputQuantidadeRealizada = data['inputQuantidadeRealizada']
    dataCarga = data['dataCarga']
    data_finalizacao = datetime.now().date().strftime("%Y-%m-%d")
    origem = data['origem']

    print(textAreaObservacao)

    query = """ 
            INSERT INTO pcp.ordens_montagem (celula,codigo,peca,qt_apontada,data_carga,data_finalizacao,operador,observacao,codificacao,origem,data_hora_inicio)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (celula, codigo, descricao, inputQuantidadeRealizada, dataCarga,
                data_finalizacao, operadorInputModal_1, textAreaObservacao, codificacao, origem, dataHoraInicio))

    conn.commit()

    return 'sucess'


@app.route("/api/pecas-interrompida/montagem", methods=['POST'])
def api_pecas_interrompida_montagem():
    """
    rota para enviar peças para status "interrompida"
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.tb_pecas_em_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    print(data)
    data = data[0]
    print(data)

    codigo = data[1]
    descricao = data[2]
    codificacao = data[4]
    data_carga = data[5]
    setor = 'Montagem'
    qt_planejada = data[7]
    celula = data[8]
    status = 'Interrompida'
    chave = data[11]
    motivo = data_request['motivo']
    origem = data[13]

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,codificacao,data_carga,setor,qt_planejada,celula,status,chave,motivo_interrompido,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, codificacao, data_carga,
                setor, qt_planejada, celula, status, chave, motivo, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/pecas-retornou/montagem", methods=['POST'])
def api_pecas_retornou_montagem():
    """
    rota para enviar peças para status "Em produção" depois de interrompidas
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.tb_pecas_em_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    data = data[0]

    codigo = data[1]
    descricao = data[2]
    codificacao = data[4]
    data_carga = data[5]
    setor = 'Montagem'
    qt_planejada = data[7]
    celula = data[8]
    status = 'Em processo'
    chave = data[11]
    origem = data[13]

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,codificacao,data_carga,setor,qt_planejada,celula,status,chave,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, codificacao, data_carga,
                setor, qt_planejada, celula, status, chave, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/pecas-em-processo/estamparia", methods=['POST'])
def api_pecas_em_processo_estamparia():
    """
    rota para enviar peças para status "em processo" a partir da criação de peça fora do planejamento
    """

    data = request.json

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    print(data)

    codigo = data['peca']
    descricao = data['descricao']
    chave = str(uuid.uuid1())

    try:
        data_planejada = pd.to_datetime(
            data['dataPlanejamento'], format="%d/%m/%Y")
    except ValueError:
        data_planejada = data['dataPlanejamento']

    celula = data['selectedMaquina']
    qt_planejada = data['qtPlanejada']
    setor = 'Estamparia'
    status = 'Em processo'
    origem = data['origem']

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,data_carga,setor,qt_planejada,celula,status,chave,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, data_planejada, setor,
                qt_planejada, celula, status, chave, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/pecas-em-processo-planejamento/estamparia", methods=['POST'])
def api_pecas_em_processo_planejamento_estamparia():
    """
    rota para enviar peças para status "em processo" a partir da criação de peça do planejamento
    """

    data = request.json

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query_consulta = """select * from pcp.planejamento_estamparia where chave = %s"""

    cur.execute(query_consulta, (data['chave'],))
    data_query = cur.fetchone()

    chave = data['chave']
    codigo = data_query[2]
    descricao = data_query[3]
    data_planejada = data_query[1]
    maquina = data_query[5]
    qt_planejada = data_query[4]
    setor = 'Estamparia'
    status = 'Em processo'
    origem = data_query[6]

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,data_carga,setor,qt_planejada,celula,status,chave,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, data_planejada, setor,
                qt_planejada, maquina, status, chave, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/planejar-pecas/estamparia", methods=['POST'])
def planejar_pecas_estamparia():
    """
    rota para receber peças planejadas para estamparia
    """

    data = request.json

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    print(data)

    chave = str(uuid.uuid1())
    codigo = data['peca']
    descricao = data['descricao']

    try:
        data_planejada = pd.to_datetime(
            data['dataPlanejamento'], format="%d/%m/%Y")
    except ValueError:
        data_planejada = data['dataPlanejamento']

    celula = data['selectedMaquina']
    qt_planejada = data['qtPlanejada']
    origem = data['origem']

    query = """ 
            INSERT INTO pcp.planejamento_estamparia (data_planejada,codigo,descricao,qt_planejada,maquina,origem,chave) VALUES (%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (data_planejada, codigo, descricao,
                qt_planejada, celula, origem, chave))

    conn.commit()

    return 'sucess'


@app.route("/api/consulta-pecas-em-processo/estamparia", methods=['GET'])
def api_consulta_pecas_em_processo_estamparia():
    """
    Api para consultar peças com status "em processo"
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select * from pcp.tb_pecas_em_processo where status = 'Em processo' and data_fim isnull and setor = 'Estamparia' order by id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/consulta-id-em-processo/estamparia", methods=['GET'])
def consulta_id_em_processo_estamparia():
    """
    Api para consultar peça específica com status "em processo" em estamparia
    """

    data = request.args

    id = data.get('id_peca')

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            SELECT * FROM pcp.tb_pecas_em_processo WHERE id = %s
            """

    cur.execute(query, (id,))
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/finalizar-peca-em-processo/estamparia", methods=['POST'])
def finalizar_peca_em_processo_estamparia():
    """
    Finalizar ordem de serviço da estamparia
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.get_json()

    print(data)

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where chave = %s"""
    cur.execute(query_update, (agora, data['idPecaEmProcesso']))
    conn.commit()

    id = data['idPecaEmProcesso']
    codigo = data['codigo']
    descricao = data['descricao']
    qt_planejada = data['qtdePlanejada']
    chave = data['idPecaEmProcesso']
    celula = data['celula']
    textAreaObservacao = data['textAreaObservacao']
    dataHoraInicio = pd.to_datetime(
        data['dataHoraInicio']).strftime("%Y-%m-%d %H:%M:%S")
    operadorInputModal_1 = data['operadorInputModal_1']
    inputQuantidadeRealizada = data['inputQuantidadeRealizada']
    dataCarga = data['dataCarga']
    data_finalizacao = datetime.now().date().strftime("%Y-%m-%d")
    origem = data['origem']

    query = """ 
            INSERT INTO pcp.ordens_estamparia (celula,codigo,descricao,qt_apontada,data_planejamento,data_finalizacao,operador,observacao,chave,origem,data_hora_atual)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (celula, codigo, descricao, inputQuantidadeRealizada, dataCarga,
                data_finalizacao, operadorInputModal_1, textAreaObservacao, chave, origem, dataHoraInicio))

    conn.commit()

    return 'sucess'


@app.route("/api/pecas-interrompida/estamparia", methods=['POST'])
def api_pecas_interrompida_estamparia():
    """
    rota para enviar peças para status "interrompida" estamparia
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.tb_pecas_em_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    print(data)
    data = data[0]
    print(data)

    codigo = data[1]
    descricao = data[2]
    codificacao = data[4]
    data_carga = data[5]
    setor = 'Estamparia'
    qt_planejada = data[7]
    celula = data[8]
    status = 'Interrompida'
    chave = data[11]
    motivo = data_request['motivo']
    origem = data[13]

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,codificacao,data_carga,setor,qt_planejada,celula,status,chave,motivo_interrompido,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, codificacao, data_carga,
                setor, qt_planejada, celula, status, chave, motivo, origem))

    conn.commit()

    return 'sucess'


@app.route("/api/consulta-pecas-interrompidas/estamparia", methods=['GET'])
def api_consulta_pecas_interrompidas_estamparia():
    """
    Api para consultar peças com status "interrompida" estamparia
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select * from pcp.tb_pecas_em_processo where status = 'Interrompida' and setor = 'Estamparia' and data_fim isnull order by id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)


@app.route("/api/pecas-retornou/estamparia", methods=['POST'])
def api_pecas_retornou_estamparia():
    """
    rota para enviar peças para status "Em produção" depois de interrompidas estamparia
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.tb_pecas_em_processo set data_fim = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.tb_pecas_em_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    data = data[0]

    codigo = data[1]
    descricao = data[2]
    codificacao = data[4]
    data_carga = data[5]
    setor = 'Estamparia'
    qt_planejada = data[7]
    celula = data[8]
    status = 'Em processo'
    chave = data[11]
    origem = data[13]

    query = """ 
            INSERT INTO pcp.tb_pecas_em_processo (codigo,descricao,codificacao,data_carga,setor,qt_planejada,celula,status,chave,origem) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

    cur.execute(query, (codigo, descricao, codificacao, data_carga,
                setor, qt_planejada, celula, status, chave, origem))

    conn.commit()

    return 'sucess'

# Apontamento corte

@app.route('/tela-apontamento-corte', methods=['GET', 'POST'])
def tela_corte():
    """
    Rota para tela de corte
    """

    return render_template('apontamento-corte.html')

@app.route('/upload-plasma', methods=['GET', 'POST'])
def receber_arquivo_plasma():
    """
    Rota para receber arquivo de geração de op plasma
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']
    # Aqui você pode salvar ou processar o arquivo conforme sua necessidade
    # file.save(file.filename)

    # df = pd.read_excel(r"C:\Users\pcp2\Downloads\OP18486 PL1 #5,32 6000 X 1500.xls")
    nome_arquivo = file.filename
    n_op = str(nome_arquivo.split()[0][2:10])

    query = """select * from pcp.ordens_corte where op = %s"""

    cur.execute(query, (n_op,))
    data = cur.fetchall()

    if not data:

        df = pd.read_excel(file)

        df = df.dropna(how='all')

        tamanho_chapa = df[df.columns[16:17]][9:10].replace('×', 'x')
        qt_chapa = df[df.columns[2:3]][9:10]

        nome_coluna_1 = df[df.columns[0]].name
        aproveitamento_df = df['Unnamed: 16'][4:5]

        df = df[17:df.shape[0]-2]

        df = df[[nome_coluna_1, 'Unnamed: 19', 'Unnamed: 20',
                 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]
        df = df.dropna(how='all')

        espessura_df = df[df.columns[2:3]][2:3]

        df = df[[nome_coluna_1, 'Unnamed: 19',
                 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]

        df = df[2:]

        # quantidade de chapa
        qt_chapa_list = qt_chapa.values.tolist()

        # tamanho da chapa
        tamanho_chapa_list = tamanho_chapa.values.tolist()

        # aproveitamento
        aproveitamento_list = aproveitamento_df.values.tolist()

        # espessura
        espessura_list = espessura_df.values.tolist()

        # Criando colunas na tabela para guardar no bando de dados

        try:
            df = df.loc[:df[df['Unnamed: 19'].isnull()].index[0]-1]
        except:
            pass

        df['Unnamed: 19'] = df['Unnamed: 19'].astype(int)
        df['espessura'] = espessura_list[0][0]
        df['aproveitamento'] = aproveitamento_list[0]
        df['tamanho da chapa'] = tamanho_chapa_list[0][0]
        df['qt. chapas'] = int(qt_chapa_list[0][0])
        df['op'] = n_op

        # reordenar colunas
        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        df = df[cols]

        # df['data criada'] = datetime.today().strftime('%d/%m/%Y')
        df['Máquina'] = 'Plasma'
        df['op_espelho'] = ''
        df['opp'] = 'opp'

        headers = ['op', 'cod_descricao', 'quantidade', 'tamanho', 'peso', 'tempo', 'espessura',
                   'aproveitamento', 'tamanho_chapa', 'qt_chapa', 'maquina', 'op_espelho', 'opp']

        df = df.set_axis(headers, axis=1)

        df['aproveitamento'] = df['aproveitamento'].apply(
            lambda x: "0." + x.replace(',', '').replace('%', ''))

        df_list = df.values.tolist()

        for item in df_list:
            op = item[0]
            cod_descricao = item[1]
            quantidade = item[2]
            tamanho = item[3]
            peso = item[4]
            tempo = item[5]
            espessura = item[6]
            aproveitamento = item[7]
            tamanho_chapa = item[8]
            qt_chapa = item[9]
            maquina = item[10]
            # op_espelho = item[11]
            opp = 'opp'

            query = """insert into pcp.ordens_corte (op,cod_descricao,quantidade,tamanho,peso,tempo,espessura,aproveitamento,tamanho_chapa,qt_chapa,maquina,opp)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

            cur.execute(query, (op, cod_descricao, quantidade, tamanho, peso, tempo,
                        espessura, aproveitamento, tamanho_chapa, qt_chapa, maquina, opp))

        conn.commit()

        return jsonify({'message': 'Arquivo recebido e dados inseridos com sucesso'})

    else:

        return jsonify({'message': 'Op ja aberta!'})

@app.route('/upload-laser', methods=['GET', 'POST'])
def receber_arquivo_laser():
    """
    Rota para receber arquivo de geração de op laser
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']
    comprimento = request.form.get('comprimentoLaser')
    largura = request.form.get('larguraLaser')
    espessura = request.form.get('espessuraLaser')

    nome_arquivo = file.filename

    print(nome_arquivo)
    nome_arquivo = nome_arquivo.split(' ')[0]
    n_op = nome_arquivo[2:len(nome_arquivo)] + ' L1'

    query = """select * from pcp.ordens_corte where op = %s"""

    cur.execute(query, (n_op,))
    data = cur.fetchall()

    if not data:

        df = pd.read_excel(file)
        df1 = pd.read_excel(file, sheet_name='Nestings_Cost')

        df = df.dropna(how='all')
        df1 = df1.dropna(how='all')

        qt_chapas = df1[df1.columns[2:3]][3:4]
        qt_chapas_list = qt_chapas.values.tolist()[0][0]

        try:
            aprov1 = df1[df1.columns[4:5]][7:8]
            aprov2 = df1[df1.columns[4:5]][9:10]
            aprov_list = str(
                1 - (float(aprov2.values.tolist()[0][0]) / float(aprov1.values.tolist()[0][0])))
        except:
            aprov1 = df1[df1.columns[2:3]][7:8]
            aprov2 = df1[df1.columns[2:3]][9:10]
            aprov_list = str(
                1 - (float(aprov2.values.tolist()[0][0]) / float(aprov1.values.tolist()[0][0])))

        df = df[['Unnamed: 1', 'Unnamed: 4']]
        df = df.rename(columns={'Unnamed: 1': 'Descrição',
                                'Unnamed: 4': 'Quantidade'})
        df = df.dropna(how='all')

        df = df[10:len(df)-1]

        df = df.reset_index(drop=True)

        df['op'] = n_op

        cols = df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        df = df[cols]

        print(df)

        df_list = df.values.tolist()

        for item in df_list():
            op = item[0]
            cod_descricao = item[1]
            quantidade = item[2]
            espessura = espessura
            tamanho_chapa = comprimento + ",00 x " + largura + ",00 mm"
            qt_chapa = qt_chapas_list
            maquina = 'Laser'
            opp = 'opp'

            query = """insert into pcp.ordens_corte (op,cod_descricao,quantidade,espessura, aproveitamento,tamanho_chapa,qt_chapa,maquina,opp) 
            values (%s,%s,%s,%s,%s,%s,%s,%s)"""

            cur.execute(query, (op, cod_descricao, quantidade,
                        espessura, tamanho_chapa, qt_chapa, maquina, opp))

        conn.commit()

        return jsonify({'message': 'OP aberta com sucesso.'})
    else:
        return jsonify({'message': 'OP ja foi aberta.'})

@app.route("/api/consulta-pecas-em-processo/corte", methods=['GET'])
def api_consulta_pecas_em_processo_corte():
    """
    Api para consultar peças com status "em processo"
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select distinct ocp.id, ocp.op,
            ocp.data_inicio,ocp.motivo_interrompido,oc.tamanho_chapa,oc.qt_chapa,oc.maquina,oc.espessura
            from pcp.ordens_corte_processo as ocp
            left join pcp.ordens_corte as oc on ocp.op = oc.op
            where ocp.status = 'Em processo' 
            and ocp.data_finalizacao isnull order by ocp.id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)

@app.route("/api/pecas-em-processo-planejamento/corte", methods=['POST'])
def api_pecas_em_processo_planejamento_corte():
    """
    rota para enviar peças para status "em processo" a partir da criação de peça do planejamento
    """

    data = request.json

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    op = data['op']
    status = 'Em processo'

    query = """ 
            INSERT INTO pcp.ordens_corte_processo (op,status) VALUES (%s,%s)
            """

    cur.execute(query, (op, status))

    conn.commit()

    return 'sucess'

@app.route('/planejamento-corte-programacao', methods=['GET'])
def planejamento_corte():
    
    """
    Rota para enviar os itens do planejamento de corte
    """

    # Obter o número da página atual do parâmetro da solicitação
    page = request.args.get('page', 1, type=int)

    # Obter o filtro OP do parâmetro da solicitação
    op_filter = request.args.get('op', None)
    maquina = request.args.get('maquina', None)

    # Definir o número de itens por página
    per_page = 10

    # Calcular o deslocamento com base na página atual e no número de itens por página
    offset = (page - 1) * per_page

    """
    Função para buscar os dados de planejamento da corte
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql_count = """
        SELECT op, qt_chapa, tamanho_chapa, espessura, data_abertura, maquina, coalesce (status,'Aguardando planejamento') as status
        FROM (
            SELECT oc.op, oc.qt_chapa, oc.tamanho_chapa, oc.espessura, oc.data_abertura, oc.maquina, oc.status, ocp.data_finalizacao,
                ROW_NUMBER() OVER (PARTITION BY oc.op ORDER BY oc.data_abertura DESC) AS row_num
            FROM pcp.ordens_corte oc 
            LEFT JOIN pcp.ordens_corte_processo ocp ON oc.op = ocp.op
            WHERE oc.data_abertura > '2024-01-01'
    """

    if op_filter:
        sql_count += f" AND oc.op = '{op_filter}'"
    
    if maquina:
        sql_count += f" AND oc.maquina = '{maquina}'"

    sql_count += """) AS subquery
                WHERE row_num = 1
                ORDER BY data_abertura desc;"""
    
    cur.execute(sql_count)
    data_count = cur.fetchall()

    # Consulta para obter os dados da página atual
    sql = """
        SELECT op, qt_chapa, tamanho_chapa, espessura, data_abertura, maquina, coalesce (status,'Aguardando planejamento') as status
        FROM (
            SELECT oc.op, oc.qt_chapa, oc.tamanho_chapa, oc.espessura, oc.data_abertura, oc.maquina, oc.status, ocp.data_finalizacao,
                ROW_NUMBER() OVER (PARTITION BY oc.op ORDER BY oc.data_abertura DESC) AS row_num
            FROM pcp.ordens_corte oc 
            LEFT JOIN pcp.ordens_corte_processo ocp ON oc.op = ocp.op
            WHERE oc.data_abertura > '2024-01-01'
        """

    if op_filter:
        sql += f" AND oc.op = '{op_filter}'"
    
    if maquina:
        sql += f" AND oc.maquina = '{maquina}'"

    sql += """) AS subquery
                WHERE row_num = 1
                ORDER BY data_abertura desc
                LIMIT %s OFFSET %s;"""

    cur.execute(sql, (per_page, offset))

    # Obter os dados da página atual
    data = cur.fetchall()
    total_rows = len(data_count)

    # Calcular o número total de páginas
    total_pages = (total_rows + per_page - 1) // per_page
    
    return jsonify({
        'data': data,
        'total_pages': total_pages
    })

@app.route("/api/pecas-interrompida/corte", methods=['POST'])
def api_pecas_interrompida_corte():
    
    """
    rota para enviar peças para status "interrompida" corte
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.ordens_corte_processo set data_finalizacao = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.ordens_corte_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    data = data[0]

    op = data[1]
    status = 'Interrompida'
    motivo = data_request['motivo']

    query = """ 
            INSERT INTO pcp.ordens_corte_processo (op,status,motivo_interrompido) VALUES (%s,%s,%s)
            """

    cur.execute(query, (op,status,motivo))

    conn.commit()

    return 'sucess'

@app.route("/api/consulta-pecas-interrompidas/corte", methods=['GET'])
def api_consulta_pecas_interrompidas_corte():
    """
    Api para consultar peças com status "interrompida" estamparia
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """ 
            select distinct ocp.id, ocp.op,
            ocp.data_inicio,ocp.motivo_interrompido,oc.tamanho_chapa,oc.qt_chapa,oc.maquina,oc.espessura
            from pcp.ordens_corte_processo as ocp
            left join pcp.ordens_corte as oc on ocp.op = oc.op
            where ocp.status = 'Interrompida' 
            and ocp.data_finalizacao isnull order by ocp.id desc
            """

    cur.execute(query)
    consulta = cur.fetchall()

    return jsonify(consulta)

@app.route("/api/pecas-retornou/corte", methods=['POST'])
def api_pecas_retornou_corte():
    """
    rota para enviar peças para status "Em produção" depois de interrompidas estamparia
    """

    data_request = request.json

    print(data_request)
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    agora = datetime.now()
    query_update = """update pcp.ordens_corte_processo set data_finalizacao = %s where id = %s"""
    cur.execute(query_update, (agora, data_request['id']))

    conn.commit()

    query_consulta = """select * from pcp.ordens_corte_processo where id = %s"""
    cur.execute(query_consulta, (data_request['id'],))
    data = cur.fetchall()

    data = data[0]

    status = 'Em processo'
    op = data[1]

    query = """ 
            INSERT INTO pcp.ordens_corte_processo (op,status) VALUES (%s,%s)
            """

    cur.execute(query, (op,status))

    conn.commit()

    return 'sucess'

@app.route("/buscar-pecas-dentro-op", methods=['GET'])
def buscar_pecas_dentro_op():
    """
    rota para buscar peças de determinada op
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    op = request.args.get('op')

    query = """select op,cod_descricao,quantidade,espessura,tamanho_chapa,qt_chapa,aproveitamento,status from pcp.ordens_corte where op = %s"""

    cur.execute(query,(op,))
    data = cur.fetchall()
    status_atual = data[0][7]

    # if data_existente:
    #     data_existente = True
    # else:
    #     data_existente = False

    return jsonify({'data':data, "status_atual": status_atual})

@app.route("/finalizar-op/corte", methods=['POST'])
def finalizar_op_corte():
    """
    rota para finalizar op
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    for item in data['tabela']:

        op = data['op']
        cod_descricao = item[0]
        qt_plan = item[1]
        tamanho_chapa = data['descricaoChapa']
        qt_chapas = data['qt_chapa']
        aproveitamento = data['aproveitamento']
        espessura = data['espessura']
        mortas = item[2]
        operador = data['operador']
        
        query = """insert into pcp.ordens_corte_finalizada (op,cod_descricao,qt_plan,tamanho_chapa,qt_chapas,aproveitamento,espessura,mortas,operador)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        cur.execute(query,(op,cod_descricao,qt_plan,tamanho_chapa,qt_chapas,aproveitamento,espessura,mortas,operador))
        # print(op,cod_descricao,qt_plan,tamanho_chapa,qt_chapas,aproveitamento,espessura,mortas,operador)

    query_update = """update pcp.ordens_corte set status = %s where op = %s"""
    status = 'Finalizada'
    cur.execute(query_update,(status,op))

    query_update_processo = """update pcp.ordens_corte_processo set data_finalizacao = %s where op = %s and data_finalizacao ISNULL"""
    agora = datetime.now()
    cur.execute(query_update_processo,(agora,op))

    conn.commit()

    return 'sucess'

@app.route('/tela-planejamento-corte', methods=['GET', 'POST'])
def tela_planejamento():
    """
    Rota para tela de planejamento do corte
    """

    return render_template('programacao-corte.html')

@app.route("/planejar-op/corte", methods=['POST'])
def planejar_op_corte():
    
    """
    rota para planejar op
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    op = data['op']
    data_planejada = data['dataPlanejada']
    status = 'Planejada'

    print(op,data_planejada)

    query_update = """update pcp.ordens_corte set status = %s, data_planejada = %s where op = %s"""

    cur.execute(query_update,(status,data_planejada,op))
    conn.commit()

    return 'sucess'

@app.route('/planejamento-corte', methods=['GET'])
def planejamento_corte_programacao():
    
    """
    Rota para enviar os itens do planejamento da corte
    """

    # Obter o número da página atual do parâmetro da solicitação
    page = request.args.get('page', 1, type=int)

    # Obter o filtro OP do parâmetro da solicitação
    op_filter = request.args.get('op', None)
    maquina = request.args.get('maquina', None)

    # Definir o número de itens por página
    per_page = 10

    # Calcular o deslocamento com base na página atual e no número de itens por página
    offset = (page - 1) * per_page

    """
    Função para buscar os dados de planejamento da corte
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql_count = """
        SELECT DISTINCT oc.op, oc.qt_chapa, oc.tamanho_chapa, oc.espessura, oc.data_abertura, oc.maquina, oc.data_planejada
        FROM pcp.ordens_corte oc 
        LEFT JOIN pcp.ordens_corte_processo ocp ON oc.op = ocp.op
        WHERE oc.data_abertura > '2024-01-01' and oc.status = 'Planejada'
        """
    
    if op_filter:
        sql_count += f" AND oc.op = '{op_filter}'"
    
    if maquina:
        sql_count += f" AND oc.maquina = '{maquina}'"

    sql_count += """
        ORDER BY oc.data_abertura desc;
        """

    cur.execute(sql_count)    
    data_count = cur.fetchall()

    # Consulta para obter os dados da página atual
    sql = """
        SELECT DISTINCT oc.op, oc.qt_chapa, oc.tamanho_chapa, oc.espessura, oc.data_abertura, oc.maquina, oc.data_planejada, ocp.status
        FROM pcp.ordens_corte oc 
        LEFT JOIN pcp.ordens_corte_processo ocp ON oc.op = ocp.op
        WHERE oc.data_abertura > '2024-01-01' and oc.status = 'Planejada'
        """

    if op_filter:
        sql += f" AND oc.op = '{op_filter}'"
    
    if maquina:
        sql += f" AND oc.maquina = '{maquina}'"

    sql += """
        ORDER BY oc.data_abertura desc
        LIMIT %s OFFSET %s;
        """

    cur.execute(sql, (per_page, offset))

    # Obter os dados da página atual
    data = cur.fetchall()
    total_rows = len(data_count)

    # Calcular o número total de páginas
    total_pages = (total_rows + per_page - 1) // per_page

    return jsonify({
        'data': data,
        'total_pages': total_pages
    })

@app.route('/verificar-ordem-iniciar', methods=['GET'])
def verificar_ordem_iniciada():
    
    """
    Rota para verificar se ordem pode ou não ser iniciada
    """
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    op = request.args.get('op')

    query = """select * from pcp.ordens_corte_processo where op = %s"""
    cur.execute(query,(op,))
    data = cur.fetchall()

    return jsonify(data)

@app.route('/consultar-op-criada/corte', methods=['GET'])
def consultar_op_criadas():
    """
    Rota para enviar itens de ops ja criadas
    """

    # Obter o número da página atual do parâmetro da solicitação
    page = request.args.get('page', 1, type=int)

    # Obter o filtro OP do parâmetro da solicitação
    op = request.args.get('opDuplicar', None)
    peca = request.args.get('peca', None)

    # Verifica se há mais de um item na string
    if ',' in peca:
        peca = tuple(peca.split(','))  # Se sim, divide os itens por vírgula e converte para tupla
    else:
        peca = "('" + peca + "')"  # Se não, adiciona parênteses ao redor do único item

    # Definir o número de itens por página
    per_page = 10

    # Calcular o deslocamento com base na página atual e no número de itens por página
    offset = (page - 1) * per_page

    """
    Função para buscar os dados de planejamento da corte
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql_count = """
                select * from (
                    SELECT *,SUBSTRING(cod_descricao, 1, 6) AS peca
                    FROM pcp.ordens_corte) as t1
                where 1=1
            """

    if op:
        sql_count += f' and op = {op}'

    if peca:
        sql_count+=f' and peca in {peca}'

    sql_count += " and quantidade > 0 and opp = 'opp'"

    cur.execute(sql_count)
    data_count = cur.fetchall()
    total_rows = len(data_count)

    sql = """select * from (
                SELECT *,SUBSTRING(cod_descricao, 1, 6) AS peca
                FROM pcp.ordens_corte) as t1
            where 1=1
        """

    if op:
        sql += f' and op = {op}'

    if peca:
        sql+=f' and peca in {peca}'

    sql += " and quantidade > 0 and opp = 'opp' LIMIT %s OFFSET %s;"

    cur.execute(sql,(per_page,offset))
    data = cur.fetchall()

    # Calcular o número total de páginas
    total_pages = (total_rows + per_page - 1) // per_page

    print(data)

    return jsonify({
        'data': data,
        'total_pages': total_pages
    })

@app.route("/duplicar-op/corte", methods=['POST'])
def duplicar_op():
    
    """
    rota para duplicar op
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    op = data['op']
    data_planejada = data['dataPlanejada']
    status = 'Planejada'
    qt_chapas = data['qtChapas']
    maquina = data['maquinaDuplicarOp']

    sql_query = """select * from pcp.ordens_corte where op = %s"""

    cur.execute(sql_query,(op,))
    data_dados_op = cur.fetchall()

    sql_op_numero_duplicada = """select CAST(op AS INTEGER) from pcp.ordens_corte where opp = '' or opp isnull order by id desc limit 1"""
    cur.execute(sql_op_numero_duplicada)
    data_ultima_op_criada = cur.fetchall()
    ultima_op_criada = data_ultima_op_criada[0][0]+1

    status = 'Planejada'
    data_abertura = datetime.today().date()

    for item in data_dados_op:

        qt_peca_nova = (item[3]/float(qt_chapas))  * float(item[10])
        op_espelho = item[1]
        desc_peca = item[2]
        espessura = item[7]
        aproveitamento = item[8][0:20]
        chapa = item[9]
        
        sql_insert = """insert into pcp.ordens_corte (op,cod_descricao,quantidade,espessura,aproveitamento,tamanho_chapa,qt_chapa,data_abertura,maquina,op_espelho,status,data_planejada)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        cur.execute(sql_insert,(ultima_op_criada,desc_peca,qt_peca_nova,espessura,aproveitamento,chapa,qt_chapas,data_abertura,maquina,op_espelho,status,data_planejada))

    conn.commit()

    return 'sucess'

#levantamento

@app.route('/levantamento', methods=['GET'])
def tela_levantamento():


    return render_template('levantamento.html')

@cachetools.cached(cache_carretas)
def buscar_dados(filename):

    """
    Função para acessar google sheets via api e
    buscar dados da base de carretas.
    """

    sheet_id = '1olnMhK7OI6W0eJ-dvsi3Lku5eCYqlpzTGJfh1Q7Pv9I'
    worksheet1 = 'Importar Dados'

    sa = gspread.service_account(filename)
    sh = sa.open_by_key(sheet_id)

    wks1 = sh.worksheet(worksheet1)

    headers = wks1.row_values(1)

    base = wks1.get()
    base = pd.DataFrame(base)
    # base = base.iloc[:,:23]
    base_carretas = base.set_axis(headers, axis=1)[1:]
    base_carretas.iloc[:,5:]
    base_carretas['PED_PREVISAOEMISSAODOC'] = pd.to_datetime(base_carretas['PED_PREVISAOEMISSAODOC'], format="%d/%m/%Y")
    # base_carretas['PED_PREVISAOEMISSAODOC'] = base_carretas['PED_PREVISAOEMISSAODOC'].dt.date
    # base_carretas[base_carretas['4o. Agrupamento'] == 'Santa Maria de Jetiba'].iloc[:,4:]

    return base_carretas

@app.route('/consultar-carreta/levantamento', methods=['GET'])
def consultar_carretas_levantamento():
    """
    Rota para enviar itens de ops ja criadas
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Obter o número da página atual do parâmetro da solicitação
    page = request.args.get('page', 1, type=int)

    # Obter o filtro OP do parâmetro da solicitação
    data = request.args.get('data', None)
    conjunto = request.args.get('conjunto', None)
    celula = request.args.get('celula', None)
    peca = request.args.get('peca', None)
    mp = request.args.get('mp', None)

    data_inicial = pd.to_datetime(data.split(' ')[0])
    
    data_final = data.split(' ')[2]
    
    if data_final == '':
        data_final = data_inicial
    else:
        data_final = pd.to_datetime(data.split(' ')[2])

    dados_carga = buscar_dados(filename)
    dados_carga['PED_PREVISAOEMISSAODOC'] = pd.to_datetime(dados_carga['PED_PREVISAOEMISSAODOC'])
    
    dados_carga_data_filtrada = dados_carga[(dados_carga['PED_PREVISAOEMISSAODOC'] >= data_inicial) & (dados_carga['PED_PREVISAOEMISSAODOC'] <= data_final)]

    dados_carga_data_filtrada['PED_QUANTIDADE'] = dados_carga_data_filtrada['PED_QUANTIDADE'].apply(lambda x: x.replace(',','.'))
    dados_carga_data_filtrada['PED_QUANTIDADE'] = dados_carga_data_filtrada['PED_QUANTIDADE'].astype(float)
    carretas_unica = dados_carga_data_filtrada[['Carreta Trat','PED_QUANTIDADE']]
    agrupado = carretas_unica.groupby('Carreta Trat')['PED_QUANTIDADE'].sum()
    agrupado = agrupado.reset_index()

    nomes_carretas = list(agrupado['Carreta Trat'])

    # Se houver apenas uma carreta, converta para uma única string
    if len(nomes_carretas) == 1:
        nomes_carretas_str = nomes_carretas[0]
    else:
        nomes_carretas_str = ', '.join("'"+carreta +"'" for carreta in nomes_carretas)

    sql_consulta = f"""select * from pcp.tb_base_carretas_explodidas where carreta in ({nomes_carretas_str})"""
    df_explodido = pd.read_sql_query(sql_consulta,conn)

    df_final = df_explodido.merge(agrupado,how='left',right_on='Carreta Trat',left_on='carreta')

    carretas_dentro_da_base=df_explodido.merge(dados_carga_data_filtrada,how='right',left_on='carreta',right_on='Carreta Trat')
    carretas_dentro_da_base = carretas_dentro_da_base[['Carreta Trat','carreta']].drop_duplicates().fillna('').values.tolist()

    df_final['quantidade'] = df_final['quantidade'] * df_final['PED_QUANTIDADE']
    if conjunto:
        df_final = df_final[df_final['conjunto'] == conjunto]

    if celula:
        df_final = df_final[df_final['processo'] == celula]

    if peca:
        df_final = df_final[df_final['codigo'] == peca]
    
    if mp:
        df_final = df_final[df_final['materia_prima'] == mp]

    total_rows = len(df_final)

    # Definir o número de itens por página
    per_page = 10

    total_pages = (total_rows + per_page - 1) // per_page

    # Calcular o deslocamento com base na página atual e no número de itens por página
    offset = (page - 1) * per_page

    # Calculando o índice final
    end_index = offset + per_page

    # Selecionando as linhas do DataFrame com base nos índices calculados
    df_paginated = df_final.drop(columns={'comprimento','largura'})
    df_paginated = df_paginated.iloc[offset:end_index].values.tolist()

    pecas_disponiveis = df_final['codigo'].unique().tolist()
    celulas_disponiveis = df_final['processo'].unique().tolist()
    conjuntos_disponiveis = df_final['conjunto'].unique().tolist()
    matprima_disponiveis = df_final['materia_prima'].unique().tolist()

    return jsonify({
        'data': df_paginated,
        'total_pages': total_pages,
        'pecas':pecas_disponiveis,
        'celula':celulas_disponiveis,
        'conjunto':conjuntos_disponiveis,
        'matprima':matprima_disponiveis,
        'carretas_na_base':carretas_dentro_da_base
    })

@app.route("/solicitar-peca/levantamento", methods=['POST'])
def solicitar_peca_levantamento():
    
    """
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.json

    print(data)

    codigo=data[2]
    quantidade=data[6]
    descricao=data[3]
    conjunto=data[1]
    observacao=data[7]
    origem = 'Levantamento'
    processo = data[0]
    mp = data[5]
    dt_inicio = data[8]
    dt_fim = data[9]

    sql_insert = """insert into software_producao.tb_solicitacao_pecas (codigo,quantidade,descricao,conjunto,observacao,origem,processo,
    materia_prima,data_inicio,data_fim) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cur.execute(sql_insert,(codigo,quantidade,descricao,conjunto,observacao,origem,processo,mp,dt_inicio,dt_fim))
    
    conn.commit()

    return 'SUCESS'

@app.route('/historico-levantamento/levantamento', methods=['GET'])
def consultar_historico_levantamento():
    """
    """

    # Obter o número da página atual do parâmetro da solicitação
    page = request.args.get('page', 1, type=int)

    # Obter o filtro OP do parâmetro da solicitação
    data = request.args.get('data', None)
    conjunto = request.args.get('conjunto', None)
    celula = request.args.get('celula', None)
    peca = request.args.get('peca', None)
    mp = request.args.get('mp', None)
    
    # Definir o número de itens por página
    per_page = 10

    # Calcular o deslocamento com base na página atual e no número de itens por página
    offset = (page - 1) * per_page

    """
    Função para buscar os dados de planejamento da corte
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                            password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """select * from software_producao.tb_solicitacao_pecas
            where 1=1
        """

    sql_count = """select * from software_producao.tb_solicitacao_pecas
            where 1=1
        """

    if data:
        data = pd.to_datetime(data,format="%d/%m/%Y").date()
        print(data)
        sql += f" and '{data}' >= data_inicio AND '{data}' <= data_fim"
        sql_count += f" and '{data}' >= data_inicio AND '{data}' <= data_fim"

    if conjunto:
        sql += f" and conjunto = '{conjunto}'"
        sql_count += f" and conjunto = '{conjunto}'"

    if celula:
        sql += f" and processo = '{celula}'"
        sql_count += f" and processo = '{celula}'"

    if peca:
        sql += f" and codigo = '{peca}'"
        sql_count += f" and codigo = '{peca}'"

    if mp:
        sql += f" and materia_prima = '{mp}'"
        sql_count += f" and materia_prima = '{mp}'"

    sql += " LIMIT %s OFFSET %s;"

    cur.execute(sql,(per_page,offset))
    data = cur.fetchall()

    cur.execute(sql_count)
    data_count = cur.fetchall()

    total_rows = len(data_count)

    # Calcular o número total de páginas
    total_pages = (total_rows + per_page - 1) // per_page

    celula_unica = set()
    mp_unica = set()
    conjunto_unico = set()
    peca_unica = set()

    # Iterar sobre a lista e adicionar os valores da coluna específica ao conjunto
    for sublist in data:

        celula_unica.update([sublist[10]])
        mp_unica.update([sublist[12]])
        conjunto_unico.update([sublist[7]])
        peca_unica.update([sublist[3]])

    return jsonify({
        'data': data,
        'total_pages': total_pages,
        'celulas_historico':list(celula_unica),
        'mp_historico':list(mp_unica),
        'conjunto_historico':list(conjunto_unico),
        'peca_historico':list(peca_unica)
    })



if __name__ == '__main__':
    app.run(debug=True)
