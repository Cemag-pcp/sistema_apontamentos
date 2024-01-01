from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, Blueprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
from gspread_formatting import CellFormat, format_cell_range
import datetime
import cachetools
import psycopg2  # pip install psycopg2
import psycopg2.extras 
from psycopg2.extras import execute_values
from datetime import datetime

app = Flask(__name__)
app.secret_key = "apontamentopintura"

cache_get_sheet = cachetools.LRUCache(maxsize=128)
cache_tipos_tinta = cachetools.LRUCache(maxsize=128)
cache_producao_finalizada = cachetools.LRUCache(maxsize=128)
cache_itens_pintura = cachetools.LRUCache(maxsize=128)

DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"


def dados_finalizar_cambao():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """SELECT *
            FROM pcp.ordens_pintura
            WHERE COALESCE(status, '') = '';"""

    df = pd.read_sql_query(sql,conn)

    df['status'] = df['status'].fillna('')
    
    df['data_carga'] = pd.to_datetime(df['data_carga']).dt.strftime("%d/%m/%Y")

    return df


def dados_sequenciamento():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = """SELECT
                gerador_ordens_pintura.*,
                COALESCE(ordens_pintura.qt_apontada, 0) as qt_apontada,
                ABS(gerador_ordens_pintura.qt_planejada - COALESCE(ordens_pintura.qt_apontada, 0)) as restante
            FROM
                pcp.gerador_ordens_pintura
            LEFT JOIN (
                SELECT
                    data_carga,
                    codigo,
                    SUM(qt_apontada) as qt_apontada
                FROM
                    pcp.ordens_pintura
                GROUP BY
                    data_carga, codigo
            ) ordens_pintura
            ON
                concat(gerador_ordens_pintura.data_carga, gerador_ordens_pintura.codigo) = concat(ordens_pintura.data_carga, ordens_pintura.codigo)
            order by id desc
            LIMIT 500;"""

    df = pd.read_sql_query(sql,conn)

    return df


@app.route('/gerar-cambao', methods=['GET','POST'])
def gerar_cambao():

    table = dados_sequenciamento()
    table['qt_produzida'] = ''
    table['cambao'] = ''
    table['tipo'] = ''
    table['data_carga'] = pd.to_datetime(table['data_carga']).dt.strftime("%d/%m/%Y")
    table = table[['data_carga','codigo','peca','restante','cor','qt_produzida','cambao','tipo']]

    sheet_data = table.values.tolist()

    return render_template('gerar-cambao.html', sheet_data=sheet_data)


@app.route('/send_gerar', methods=['GET','POST'])
def gerar_planilha():

    # dados = request.get_json()
    
    dados_recebidos = request.json['linhas']

    print(dados_recebidos)

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                    password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Lista de tuplas contendo os dados a serem inseridos
    values = [(linha['codigo'], linha['descricao'], linha['qt_itens'], linha['cor'], linha['prod'], linha['cambao'], linha['tipo'], datetime.strptime(linha['data'],'%d/%m/%Y').strftime('%Y-%m-%d'), datetime.now().date(), 'Pintura') for linha in dados_recebidos]

    print(values)

    # Sua string de consulta com marcadores de posição (%s) adequados para cada valor
    query = """INSERT INTO pcp.ordens_pintura (codigo, peca, qt_planejada, cor, qt_apontada, cambao, tipo, data_carga, data_finalizada, setor) VALUES %s"""

    # Use execute_values para inserir várias linhas de uma vez
    execute_values(cur, query, values)

    # Comitar as alterações
    conn.commit()

    # Fechar a conexão
    cur.close()
    conn.close()

    return redirect(url_for("gerar_cambao"))

   
@app.route('/gerar-cambao-peca-fora-do-planejamento', methods=['POST'])
def gerar_cambao_peca_fora_do_planejamento():

    return redirect(url_for('gerar_cambao'))


@app.route('/finalizar-cambao', methods=['GET','POST'])
def finalizar_cambao():

    table = dados_finalizar_cambao()

    sheet_data = table.values.tolist()

    return render_template('finalizar-cambao.html', sheet_data=sheet_data)


@app.route("/receber-dados-finalizar-cambao", methods=['POST'])
def receber_dados_finalizar_cambao():

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

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                    password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    sql = 'SELECT * FROM pcp.ordens_pintura WHERE status ISNULL'

    cur.execute(sql)
    data = cur.fetchall()

    return render_template("painel.html", datas=data)

if __name__ == '__main__':
    app.run(debug=True)