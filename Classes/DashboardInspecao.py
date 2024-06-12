import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import request

class DashboardInspecao:

    def __init__(self, cur):
        self.cur = cur

    def dados_pintura(cur,data_inicial,data_final):
        query_dash_pintura = f"""
        WITH pecas_inspecionadas AS (
            SELECT 
                TO_CHAR(data_inspecao, 'YYYY-Month') AS ano_mes,
                EXTRACT(MONTH FROM data_inspecao) AS mes,
                EXTRACT(YEAR FROM data_inspecao) AS ano,
                SUM(CASE WHEN num_inspecao = 0 THEN nao_conformidades ELSE 0 END) AS total_nao_conformidades,
                SUM(CASE WHEN num_inspecao = 0 THEN total_conformidades + nao_conformidades ELSE 0 END) AS num_inspecoes
            FROM pcp.pecas_inspecionadas
            WHERE setor = 'Pintura'
            AND data_inspecao BETWEEN '{data_inicial}' AND '{data_final}'
            GROUP BY TO_CHAR(data_inspecao, 'YYYY-Month'), EXTRACT(MONTH FROM data_inspecao), EXTRACT(YEAR FROM data_inspecao)
        ),
        pecas_inspecao AS (
            SELECT 
                EXTRACT(MONTH FROM data_finalizada) AS mes,
                EXTRACT(YEAR FROM data_finalizada) AS ano,
                SUM(qt_apontada) FILTER (WHERE setor = 'Pintura') AS num_pecas_produzidas
            FROM pcp.pecas_inspecao
            WHERE setor = 'Pintura' 
            AND data_finalizada BETWEEN '{data_inicial}' AND '{data_final}'
            GROUP BY EXTRACT(MONTH FROM data_finalizada), EXTRACT(YEAR FROM data_finalizada)
        )
        SELECT 
            COALESCE(pi2.ano_mes, TO_CHAR(TO_DATE(pi.ano || '-' || pi.mes, 'YYYY-MM'), 'YYYY-Month'||'❌')) AS ano_mes,
            COALESCE(pi.num_pecas_produzidas, 0) AS num_pecas_produzidas,
            COALESCE(pi2.num_inspecoes, 0) AS num_inspecoes,
            COALESCE(pi2.total_nao_conformidades, 0) AS total_nao_conformidades,
            COALESCE(
                ROUND(
                    100.0 * COALESCE(pi2.num_inspecoes, 0) / NULLIF(COALESCE(pi.num_pecas_produzidas, 0), 0), 2
                ), 0
            ) AS porcentagem_inspecao,
            COALESCE(
                ROUND(
                    100.0 * COALESCE(pi2.total_nao_conformidades, 0) / NULLIF(COALESCE(pi2.num_inspecoes, 0), 0), 2
                ), 0
            ) AS porcentagem_nao_conformidades
        FROM pecas_inspecionadas pi2
        FULL OUTER JOIN pecas_inspecao pi
        ON pi2.mes = pi.mes AND pi2.ano = pi.ano
        ORDER BY COALESCE(pi2.ano, pi.ano), COALESCE(pi2.mes, pi.mes);
        """
        cur.execute(query_dash_pintura)
        return cur.fetchall()

    def dados_causas_pintura(cur,data_inicial,data_final):

        query_total_causas = f"""
                SELECT ano_mes,
                    causa,
                    SUM(total_quantidade) as total_quantidade
                FROM (
                    SELECT DISTINCT TO_CHAR(pi.data_inspecao, 'YYYY-Month') as ano_mes,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecionadas pi ON pi.id_inspecao = foto.id
                    WHERE pi.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND foto.num_inspecao = 0
                ) AS subquery
                GROUP BY ano_mes, causa
                ORDER BY ano_mes desc;
            """
        cur.execute(query_total_causas)
        total_causas = cur.fetchall()

        # Para obter a soma de todos os total_quantidade
        query_soma_total = f"""
            SELECT SUM(total_quantidade) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_inspecao, 'YYYY-Month') as ano_mes,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecionadas pi ON pi.id_inspecao = foto.id
                WHERE pi.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND foto.num_inspecao = 0
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        query_total_liquida = f"""
                SELECT DISTINCT TO_CHAR(pi2.data_inspecao, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                FROM pcp.pecas_inspecao pi
            LEFT JOIN pcp.pecas_inspecionadas pi2 ON pi.id = pi2.id_inspecao
            LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
            WHERE pi2.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND pi.tipo = 'PU' 
        """
        cur.execute(query_total_liquida)
        total_liquida = cur.fetchall()

        query_soma_total_liquida = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi2.data_inspecao, 'YYYY-Month') as ano_mes,pi.tipo,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.pecas_inspecionadas pi2 ON pi.id = pi2.id_inspecao
                LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
                WHERE pi2.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND pi.tipo = 'PU' 
            ) AS subquery;
        """

        cur.execute(query_soma_total_liquida)
        soma_total_liquida = cur.fetchone()

        query_total_po = f"""
            SELECT DISTINCT TO_CHAR(pi2.data_inspecao, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                FROM pcp.pecas_inspecao pi
            LEFT JOIN pcp.pecas_inspecionadas pi2 ON pi.id = pi2.id_inspecao
            LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
            WHERE pi2.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND pi.tipo = 'PÓ' 
        """
        cur.execute(query_total_po)
        total_po = cur.fetchall()

        query_soma_total_po = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi2.data_inspecao, 'YYYY-Month') as ano_mes,pi.tipo,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.pecas_inspecionadas pi2 ON pi.id = pi2.id_inspecao
                LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
                WHERE pi2.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND pi.tipo = 'PÓ' 
            ) AS subquery;
        """

        cur.execute(query_soma_total_po)
        soma_total_po = cur.fetchone()

        return total_causas,soma_total,total_liquida,soma_total_liquida,total_po,soma_total_po

    def fotos_pintura(cur,data_inicial,data_final):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_inspecao, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecionadas pi2 ON foto.id = pi2.id_inspecao
                WHERE pi2.data_inspecao BETWEEN '{data_inicial}' AND '{data_final}' AND caminho_foto NOTNULL 
                ORDER BY ano_mes DESC
            """
        cur.execute(query_fotos)
        fotos = cur.fetchall()

        return fotos

    def fechar_conexao(self):
        self.cur.close()
        self.conn.close()
