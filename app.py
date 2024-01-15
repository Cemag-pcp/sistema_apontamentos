from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint
import pandas as pd
import time
import datetime
import psycopg2  # pip install psycopg2
import psycopg2.extras 
from psycopg2.extras import execute_values
from datetime import datetime
import cachetools

app = Flask(__name__)
app.secret_key = "apontamentopintura"

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"

cache_historico_pintura = cachetools.LRUCache(maxsize=128)

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

    df = pd.read_sql_query(sql,conn)

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
    
    df = pd.read_sql_query(sql,conn)

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

    df = pd.read_sql_query(sql,conn)

    return df


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

    df = pd.read_sql_query(sql,conn)

    return df


@app.route('/', methods=['GET'])
def pagina_inicial():

    """
    Rota para página inicial
    """

    return render_template('pagina-branco.html')


@app.route('/gerar-cambao', methods=['GET','POST'])
def gerar_cambao():

    """
    Rota para página de gerar cambão
    """

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['id','data_carga','codigo','peca','restante','cor','qt_produzida','cambao','tipo','codificacao']]
    sheet_data = table.values.tolist()

    return render_template('gerar-cambao.html', sheet_data=sheet_data)


@app.route('/send_gerar', methods=['POST'])
def gerar_planilha():
    
    """
    Rota para receber a resposta da geração de cambão
    """

    # dados = request.get_json()
    
    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                    password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lista de tuplas contendo os dados a serem inseridos
    values = [(linha['codigo'], linha['descricao'], linha['qt_itens'], linha['cor'], linha['prod'], linha['cambao'], linha['tipo'], datetime.strptime(linha['data'],'%d/%m/%Y').strftime('%Y-%m-%d'), datetime.now().date(), linha['celula'], linha['chave']) for linha in dados_recebidos]

    print(values)

    # Sua string de consulta com marcadores de posição (%s) adequados para cada valor
    query = """INSERT INTO pcp.ordens_pintura (codigo, peca, qt_planejada, cor, qt_apontada, cambao, tipo, data_carga, data_finalizada, celula, chave) VALUES %s"""

    # Use execute_values para inserir várias linhas de uma vez
    execute_values(cur, query, values)

    # Comitar as alterações
    conn.commit()

    # Fechar a conexão
    cur.close()
    conn.close()

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga','codigo','peca','restante','cor','qt_produzida','cambao','tipo','codificacao']]
    sheet_data = table.values.tolist()

    return jsonify({"linhas": sheet_data})


@app.route('/finalizar-cambao', methods=['GET','POST'])
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
    cur.execute(sql_search,(codigo,))
    registro = cur.fetchall()

    if len(registro) > 0:
        celula = registro[0][0]
    else:
        celula = ''

    today = datetime.now().date()
    
    data_carga_formatada = datetime.strptime(data['dataCarga'], '%Y-%m-%d').strftime('%d/%m/%Y')
    
    # Se caso o usuário informar apenas o primeiro nome do conjunto
    try:
        descricao = data['peca'].split(' - ')[1]
    except IndexError:
        descricao = ''

    sql_insert = "insert into pcp.ordens_pintura (codigo,peca,qt_planejada,cor,qt_apontada,cambao,tipo,data_carga,data_finalizada,celula) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(sql_insert,(codigo,
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


@app.route('/apontar-montagem', methods=['GET','POST'])
def apontar_montagem():

    """
    Rota para página de apontamento de montagem
    """

    table = dados_sequenciamento_montagem()
    table['qt_produzida'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga','celula','codigo','peca','qt_planejada','qt_produzida','codificacao']]

    sheet_data = table.values.tolist()

    return render_template('apontamento-montagem.html', sheet_data=sheet_data)


@app.route('/salvar-apontamento-montagem', methods=['GET','POST'])
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
                datetime.strptime(linha['data'],'%d/%m/%Y').strftime('%Y-%m-%d'), datetime.now().date(),
                linha['operador'], linha['obs'], linha['codificacao'],'Sequenciamento') for linha in dados_recebidos]

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
    cur.execute(sql_insert,(celula,
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
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['data_finalizada'] = pd.to_datetime(table['data_finalizada']).dt.strftime("%d/%m/%Y")

    sheet_data = table.values.tolist()

    return render_template('historico-pintura.html', sheet_data=sheet_data)


@app.route('/limpar-cache-historico', methods=['POST'])
def limpar_cache_historico():

    cache_historico_pintura.clear()

    return render_template('historico-pintura.html')


@app.route('/planejar-pintura', methods=['GET','POST'])
def planejar_pintura():

    """
    Rota para página de gerar cambão
    """

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga','codigo','peca','restante','cor','qt_produzida','cambao','tipo','codificacao']]
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
            data = datetime.strptime(dado['data'],'%d/%m/%Y').strftime('%Y-%m-%d')
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


@app.route('/planejar-montagem', methods=['GET','POST'])
def planejar_montagem():

    """
    Rota para página planejamento da montagem
    """

    table = dados_sequenciamento_montagem()
    table['qt_produzida'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table['codificacao'] = table.apply(criar_codificacao, axis=1)

    table = table[['data_carga','codigo','peca','qt_planejada','qt_produzida','codificacao','celula']]
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
            data = datetime.strptime(dado['data'],'%d/%m/%Y').strftime('%Y-%m-%d')
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

    sql = "select * from pcp.ordens_pintura where data_carga > '2024-01-01'"

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


if __name__ == '__main__':
    app.run(debug=True)