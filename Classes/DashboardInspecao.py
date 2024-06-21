import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import request

class DashboardInspecao:

    def __init__(self, cur, data_inicial,data_final):
        self.cur = cur
        self.data_inicial = data_inicial
        self.data_final = data_final

    def dadosPintura(self,cur):
        query_dash_pintura = f"""
        WITH pecas_inspecionadas AS (
            SELECT 
                TO_CHAR(inspecao.data_finalizada, 'YYYY-Month') AS ano_mes,
                EXTRACT(MONTH FROM inspecao.data_finalizada) AS mes,
                EXTRACT(YEAR FROM inspecao.data_finalizada) AS ano,
                SUM(CASE WHEN inspecionadas.num_inspecao = 0 THEN inspecionadas.nao_conformidades ELSE 0 END) AS total_nao_conformidades,
                SUM(CASE WHEN inspecionadas.num_inspecao = 0 THEN inspecionadas.total_conformidades + inspecionadas.nao_conformidades ELSE 0 END) AS num_inspecoes
            FROM pcp.pecas_inspecionadas AS inspecionadas
            LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id = inspecionadas.id_inspecao
            WHERE inspecionadas.setor = 'Pintura' AND inspecao.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
            GROUP BY TO_CHAR(inspecao.data_finalizada, 'YYYY-Month'), EXTRACT(MONTH FROM inspecao.data_finalizada), EXTRACT(YEAR FROM inspecao.data_finalizada)
        ),
        pecas_inspecao AS (
            SELECT  
                EXTRACT(MONTH FROM data_finalizada) AS mes,
                EXTRACT(YEAR FROM data_finalizada) AS ano,
                SUM(qt_apontada) FILTER (WHERE setor = 'Pintura') AS num_pecas_produzidas
            FROM pcp.pecas_inspecao
            WHERE setor = 'Pintura' 
            AND data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
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

    def dadosCausasPinturas(self,cur):

        query_total_causas = f"""
                SELECT ano_mes,
                    causa,
                    SUM(total_quantidade) as total_quantidade
                FROM (
                    SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                    WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Pintura'
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
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                    foto.causa,
                    foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Pintura'
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        query_total_liquida = f"""
            SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                FROM pcp.pecas_inspecao pi
            LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
            WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PU' AND foto.causa NOTNULL
        """
        cur.execute(query_total_liquida)
        total_liquida = cur.fetchall()

        query_soma_total_liquida = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PU' AND foto.causa NOTNULL
            ) AS subquery;
        """

        cur.execute(query_soma_total_liquida)
        soma_total_liquida = cur.fetchone()

        query_total_po = f"""
            SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                FROM pcp.pecas_inspecao pi
            LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
            WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PÓ' AND pi.setor = 'Pintura' AND foto.causa NOTNULL
        """
        cur.execute(query_total_po)
        total_po = cur.fetchall()

        query_soma_total_po = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.inspecao_foto foto ON pi.id = foto.id::varchar
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PÓ' AND pi.setor = 'Pintura' AND foto.causa NOTNULL
            ) AS subquery;
        """

        cur.execute(query_soma_total_po)
        soma_total_po = cur.fetchone()

        return total_causas,soma_total,total_liquida,soma_total_liquida,total_po,soma_total_po

    def fotosPintura(self,cur):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id
                WHERE pi2.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND caminho_foto NOTNULL AND pi2.setor = 'Pintura'
                ORDER BY ano_mes DESC
            """
        cur.execute(query_fotos)
        fotos = cur.fetchall()

        return fotos
    
    def dadosSolda(self,cur):
        query_dash_solda = f"""
        WITH pecas_inspecionadas AS (
            SELECT 
                TO_CHAR(inspecao.data_finalizada, 'YYYY-Month') AS ano_mes,
                EXTRACT(MONTH FROM inspecao.data_finalizada) AS mes,
                EXTRACT(YEAR FROM inspecao.data_finalizada) AS ano,
                SUM(CASE WHEN inspecionadas.num_inspecao = 0 THEN inspecionadas.nao_conformidades ELSE 0 END) AS total_nao_conformidades,
                SUM(CASE 
                    WHEN inspecionadas.num_inspecao = 0 AND inspecionadas.setor = 'Solda' THEN inspecionadas.total_conformidades + inspecionadas.nao_conformidades
                    WHEN inspecionadas.num_inspecao = 0 AND (inspecionadas.setor = 'Solda - Cilindro' OR inspecionadas.setor = 'Solda - Tubo') THEN inspecao.qt_inspecionada
                    ELSE 0 
                END) AS num_inspecoes
            FROM pcp.pecas_inspecionadas AS inspecionadas
            LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id = inspecionadas.id_inspecao
            WHERE (inspecionadas.setor = 'Solda' OR inspecionadas.setor = 'Solda - Cilindro' OR inspecionadas.setor = 'Solda - Tubo')
            AND inspecao.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
            GROUP BY TO_CHAR(inspecao.data_finalizada, 'YYYY-Month'), EXTRACT(MONTH FROM inspecao.data_finalizada), EXTRACT(YEAR FROM inspecao.data_finalizada)
        ),
        pecas_inspecao AS (
            SELECT 
                EXTRACT(MONTH FROM data_finalizada) AS mes,
                EXTRACT(YEAR FROM data_finalizada) AS ano,
                SUM(qt_apontada) FILTER (WHERE setor = 'Solda' OR setor = 'Solda - Cilindro' OR setor = 'Solda - Tubo') AS num_pecas_produzidas
            FROM pcp.pecas_inspecao
            WHERE (setor = 'Solda' OR setor = 'Solda - Cilindro' OR setor = 'Solda - Tubo')
            AND data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
            GROUP BY EXTRACT(MONTH FROM data_finalizada), EXTRACT(YEAR FROM data_finalizada)
        )
        SELECT 
            COALESCE(pi2.ano_mes, TO_CHAR(TO_DATE(pi.ano || '-' || pi.mes, 'YYYY-MM'), 'YYYY-Month' || '❌')) AS ano_mes,
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
        cur.execute(query_dash_solda)
        return cur.fetchall()

    def dadosCausasSolda(self,cur):

        query_total_causas = f"""
                SELECT ano_mes,
                    conjunto,
                    causa,
                    SUM(total_quantidade) as total_quantidade
                FROM (
                    SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                    pi.codigo || '-' ||pi.peca as conjunto,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                    WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Solda'
                ) AS subquery
                GROUP BY ano_mes, conjunto, causa
                ORDER BY ano_mes desc;
            """
        cur.execute(query_total_causas)
        total_causas = cur.fetchall()

        # Para obter a soma de todos os total_quantidade
        query_soma_total = f"""
            SELECT SUM(total_quantidade) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Solda'
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        query_tubos = f"""
                    SELECT ano_mes,
                            conjunto,
                            causa,
                            origem,
                            SUM(total_quantidade) AS total_quantidade
                        FROM (
                            SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') AS ano_mes,
                                            pi.codigo || '-' || pi.peca AS conjunto,
                                            foto.id,
                                            foto.causa,
                                            inspecionadas.origem,
                                            foto.quantidade::INTEGER AS total_quantidade
                            FROM pcp.inspecao_foto foto
                            LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                            LEFT JOIN pcp.pecas_inspecionadas inspecionadas ON pi.id = inspecionadas.id_inspecao
                            WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                            AND foto.num_inspecao = 0
                            AND pi.setor = 'Solda - Tubo'
                        ) AS subquery
                        GROUP BY ano_mes, conjunto, causa, origem
                        ORDER BY ano_mes DESC;
                    """
        
        cur.execute(query_tubos)
        tubos = cur.fetchall()

        query_tubos_soma_total = f"""
            SELECT COALESCE(SUM(total_quantidade),0) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                foto.id,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                AND foto.num_inspecao = 0 AND pi.setor = 'Solda - Tubo'
            ) AS subquery;
        """

        cur.execute(query_tubos_soma_total)
        tubos_soma = cur.fetchone()

        query_cilindro = f"""
                    SELECT ano_mes,
                            conjunto,
                            causa,
                            origem,
                            SUM(total_quantidade) AS total_quantidade
                        FROM (
                            SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') AS ano_mes,
                                            pi.codigo || '-' || pi.peca AS conjunto,
                                            foto.id,
                                            foto.causa,
                                            inspecionadas.origem,
                                            foto.quantidade::INTEGER AS total_quantidade
                            FROM pcp.inspecao_foto foto
                            LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                            LEFT JOIN pcp.pecas_inspecionadas inspecionadas ON pi.id = inspecionadas.id_inspecao
                            WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                            AND foto.num_inspecao = 0
                            AND pi.setor = 'Solda - Cilindro'
                        ) AS subquery
                        GROUP BY ano_mes, conjunto, causa, origem
                        ORDER BY ano_mes DESC;"""
        
        cur.execute(query_cilindro)
        cilindro = cur.fetchall()

        query_cilindro_soma_total = f"""
            SELECT COALESCE(SUM(total_quantidade),0) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                foto.id,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                AND foto.num_inspecao = 0 AND pi.setor = 'Solda - Cilindro'
            ) AS subquery;
        """

        cur.execute(query_cilindro_soma_total)
        cilindro_soma = cur.fetchone()

        return total_causas, soma_total, tubos, tubos_soma, cilindro, cilindro_soma

    def fotosSolda(self,cur):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id
                WHERE pi2.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND caminho_foto NOTNULL AND pi2.setor = 'Solda' AND foto.causa NOTNULL
                ORDER BY ano_mes DESC
            """
        cur.execute(query_fotos)
        fotos = cur.fetchall()

        return fotos

    def dadosEstamparia(self,cur):
        
        query_dash_solda = f"""
            WITH pecas_inspecionadas AS (
                SELECT 
                    TO_CHAR(inspecao.data_finalizada, 'YYYY-Month') AS ano_mes,
                    EXTRACT(MONTH FROM inspecao.data_finalizada) AS mes,
                    EXTRACT(YEAR FROM inspecao.data_finalizada) AS ano,
                    SUM(CASE WHEN inspecionadas.num_inspecao = 0 THEN inspecionadas.nao_conformidades ELSE 0 END) AS total_nao_conformidades,
                    COUNT(inspecionadas.setor) FILTER (WHERE inspecionadas.setor = 'Estamparia') AS num_inspecoes
                FROM pcp.pecas_inspecionadas AS inspecionadas
                LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id = inspecionadas.id_inspecao
                WHERE inspecionadas.setor = 'Estamparia' AND inspecao.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                GROUP BY TO_CHAR(inspecao.data_finalizada, 'YYYY-Month'), EXTRACT(MONTH FROM inspecao.data_finalizada), EXTRACT(YEAR FROM inspecao.data_finalizada)
            ),
            pecas_inspecao AS (
                SELECT 
                    EXTRACT(MONTH FROM data_finalizada) AS mes,
                    EXTRACT(YEAR FROM data_finalizada) AS ano,
                    COUNT(data_finalizada) FILTER (WHERE setor = 'Estamparia') AS tipo_pecas_produzidas
                FROM pcp.pecas_inspecao
                WHERE setor = 'Estamparia' 
                AND data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                GROUP BY EXTRACT(MONTH FROM data_finalizada), EXTRACT(YEAR FROM data_finalizada)
            )
            SELECT 
                COALESCE(pi2.ano_mes, TO_CHAR(TO_DATE(pi.ano || '-' || pi.mes, 'YYYY-MM'), 'YYYY-Month'||'❌')) AS ano_mes,
                COALESCE(pi.tipo_pecas_produzidas, 0) AS tipo_pecas_produzidas,
                COALESCE(pi2.num_inspecoes, 0) AS num_inspecoes,
                COALESCE(pi2.total_nao_conformidades, 0) AS total_nao_conformidades,
                COALESCE(
                    ROUND(
                        100.0 * COALESCE(pi2.num_inspecoes, 0) / NULLIF(COALESCE(pi.tipo_pecas_produzidas, 0), 0), 2
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
        cur.execute(query_dash_solda)
        return cur.fetchall()

    def dadosCausasEstamparia(self,cur):

        query_total_causas = f"""
                SELECT ano_mes,
                    conjunto,
                    causa,
                    SUM(total_quantidade) as total_quantidade
                FROM (
                    SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                    pi.codigo || '-' ||pi.peca as conjunto,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                    WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Estamparia'
                ) AS subquery
                GROUP BY ano_mes, conjunto, causa
                ORDER BY ano_mes desc;
            """
        cur.execute(query_total_causas)
        total_causas = cur.fetchall()

        # Para obter a soma de todos os total_quantidade
        query_soma_total = f"""
            SELECT SUM(total_quantidade) as soma_total
            FROM (
                SELECT DISTINCT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id = foto.id
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Estamparia'
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        return total_causas, soma_total

    def fotosFichaEstamparia(self,cur):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id
                WHERE pi2.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND caminho_foto NOTNULL AND pi2.setor = 'Estamparia' AND foto.causa NOTNULL
                ORDER BY ano_mes DESC
            """
        cur.execute(query_fotos)
        fotos = cur.fetchall()

        query_fichas = f"""
                SELECT 
                    TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,
                    caminho_ficha,
                    CASE 
                        WHEN ficha.ficha_completa = true THEN 'Ficha 100%'
                        ELSE 'Ficha Produção'
                    END as tipo_ficha
                FROM 
                    pcp.ficha_inspecao ficha
                LEFT JOIN 
                    pcp.pecas_inspecao pi2 ON ficha.id = pi2.id
                WHERE 
                    pi2.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                    AND caminho_ficha IS NOT NULL 
                    AND pi2.setor = 'Estamparia'
                ORDER BY 
                    ano_mes DESC;
            """
        cur.execute(query_fichas)
        fichas = cur.fetchall()

        return fotos,fichas

    def fechar_conexao(self):
        self.cur.close()
        self.conn.close()
