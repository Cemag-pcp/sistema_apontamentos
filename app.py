from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint,send_file
import pandas as pd
import time
import uuid
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

def gerar_id_aleatorio():

    x = str(uuid.uuid4())

    return x
    
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

def formatar_data(data):
    return data.strftime('%d/%m/%Y')

def dados_inspecionar_reinspecionar():

    """
    Função para buscar os dados gerados pelo gerador de cambão
    """

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    inspecao = """SELECT *
                FROM pcp.pecas_inspecao
                ORDER BY id desc"""
    
    cur.execute(inspecao)

    data_inspecao = cur.fetchall()

    inspecaionados= """SELECT i.*, op.peca,op.cor,op.tipo
                FROM pcp.pecas_inspecionadas as i
                LEFT JOIN pcp.ordens_pintura as op ON i.id_inspecao = op.id::varchar
                WHERE i.setor = 'Pintura' """

    cur.execute(inspecaionados)

    data_inspecionadas = cur.fetchall()

    reinspecao = """SELECT r.*, op.peca,op.cor,op.tipo
                FROM pcp.pecas_reinspecao as r
                LEFT JOIN pcp.ordens_pintura as op ON r.id = op.id::varchar
                WHERE r.setor = 'Pintura'"""

    cur.execute(reinspecao)

    data_reinspecao = cur.fetchall()

    return data_inspecao,data_reinspecao,data_inspecionadas

