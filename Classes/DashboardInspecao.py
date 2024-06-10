import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import request

class DashboardInspecao:

    def __init__(self, cur):
        self.cur = cur

    @staticmethod
    def dados_pintura(cur,data_inicial,data_final):
        query_dash_pintura = f"""
        WITH pecas_inspecionadas AS (
            SELECT 
                TO_CHAR(data_inspecao, 'YYYY-Month') AS ano_mes,
                EXTRACT(MONTH FROM data_inspecao) AS mes,
                EXTRACT(YEAR FROM data_inspecao) AS ano,
                SUM(nao_conformidades) AS total_nao_conformidades
            FROM pcp.pecas_inspecionadas
            WHERE setor = 'Pintura'
            AND data_inspecao BETWEEN '{data_inicial}' AND '{data_final}'
            GROUP BY TO_CHAR(data_inspecao, 'YYYY-Month'), EXTRACT(MONTH FROM data_inspecao), EXTRACT(YEAR FROM data_inspecao)
        ),
        pecas_inspecao AS (
            SELECT 
                EXTRACT(MONTH FROM data_finalizada) AS mes,
                EXTRACT(YEAR FROM data_finalizada) AS ano,
                SUM(qt_apontada) FILTER (WHERE setor = 'Pintura') AS num_pecas_produzidas,
                SUM(qt_apontada) FILTER (WHERE setor = 'Pintura' AND excluidas = 'true') AS num_inspecoes
            FROM pcp.pecas_inspecao
            WHERE setor = 'Pintura' 
            AND data_finalizada BETWEEN '{data_inicial}' AND '{data_final}'
            GROUP BY EXTRACT(MONTH FROM data_finalizada), EXTRACT(YEAR FROM data_finalizada)
        )
        SELECT 
            pi2.ano_mes,
            COALESCE(pi.num_pecas_produzidas, 0) AS num_pecas_produzidas,
            COALESCE(pi.num_inspecoes, 0) AS num_inspecoes,
            COALESCE(pi2.total_nao_conformidades, 0) AS total_nao_conformidades,
            COALESCE(
                ROUND(
                    100.0 * COALESCE(pi.num_inspecoes, 0) / NULLIF(COALESCE(pi.num_pecas_produzidas, 0), 0), 2
                ), 0
            ) AS porcentagem_inspecao,
            COALESCE(
                ROUND(
                    100.0 * COALESCE(pi2.total_nao_conformidades, 0) / NULLIF(COALESCE(pi.num_inspecoes, 0), 0), 2
                ), 0
            ) AS porcentagem_nao_conformidades
        FROM pecas_inspecionadas pi2
        LEFT JOIN pecas_inspecao pi
        ON pi2.mes = pi.mes AND pi2.ano = pi.ano
        ORDER BY pi2.ano, pi2.mes
        """
        cur.execute(query_dash_pintura)
        return cur.fetchall()

    def fechar_conexao(self):
        self.cur.close()
        self.conn.close()
