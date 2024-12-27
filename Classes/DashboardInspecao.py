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
            LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id::VARCHAR = inspecionadas.id_inspecao
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
                    SELECT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                    pi.tipo,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
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
                SELECT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                    pi.tipo,
                    foto.causa,
                    foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Pintura'
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        query_total_liquida = f"""
            SELECT 
                TO_CHAR(pi.data_finalizada, 'YYYY-Month') AS ano_mes,
                foto.causa,
                SUM(CAST(foto.quantidade AS INTEGER)) AS total_quantidade
            FROM 
                pcp.pecas_inspecao pi
                LEFT JOIN 
                    pcp.inspecao_foto foto 
                    ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
            WHERE 
                pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                AND pi.tipo = 'PU' 
                AND foto.num_inspecao = 0 
                AND foto.causa IS NOT NULL
            GROUP BY 
                TO_CHAR(pi.data_finalizada, 'YYYY-Month'), 
                foto.causa
            ORDER BY 
                ano_mes, 
                foto.causa;
        """
        cur.execute(query_total_liquida)
        total_liquida = cur.fetchall()

        query_soma_total_liquida = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.inspecao_foto foto ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PU' AND foto.num_inspecao = 0 AND foto.causa NOTNULL
            ) AS subquery;
        """

        cur.execute(query_soma_total_liquida)
        soma_total_liquida = cur.fetchone()

        query_total_po = f"""
            SELECT 
                    TO_CHAR(pi.data_finalizada, 'YYYY-Month') AS ano_mes,
                    foto.causa,
                    SUM(CAST(foto.quantidade AS INTEGER)) AS total_quantidade
                FROM 
                    pcp.pecas_inspecao pi
            LEFT JOIN 
                pcp.inspecao_foto foto 
                ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
            WHERE 
                pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' 
                AND pi.tipo = 'PÓ' 
                AND foto.num_inspecao = 0 
                AND pi.setor = 'Pintura' 
                AND foto.causa IS NOT NULL
            GROUP BY 
                TO_CHAR(pi.data_finalizada, 'YYYY-Month'), 
                foto.causa
            ORDER BY 
                ano_mes, 
                foto.causa;
        """
        cur.execute(query_total_po)
        total_po = cur.fetchall()

        query_soma_total_po = f"""
            SELECT SUM(quantidade::INTEGER) as soma_total
            FROM (
                SELECT TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,foto.causa,foto.quantidade
                    FROM pcp.pecas_inspecao pi
                LEFT JOIN pcp.inspecao_foto foto ON pi.id::VARCHAR  = foto.id AND pi.setor = foto.setor
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND pi.tipo = 'PÓ' AND foto.num_inspecao = 0 AND pi.setor = 'Pintura' AND foto.causa NOTNULL
            ) AS subquery;
        """

        cur.execute(query_soma_total_po)
        soma_total_po = cur.fetchone()

        return total_causas,soma_total,total_liquida,soma_total_liquida,total_po,soma_total_po

    def fotosPintura(self,cur):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id::VARCHAR AND foto.setor = pi2.setor
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
                    SUM(CASE 
                        WHEN inspecionadas.num_inspecao = 0 THEN inspecionadas.nao_conformidades 
                        ELSE 0 
                    END) AS total_nao_conformidades,
                    SUM(CASE 
                        WHEN inspecionadas.num_inspecao = 0 AND inspecionadas.setor IN ('Solda', 'Solda - Cilindro', 'Solda - Tubo') THEN 
                            inspecionadas.total_conformidades + inspecionadas.nao_conformidades
                        ELSE 0 
                    END) AS num_inspecoes
                FROM pcp.pecas_inspecionadas AS inspecionadas
                LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id::VARCHAR = inspecionadas.id_inspecao
                WHERE inspecionadas.setor IN ('Solda', 'Solda - Cilindro', 'Solda - Tubo')
                AND inspecao.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                GROUP BY TO_CHAR(inspecao.data_finalizada, 'YYYY-Month'), EXTRACT(MONTH FROM inspecao.data_finalizada), EXTRACT(YEAR FROM inspecao.data_finalizada)
            ),
            pecas_inspecao AS (
                SELECT 
                    EXTRACT(MONTH FROM data_finalizada) AS mes,
                    EXTRACT(YEAR FROM data_finalizada) AS ano,
                    SUM(qt_apontada) FILTER (WHERE setor IN ('Solda', 'Solda - Cilindro', 'Solda - Tubo')) AS num_pecas_produzidas
                FROM pcp.pecas_inspecao
                WHERE setor IN ('Solda', 'Solda - Cilindro', 'Solda - Tubo')
                AND data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                GROUP BY EXTRACT(MONTH FROM data_finalizada), EXTRACT(YEAR FROM data_finalizada)
            ),
            estanqueidade_inspecionadas AS (
                SELECT 
                    TO_CHAR(ins.data, 'YYYY-Month') AS ano_mes,
                    EXTRACT(MONTH FROM ins.data) AS mes,
                    EXTRACT(YEAR FROM ins.data) AS ano,
                    COALESCE(SUM(exec.quantidade_inspecionada),0) AS quantidade_inspecionada,
                    SUM(exec.nao_conforme + exec.nao_conforme_refugo) AS total_nao_conformidades,
                    SUM(exec.quantidade_inspecionada) AS num_inspecoes
                FROM pcp.inspecao_estanqueidade ins
                LEFT JOIN pcp.execucoes_inspecao_estanqueidade exec ON ins.id = exec.inspecao_id
                WHERE ins.inspecao IN ('Tubos', 'Cilindros')
                AND ins.data BETWEEN '{self.data_inicial}' AND '{self.data_final}' and exec.numero_execucao = 0
                GROUP BY TO_CHAR(ins.data, 'YYYY-Month'), EXTRACT(MONTH FROM ins.data), EXTRACT(YEAR FROM ins.data)
            )
            SELECT 
                TO_CHAR(TO_DATE(COALESCE(pi.ano, ei.ano) || '-' || COALESCE(pi.mes, ei.mes), 'YYYY-MM'), 'YYYY-Month') AS ano_mes,
                COALESCE(SUM(pi.num_pecas_produzidas + ei.quantidade_inspecionada), SUM(pi.num_pecas_produzidas), 0) AS num_pecas_produzidas,
                COALESCE(SUM(pi2.num_inspecoes + ei.num_inspecoes), SUM(pi2.num_inspecoes), 0) AS num_inspecoes,
                COALESCE(SUM(pi2.total_nao_conformidades + ei.total_nao_conformidades), SUM(pi2.total_nao_conformidades), 0) AS total_nao_conformidades_totais,
                COALESCE(
                    ROUND(
                        100.0 * COALESCE(SUM(pi2.num_inspecoes + ei.num_inspecoes), SUM(pi2.num_inspecoes), 0) / COALESCE(SUM(pi.num_pecas_produzidas + ei.quantidade_inspecionada), SUM(pi.num_pecas_produzidas), 0), 2
                    ), 0
                ) AS porcentagem_inspecao,
                COALESCE(
                    ROUND(
                        100.0 * COALESCE(SUM(pi2.total_nao_conformidades + ei.total_nao_conformidades), SUM(pi2.total_nao_conformidades), 0) / COALESCE(SUM(pi2.num_inspecoes + ei.num_inspecoes), SUM(pi2.num_inspecoes), 0), 2
                    ), 0
                ) AS porcentagem_nao_conformidades
            FROM pecas_inspecionadas pi2
            FULL OUTER JOIN pecas_inspecao pi
                ON pi2.mes = pi.mes AND pi2.ano = pi.ano
            FULL OUTER JOIN estanqueidade_inspecionadas ei
                ON pi2.mes = ei.mes AND pi2.ano = ei.ano
            GROUP BY pi.ano, pi.mes, ei.ano, ei.mes
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
                                    pi.id,
                                    foto.causa,
                                    foto.quantidade::INTEGER as total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
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
                                pi.id,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
                WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND foto.num_inspecao = 0 AND pi.setor = 'Solda'
            ) AS subquery;
        """

        cur.execute(query_soma_total)
        soma_total = cur.fetchone()

        query_tubos = f"""
                        SELECT ano_mes,
                            causa,
                            codigo_descricao,
                            motivo,
                            quantidade as total_quantidade
                        FROM (
                            SELECT TO_CHAR(ins.data, 'YYYY-Month') AS ano_mes,
                                ins.codigo || ' - ' || ins.descricao AS codigo_descricao,
                                re.causa,
                                exec.motivo,
                                exec.quantidade_inspecionada,
                                re.quantidade
                            FROM pcp.inspecao_estanqueidade ins
                            LEFT JOIN pcp.execucoes_inspecao_estanqueidade exec ON ins.id = exec.inspecao_id
                            LEFT JOIN pcp.reteste_estanqueidade re ON exec.id = re.execucoes_inspecao_estanqueidade_id
                            WHERE ins.data BETWEEN '{self.data_inicial}' and '{self.data_final}'
                            and ins.inspecao IN ('Tubos')
                            and     exec.numero_execucao = 0
                            and exec.nao_conforme + exec.nao_conforme_refugo <> 0
                        ) AS subquery
                        GROUP BY ano_mes, codigo_descricao, motivo, causa, quantidade
                        ORDER BY ano_mes DESC;
                    """
        
        cur.execute(query_tubos)
        tubos = cur.fetchall()

        query_tubos_soma_total = f"""
            SELECT COALESCE(SUM(total_quantidade), 0) AS soma_total
            FROM (
                SELECT TO_CHAR(ins.data, 'YYYY-Month') AS ano_mes,
                    ins.codigo || ' - ' || ins.descricao AS codigo_descricao,
                    exec.nao_conforme + exec.nao_conforme_refugo AS total_quantidade
                FROM pcp.inspecao_estanqueidade ins
                LEFT JOIN pcp.execucoes_inspecao_estanqueidade exec ON ins.id = exec.inspecao_id
                WHERE ins.data BETWEEN '{self.data_inicial}' and '{self.data_final}' 
                AND ins.inspecao IN ('Tubos')
                AND exec.numero_execucao = 0
                AND exec.nao_conforme + exec.nao_conforme_refugo <> 0
            ) AS subquery;
        """

        cur.execute(query_tubos_soma_total)
        tubos_soma = cur.fetchone()

        query_cilindro = f"""
                    SELECT ano_mes,
                            causa,
                            codigo_descricao,
                            motivo,
                            quantidade as total_quantidade
                        FROM (
                            SELECT TO_CHAR(ins.data, 'YYYY-Month') AS ano_mes,
                                ins.codigo || ' - ' || ins.descricao AS codigo_descricao,
                                re.causa,
                                exec.motivo,
                                exec.quantidade_inspecionada,
                                re.quantidade
                            FROM pcp.inspecao_estanqueidade ins
                            LEFT JOIN pcp.execucoes_inspecao_estanqueidade exec ON ins.id = exec.inspecao_id
                            LEFT JOIN pcp.reteste_estanqueidade re ON exec.id = re.execucoes_inspecao_estanqueidade_id
                            WHERE ins.data BETWEEN '{self.data_inicial}' and '{self.data_final}'
                            and ins.inspecao IN ('Cilindros')
                            and     exec.numero_execucao = 0
                            and exec.nao_conforme + exec.nao_conforme_refugo <> 0
                        ) AS subquery
                        GROUP BY ano_mes, codigo_descricao, motivo, causa, quantidade
                        ORDER BY ano_mes DESC;"""
        
        cur.execute(query_cilindro)
        cilindro = cur.fetchall()

        query_cilindro_soma_total = f"""
            SELECT COALESCE(SUM(total_quantidade), 0) AS soma_total
            FROM (
                SELECT TO_CHAR(ins.data, 'YYYY-Month') AS ano_mes,
                    ins.codigo || ' - ' || ins.descricao AS codigo_descricao,
                    exec.nao_conforme + exec.nao_conforme_refugo AS total_quantidade
                FROM pcp.inspecao_estanqueidade ins
                LEFT JOIN pcp.execucoes_inspecao_estanqueidade exec ON ins.id = exec.inspecao_id
                WHERE ins.data BETWEEN '{self.data_inicial}' and '{self.data_final}' 
                AND ins.inspecao IN ('Cilindros')
                AND exec.numero_execucao = 0
                AND exec.nao_conforme + exec.nao_conforme_refugo <> 0
            ) AS subquery;
        """

        cur.execute(query_cilindro_soma_total)
        cilindro_soma = cur.fetchone()

        return total_causas, soma_total, tubos, tubos_soma, cilindro, cilindro_soma

    def fotosSolda(self,cur):

        query_fotos = f"""
                SELECT TO_CHAR(pi2.data_finalizada, 'YYYY-Month') as ano_mes,caminho_foto,foto.causa
                    FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id AND pi2.setor = foto.setor
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
                LEFT JOIN pcp.pecas_inspecao AS inspecao ON inspecao.id::VARCHAR = inspecionadas.id_inspecao
                WHERE inspecionadas.setor = 'Estamparia' AND inspecao.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}' AND inspecionadas.num_inspecao = 0
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
                    SUM(total_quantidade) AS total_quantidade
                FROM (
                    SELECT DISTINCT ON (foto.id, foto.causa)
                        foto.id,
                        TO_CHAR(pi.data_finalizada, 'YYYY-Month') AS ano_mes,
                        pi.codigo || '-' || pi.peca AS conjunto,
                        foto.causa,
                        foto.quantidade::INTEGER AS total_quantidade
                    FROM pcp.inspecao_foto foto
                    LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
                    WHERE pi.data_finalizada BETWEEN '{self.data_inicial}' AND '{self.data_final}'
                    AND foto.num_inspecao = (
                        SELECT MAX(f2.num_inspecao)
                        FROM pcp.inspecao_foto f2
                        WHERE f2.id = foto.id 
                    )
                    AND pi.setor = 'Estamparia'
                ) AS subquery
                GROUP BY ano_mes, conjunto, causa
                ORDER BY ano_mes DESC;
            """
        cur.execute(query_total_causas)
        total_causas = cur.fetchall()

        # Para obter a soma de todos os total_quantidade
        query_soma_total = f"""
            SELECT SUM(total_quantidade) as soma_total
            FROM (
                SELECT DISTINCT ON (foto.id, foto.causa) TO_CHAR(pi.data_finalizada, 'YYYY-Month') as ano_mes,
                                foto.causa,
                                foto.quantidade::INTEGER as total_quantidade
                FROM pcp.inspecao_foto foto
                LEFT JOIN pcp.pecas_inspecao pi ON pi.id::VARCHAR = foto.id AND pi.setor = foto.setor
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
                LEFT JOIN pcp.pecas_inspecao pi2 ON foto.id = pi2.id::VARCHAR AND pi2.setor = foto.setor
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
                    pcp.pecas_inspecao pi2 ON ficha.id = pi2.id::VARCHAR
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