def inserir_reinspecao(id_inspecao,n_nao_conformidades,causa_reinspecao,inspetor,setor,
                       conjunto_especifico='',tipo_nao_conformidade='',outraCausaSolda='',origemInspecaoSolda='',observacaoSolda=''):

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    id_inspecao = str(id_inspecao)

    if setor == 'Pintura':

        delete_table_inspecao = f"""DELETE 
                                FROM pcp.pecas_inspecao 
                                WHERE id = '{id_inspecao}'"""
        
        cur.execute(delete_table_inspecao)

        sql = """INSERT INTO pcp.pecas_reinspecao 
                        (id,nao_conformidades, causa_reinspecao, inspetor,setor) 
                        VALUES (%s, %s, %s, %s, %s)"""
        values = (
            id_inspecao,
            n_nao_conformidades,
            causa_reinspecao,
            inspetor,
            setor
        )

    elif setor == 'Solda':

        sql = """INSERT INTO pcp.pecas_reinspecao 
                        (id,nao_conformidades, causa_reinspecao, inspetor,setor,conjunto,tipo_nao_conformidade,outra_causa,origem,observacao) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
            id_inspecao,
            n_nao_conformidades,
            causa_reinspecao,
            inspetor,
            setor,
            conjunto_especifico,
            tipo_nao_conformidade,
            outraCausaSolda,
            origemInspecaoSolda,
            observacaoSolda
        )

    cur.execute(sql, values)

    conn.commit()

    print("inserir_reinspecao")

def inserir_inspecionados(id_inspecao,n_conformidades,inspetor,setor,
                          conjunto_especifico='',origemInspecaoSolda='',observacaoSolda=''):

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    id_inspecao = str(id_inspecao)

    if setor == 'Pintura':

        delete_table_inspecao = f"""DELETE 
                                FROM pcp.pecas_inspecao 
                                WHERE id = '{id_inspecao}'"""
        
        cur.execute(delete_table_inspecao)

        sql = """INSERT INTO pcp.pecas_inspecionadas 
                        (id_inspecao,total_conformidades, inspetor, setor,num_inspecao) 
                        VALUES (%s, %s, %s,%s,0)"""
        values = (
            id_inspecao,
            n_conformidades,
            inspetor,
            setor
        )
    
    elif setor == 'Solda':

        sql = """INSERT INTO pcp.pecas_inspecionadas 
                        (id_inspecao,total_conformidades, inspetor, setor,num_inspecao,conjunto,origem,observacao) 
                        VALUES (%s, %s, %s,%s,0,%s,%s,%s)"""
        values = (
            id_inspecao,
            n_conformidades,
            inspetor,
            setor,
            conjunto_especifico,
            origemInspecaoSolda,
            observacaoSolda
        )

    cur.execute(sql, values)

    conn.commit()

    print("inserir_inspecionados")

def alterar_reinspecao(id_inspecao,n_nao_conformidades,qtd_produzida,n_conformidades,causa_reinspecao,inspetor,setor,
                       conjunto_especifico='',tipo_nao_conformidade='',outraCausaSolda='',origemInspecaoSolda='',observacaoSolda=''):

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    id_inspecao = str(id_inspecao)

    if setor == 'Pintura':

        if n_conformidades == "0":

            sql_uptdade = """UPDATE pcp.pecas_reinspecao 
                    SET causa_reinspecao = %s, inspetor = %s
                    WHERE id = %s """
            
            values = (
                causa_reinspecao,
                inspetor,
                id_inspecao
            )

            cur.execute(sql_uptdade, values)

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 
                                            (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                        );
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """

            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor
            )

            cur.execute(sql_insert, values)

        elif n_conformidades > "0" and n_conformidades < qtd_produzida:

            sql_uptdade = """UPDATE pcp.pecas_reinspecao 
                    SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s
                    WHERE id = %s """
            
            values = (
                n_nao_conformidades,
                causa_reinspecao,
                inspetor,
                id_inspecao
            )

            cur.execute(sql_uptdade, values)

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 
                                            (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                        );
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """

            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor
            )

            cur.execute(sql_insert, values)

        elif n_conformidades == qtd_produzida:

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 
                                            (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                        );
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """

            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor
            )

            cur.execute(sql_insert, values)

            delete_table_inspecao = f"""DELETE 
                                FROM pcp.pecas_reinspecao 
                                WHERE id = '{id_inspecao}'"""
        
            cur.execute(delete_table_inspecao)

    elif setor == 'Solda':

        if n_conformidades == "0":

            sql_uptdade = """UPDATE pcp.pecas_reinspecao 
                    SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s, tipo_nao_conformidade = %s,
                    outra_causa = %s, origem = %s, observacao = %s
                    WHERE id = %s """

            values = (
                n_nao_conformidades,
                causa_reinspecao,
                inspetor,
                tipo_nao_conformidade,
                outraCausaSolda,
                origemInspecaoSolda,
                observacaoSolda,
                id_inspecao
            )

            cur.execute(sql_uptdade, values)

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """
            
            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda
            )

            cur.execute(sql_insert, values)

        elif n_conformidades > "0" and n_conformidades < qtd_produzida:

            sql_uptdade = """UPDATE pcp.pecas_reinspecao 
                    SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s, tipo_nao_conformidade = %s,
                    outra_causa = %s, origem = %s, observacao = %s
                    WHERE id = %s """
            # conjunto_especifico='',tipo_nao_conformidade='',outraCausaSolda='',origemInspecaoSolda='',observacaoSolda=''
            values = (
                n_nao_conformidades,
                causa_reinspecao,
                inspetor,
                tipo_nao_conformidade,
                outraCausaSolda,
                origemInspecaoSolda,
                observacaoSolda,
                id_inspecao
            )

            cur.execute(sql_uptdade, values)

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """
            
            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda
            )

            cur.execute(sql_insert, values)

        elif n_conformidades == qtd_produzida:

            sql_insert = """DO $$
                            BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas
                                        (id_inspecao, total_conformidades, inspetor, setor, conjunto, origem, observacao, num_inspecao) 
                                    VALUES 
                                        (%s, %s, %s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;
                        """
            
            values = (
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda,
                id_inspecao,
                id_inspecao,
                n_conformidades,
                inspetor,
                setor,
                conjunto_especifico,
                origemInspecaoSolda,
                observacaoSolda
            )

            cur.execute(sql_insert, values)

            delete_table_inspecao = f"""DELETE 
                                FROM pcp.pecas_reinspecao 
                                WHERE id = '{id_inspecao}'"""
        
            cur.execute(delete_table_inspecao)
    
    print('alterar_reinspecao')

    conn.commit()

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

            #  Construir e executar a consulta UPDATE
            
            query = ("UPDATE pcp.ordens_pintura SET status = 'OK' WHERE id = %s")
            cursor.execute(query, (str(dado['chave']),))
    
            sql = """INSERT INTO pcp.pecas_inspecao 
                     (id, data_finalizada,codigo, peca, cor, qt_apontada, tipo, setor) 
                     VALUES (%s, NOW(),%s, %s, %s, %s, %s, 'Pintura')"""
            values = (
                dado['chave'],
                dado['codigo'],
                dado['descricao'],
                dado['cor'],
                dado['prod'],
                dado['tipo']
            )
            cursor.execute(sql, values)

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

@app.route('/inspecao', methods=['GET','POST'])
def inspecao():

    """
    Rota para página de inspecao
    """
    if request.method == 'POST':

        data = request.get_json()

        id_inspecao = data['id_inspecao']
        data_inspecao = data['data_inspecao']
        data_inspecao_obj = datetime.strptime(data_inspecao, "%d/%m/%Y")

        # Converter de volta para string no formato desejado
        data_inspecao = data_inspecao_obj.strftime("%Y-%m-%d")

        n_nao_conformidades = data['n_nao_conformidades']
        n_conformidades = data['n_conformidades_value']
        causa_reinspecao = data['causa_reinspecao']
        inspetor = data['inspetor']
        qtd_produzida = data['qtd_produzida']
        setor = 'Pintura'

        # Identificar se veio do modal de reinspecoes ou não
        modal_reinspecao = data['reinspecao']
        if modal_reinspecao:
            alterar_reinspecao(id_inspecao,n_nao_conformidades,qtd_produzida,n_conformidades,causa_reinspecao,inspetor,setor)
            return jsonify("Success")
        
        else:
            if n_conformidades != qtd_produzida:
                inserir_reinspecao(id_inspecao,n_nao_conformidades,causa_reinspecao,inspetor,setor)
                inserir_inspecionados(id_inspecao,n_conformidades,inspetor,setor)
            else:
                inserir_inspecionados(id_inspecao,n_conformidades,inspetor,setor)

            return jsonify("Success")

    inspecoes,reinspecoes,inspecionadas = dados_inspecionar_reinspecionar()

    return render_template('inspecao.html',inspecoes=inspecoes,reinspecoes=reinspecoes,inspecionadas=inspecionadas)

@app.route('/inspecao-solda',methods=['GET','POST'])
def solda():

    if request.method == 'POST':

        data = request.get_json()

        data_inspecao = data['data_inspecao']
        data_inspecao_obj = datetime.strptime(data_inspecao, "%d/%m/%Y")

        # Converter de volta para string no formato desejado
        data_inspecao = data_inspecao_obj.strftime("%Y-%m-%d")
        
        inspetor = data['inspetor']
        conjunto_especifico = data['conjunto_especifico']
        num_pecas = data['num_pecas']
        num_conformidades = data['num_conformidades']
        num_nao_conformidades = data['num_nao_conformidades']
        tipo_nao_conformidade = data['tipo_nao_conformidade']
        causaSolda = data['causaSolda']
        outraCausaSolda = data['outraCausaSolda']
        origemInspecaoSolda = data['origemInspecaoSolda']
        observacaoSolda = data['observacaoSolda']
        setor = 'Solda'
        reinspecao = data['modal_reinspecao_solda']

        try:
            id_inspecao_solda = data['id_inspecao_solda']
        except:
            id_inspecao_solda = gerar_id_aleatorio()

        if reinspecao:
            alterar_reinspecao(id_inspecao_solda,num_nao_conformidades,num_pecas,num_conformidades,causaSolda,inspetor,setor,
                               conjunto_especifico,tipo_nao_conformidade,outraCausaSolda,origemInspecaoSolda,observacaoSolda)
            return jsonify("Success")
        
        else:
            if num_conformidades != num_pecas:
                inserir_reinspecao(id_inspecao_solda,num_nao_conformidades,causaSolda,inspetor,setor,conjunto_especifico,
                                   tipo_nao_conformidade,outraCausaSolda,origemInspecaoSolda,observacaoSolda)
                inserir_inspecionados(id_inspecao_solda,num_conformidades,inspetor,setor,conjunto_especifico,
                                      origemInspecaoSolda,observacaoSolda)
            else:
                inserir_inspecionados(id_inspecao_solda,num_conformidades,inspetor,setor,conjunto_especifico,
                                      origemInspecaoSolda,observacaoSolda)

            return jsonify("Success")
        
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query_inspecao = """SELECT *
            FROM pcp.pecas_inspecionadas
            WHERE setor = 'Solda'"""
    
    cur.execute(query_inspecao)

    inspecoes_solda = cur.fetchall()

    for item in inspecoes_solda:
        if isinstance(item[1], datetime):
            item[1] = formatar_data(item[1])

    print(inspecoes_solda)

    query_reinspecao = """SELECT *
            FROM pcp.pecas_reinspecao
            WHERE setor = 'Solda'"""
    
    cur.execute(query_reinspecao)

    reinspecoes_solda = cur.fetchall()

    for item in reinspecoes_solda:
        if isinstance(item[1], datetime):
            item[1] = formatar_data(item[1])
    
    return render_template('inspecao-solda.html',inspecoes_solda=inspecoes_solda,reinspecoes_solda=reinspecoes_solda)

@app.route('/conjuntos', methods=['POST'])
def listar_conjuntos():
    """
    Função para buscar conjuntos disponíveis
    """
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    data = request.get_json()

    conjunto = data['conjuntos']

    sql = f"""SELECT DISTINCT descricao
            FROM pcp.base_pecas_sequenciamento
            WHERE celula = '{conjunto}'"""

    cur.execute(sql)

    data = cur.fetchall()

    return jsonify(data)

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
    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula'] else ('EIC' if 'EIXO COMPLETO' in row['celula'] else row['celula'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%d%m%Y").dt.strftime("%Y-%m-%d")

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
    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula'] else ('EIC' if 'EIXO COMPLETO' in row['celula'] else row['celula'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%d%m%Y").dt.strftime("%Y-%m-%d")

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
    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%Y-%m-%d").dt.strftime("%d%m%Y")

    df['codificacao'] = df.apply(lambda row: 'EIS' if 'EIXO SIMPLES' in row['celula_nova'] else ('EIC' if 'EIXO COMPLETO' in row['celula_nova'] else row['celula_nova'][:3]), axis=1) + df['data_carga'].str.replace('-', '')

    df['data_carga'] = pd.to_datetime(df['data_carga'],format="%d%m%Y").dt.strftime("%Y-%m-%d")

    # Fecha a conexão com o PostgreSQL
    conn.close()

    # Salva os dados em um arquivo CSV temporário
    temp_file_path = 'apontamento_pintura.csv'
    df.to_csv(temp_file_path, index=False)

    # Retorna o arquivo CSV como resposta
    return send_file(temp_file_path, mimetype='text/csv', as_attachment=True, download_name='apontamento_pintura.csv')


if __name__ == '__main__':
    app.run(debug=True)