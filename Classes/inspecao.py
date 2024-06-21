import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import request

class Inspecao:

    def __init__(self, db_name, db_user, db_pass, db_host, upload_folder,upload_folder_token):

        self.conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.upload_folder = upload_folder
        self.upload_folder_token = upload_folder_token

    def inserir_reinspecao(self, id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico='', categoria='', outraCausaSolda='', origemInspecaoSolda='', observacaoSolda=''):
        
        id_inspecao = str(id_inspecao)

        if setor == 'Pintura':
            
            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true' WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_reinspecao (id, nao_conformidades, causa_reinspecao, inspetor, setor) VALUES (%s, %s, %s, %s, %s)"""
            values = (id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor)

        elif setor == 'Solda' or setor == 'Estamparia':

            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true' WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_reinspecao (id, nao_conformidades, causa_reinspecao, inspetor, setor, conjunto, categoria, outra_causa, origem, observacao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico, categoria, outraCausaSolda, origemInspecaoSolda, observacaoSolda)

        elif setor == 'Solda - Cilindro' or setor == 'Solda - Tubo':
            sql = """INSERT INTO pcp.pecas_reinspecao (id, nao_conformidades, causa_reinspecao, inspetor, setor, conjunto, categoria, outra_causa, origem, observacao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico,categoria, outraCausaSolda, origemInspecaoSolda, observacaoSolda)

        self.cur.execute(sql, values)
        self.conn.commit()

        print("inserir_reinspecao")

    def inserir_inspecionados(self, id_inspecao, n_conformidades,n_nao_conformidades, inspetor, setor, conjunto_especifico='', origemInspecaoSolda='', observacaoSolda='', qtd_inspecionada = ''):

        id_inspecao = str(id_inspecao)
        if setor == 'Pintura':

            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true' WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) VALUES (%s, %s, %s, %s, %s, 0)"""
            values = (id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor)

        elif setor == 'Solda' or setor == 'Estamparia':

            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true', qt_inspecionada = {qtd_inspecionada} WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao) VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s)"""
            values = (id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacaoSolda)

        elif setor == 'Solda - Cilindro' or setor == 'Solda - Tubo':

            motivo,observacao = observacaoSolda.split(" - ")

            sql = """INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, operadores, observacao, origem) VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s)"""
            values = (id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacao, motivo)

        self.cur.execute(sql, values)
        self.conn.commit()

        print("inserir_inspecionados")

    def alterar_reinspecao(self, id_inspecao, n_nao_conformidades, qtd_produzida, n_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico='', categoria='', outraCausaSolda='', origemInspecaoSolda='', observacaoSolda='', operadores=''):
        
        id_inspecao = str(id_inspecao)

        n_conformidades = int(n_conformidades)

        qtd_produzida = int(qtd_produzida)

        if setor == 'Pintura':

            if n_conformidades == 0:
                
                sql_update = """UPDATE pcp.pecas_reinspecao SET causa_reinspecao = %s, inspetor = %s WHERE id = %s """
                values_update = (causa_reinspecao, inspetor, id_inspecao)

                self.cur.execute(sql_update, values_update)
                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;"""
                
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor)
                self.cur.execute(sql_insert, values)

            elif n_conformidades > 0 and n_conformidades < qtd_produzida:

                sql_update = """UPDATE pcp.pecas_reinspecao SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s WHERE id = %s """
                values = (n_nao_conformidades, causa_reinspecao, inspetor, id_inspecao)

                self.cur.execute(sql_update, values)
                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;"""
                
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor)
                self.cur.execute(sql_insert, values)

            elif n_conformidades == qtd_produzida:

                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s,(SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s));
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao) 
                                    VALUES (%s, %s, %s, %s, %s, 0);
                                END IF;
                            END $$;"""
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor)
                self.cur.execute(sql_insert, values)

                delete_table_inspecao = f"""UPDATE pcp.pecas_reinspecao SET excluidas = 'true' WHERE id ='{id_inspecao}'"""
                self.cur.execute(delete_table_inspecao)
                
        elif setor == 'Solda' or setor == 'Estamparia':

            if n_conformidades == 0:

                sql_update = """UPDATE pcp.pecas_reinspecao SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s, conjunto = %s, categoria = %s, outra_causa = %s, origem = %s, observacao = %s WHERE id = %s """
                values_update = (n_nao_conformidades, causa_reinspecao, inspetor, conjunto_especifico, categoria, outraCausaSolda, origemInspecaoSolda, observacaoSolda, id_inspecao)

                self.cur.execute(sql_update, values_update)
                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao,operadores) 
                                    VALUES (%s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s), %s, %s, %s, %s);
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao, operadores) 
                                    VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s);
                                END IF;
                            END $$;"""
                
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores)
                self.cur.execute(sql_insert, values)

                print("Entrou")

            elif n_conformidades > 0 and n_conformidades < qtd_produzida:

                sql_update = """UPDATE pcp.pecas_reinspecao SET nao_conformidades = %s, causa_reinspecao = %s, inspetor = %s, conjunto = %s, categoria = %s, outra_causa = %s, origem = %s, observacao = %s WHERE id = %s """
                values_update = (n_nao_conformidades, causa_reinspecao, inspetor, conjunto_especifico, categoria, outraCausaSolda, origemInspecaoSolda, observacaoSolda, id_inspecao)

                self.cur.execute(sql_update, values_update)
                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao, operadores) 
                                    VALUES (%s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s), %s, %s, %s, %s);
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao, operadores) 
                                    VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s);
                                END IF;
                            END $$;"""
                
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores)
                self.cur.execute(sql_insert, values)

                print("Entrou")

            elif n_conformidades == qtd_produzida:

                sql_insert = """DO $$ BEGIN
                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao, operadores) 
                                    VALUES (%s, %s, %s, %s, %s, (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s), %s, %s, %s, %s);
                                ELSE
                                    INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao, operadores) 
                                    VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s);
                                END IF;
                            END $$;"""
                
                values = (id_inspecao, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, id_inspecao, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores, id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacaoSolda, operadores)
                self.cur.execute(sql_insert, values)

                delete_table_inspecao = f"""UPDATE pcp.pecas_reinspecao SET excluidas = 'true' WHERE id ='{id_inspecao}'"""
                self.cur.execute(delete_table_inspecao)

                print("Entrou")
    
        self.conn.commit()
        print("alterar_reinspecao")

    def dados_inspecionar_reinspecionar_pintura(self):

        inspecao = """SELECT * FROM pcp.pecas_inspecao WHERE excluidas = 'false' AND setor = 'Pintura' ORDER BY id desc"""
        self.cur.execute(inspecao)

        data_inspecao = self.cur.fetchall()

        inspecionados = """SELECT i.*, op.peca, op.cor, op.tipo
                           FROM pcp.pecas_inspecionadas as i
                           LEFT JOIN pcp.ordens_pintura as op ON i.id_inspecao = op.id::varchar
                           WHERE i.setor = 'Pintura' and i.num_inspecao = 0"""
        
        self.cur.execute(inspecionados)
        data_inspecionadas = self.cur.fetchall()

        reinspecao = """SELECT r.*, op.peca, op.cor, op.tipo
                        FROM pcp.pecas_reinspecao as r
                        LEFT JOIN pcp.ordens_pintura as op ON r.id = op.id::varchar
                        WHERE r.setor = 'Pintura' AND r.excluidas IS NOT true"""
        
        self.cur.execute(reinspecao)
        data_reinspecao = self.cur.fetchall()

        return data_inspecao, data_reinspecao, data_inspecionadas
    
    def dados_inspecionar_reinspecionar_estamparia(self):

        inspecao = """SELECT * FROM pcp.pecas_inspecao WHERE excluidas = 'false' AND setor = 'Estamparia' ORDER BY id desc"""
        self.cur.execute(inspecao)

        data_inspecao = self.cur.fetchall()

        inspecionados = """SELECT *
                           FROM pcp.pecas_inspecionadas
                           WHERE setor = 'Estamparia' and num_inspecao = 0"""
        
        self.cur.execute(inspecionados)
        data_inspecionadas = self.cur.fetchall()

        reinspecao = """SELECT *
                        FROM pcp.pecas_reinspecao
                        WHERE setor = 'Estamparia' AND excluidas IS NOT true"""
        
        self.cur.execute(reinspecao)
        data_reinspecao = self.cur.fetchall()

        return data_inspecao, data_reinspecao, data_inspecionadas

    def dados_reteste_tubos_cilindros(self):

        inspecao = """SELECT * FROM pcp.pecas_reinspecao WHERE excluidas = 'false' AND (setor = 'Solda - Cilindro' or setor = 'Solda - Tubo') ORDER BY id desc"""
        self.cur.execute(inspecao)

        dado_reteste_cilindros_tubos = self.cur.fetchall()

        inspecao_dados = """SELECT 
                        id_inspecao,
                        data_inspecao,
                        conjunto,
                        inspetor,
                        pi2.qt_inspecionada
                    FROM pcp.pecas_inspecionadas pi
                    LEFT JOIN pcp.pecas_inspecao pi2 ON pi.id_inspecao = pi2.id
                    WHERE (pi.setor = 'Solda - Cilindro' OR pi.setor = 'Solda - Tubo') AND num_inspecao = 0
                    ORDER BY id_inspecao DESC;
                """
        self.cur.execute(inspecao_dados)

        dado_inspecao_cilindros_tubos = self.cur.fetchall()

        return dado_reteste_cilindros_tubos, dado_inspecao_cilindros_tubos

    def executando_reteste(self,id,reteste_status1,reteste_status2,reteste_status3):

        query = """INSERT INTO pcp.inspecao_reteste (id,reteste_1,reteste_2,reteste_3) VALUES (%s,%s,%s,%s)"""
        values = (id, reteste_status1, reteste_status2, reteste_status3)
        self.cur.execute(query, values)

         # Atualiza a tabela de reinspecao
        sql = """UPDATE pcp.pecas_reinspecao SET excluidas = 'true' WHERE id=%s"""
        self.cur.execute(sql, (id,))

        query_select = """SELECT * FROM pcp.pecas_inspecionadas WHERE id_inspecao=%s"""
        self.cur.execute(query_select, (id,))
        row = self.cur.fetchone()

        if row:
            # Insere uma nova linha com os mesmos dados, mas com num_inspecao definido para 1
            query_insert = """
            INSERT INTO pcp.pecas_inspecionadas (
                id_inspecao, inspetor, setor,
                num_inspecao, conjunto, operadores, observacao, origem
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_insert = (
                row['id_inspecao'],row['inspetor'], row['setor'],
                1, row['conjunto'], row['operadores'], row['observacao'],row['origem']
            )
            self.cur.execute(query_insert, values_insert)

        self.conn.commit()

    def processar_fotos_inspecao(self, id_inspecao, n_nao_conformidades, list_causas, num_inspecao= '',tipos_causas_estamparia='',list_quantidade=[]):

        if tipos_causas_estamparia == '':
            for i in range(1, n_nao_conformidades + 1):
                file_key = f'foto_inspecao_{i}[]'
                fotos = request.files.getlist(file_key)
                print(fotos)
                if fotos == []:
                    fotos.append('')
                for foto in fotos:
                    if foto != '':
                        filename = secure_filename(foto.filename)
                        file_path = os.path.join(self.upload_folder, filename)
                        arquivos = file_path
                        arquivos = arquivos.replace('\\', '/')
                        foto.save(file_path)
                    else:
                        arquivos = None

                    if num_inspecao == '':

                        query_fotos = """DO $$
                                            BEGIN
                                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                                    INSERT INTO pcp.inspecao_foto
                                                        (id, caminho_foto, causa, num_inspecao) 
                                                    VALUES 
                                                        (%s, %s, %s,
                                                            (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                                        );
                                                ELSE
                                                    INSERT INTO pcp.inspecao_foto
                                                        (id, caminho_foto, causa, num_inspecao) 
                                                    VALUES 
                                                        (%s, %s, %s, 0);
                                                END IF;
                                            END $$;
                                        """
                        values_fotos = (
                                id_inspecao,
                                id_inspecao,
                                arquivos,
                                list_causas[i - 1],
                                id_inspecao,
                                id_inspecao,
                                arquivos,
                                list_causas[i - 1]
                            )
                    else:
                        query_fotos = """INSERT INTO pcp.inspecao_foto (id, caminho_foto, causa, num_inspecao) VALUES (%s, %s, %s, %s); """
                        values_fotos = (
                                id_inspecao,
                                arquivos,
                                list_causas[i - 1],
                                num_inspecao
                            )

                    self.cur.execute(query_fotos, values_fotos)
        else:
            for i in range(tipos_causas_estamparia):
                file_key = f'foto_inspecao_{i}[]'
                fotos = request.files.getlist(file_key)
                print(fotos)
                if fotos == []:
                    fotos.append('')
                for foto in fotos:
                    if foto != '':
                        filename = secure_filename(foto.filename)
                        file_path = os.path.join(self.upload_folder, filename)
                        arquivos = file_path + ";"
                        arquivos = arquivos.replace('\\', '/')
                        foto.save(file_path)
                    else:
                        arquivos = None

                    if num_inspecao == '':

                        query_fotos = """DO $$
                                            BEGIN
                                                IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                                    INSERT INTO pcp.inspecao_foto
                                                        (id, caminho_foto, causa, quantidade,num_inspecao) 
                                                    VALUES 
                                                        (%s, %s, %s, %s,
                                                            (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                                        );
                                                ELSE
                                                    INSERT INTO pcp.inspecao_foto
                                                        (id, caminho_foto, causa, quantidade, num_inspecao) 
                                                    VALUES 
                                                        (%s, %s, %s, %s, 0);
                                                END IF;
                                            END $$;
                                        """
                        values_fotos = (
                                id_inspecao,
                                id_inspecao,
                                arquivos,
                                list_causas[i],
                                list_quantidade[i],
                                id_inspecao,
                                id_inspecao,
                                arquivos,
                                list_causas[i],
                                list_quantidade[i]
                            )
                    else:

                        print("Entrou no Else")
                        query_fotos = """INSERT INTO pcp.inspecao_foto (id, caminho_foto, causa, num_inspecao, quantidade) VALUES (%s, %s, %s, %s, %s); """
                        values_fotos = (
                                id_inspecao,
                                arquivos,
                                list_causas[i],
                                num_inspecao,
                                list_quantidade[i]
                            )

                    self.cur.execute(query_fotos, values_fotos)

        self.conn.commit()

    def processar_ficha_inspecao(self,id_inspecao,ficha_completa=''):

        if ficha_completa != '':
            filename = secure_filename(ficha_completa.filename)
            file_path = os.path.join(self.upload_folder_token, filename)
            arquivos = file_path + ";"
            arquivos = arquivos.replace('\\', '/')
            ficha_completa.save(file_path)

            query_ficha_completa = """DO $$
                        BEGIN
                            IF EXISTS (SELECT 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s) THEN
                                INSERT INTO pcp.ficha_inspecao
                                    (id, caminho_ficha, ficha_completa, num_inspecao) 
                                VALUES 
                                    (%s, %s, 'true',
                                        (SELECT COALESCE(MAX(num_inspecao), 0) + 1 FROM pcp.pecas_inspecionadas WHERE id_inspecao = %s)
                                    );
                            ELSE
                                INSERT INTO pcp.ficha_inspecao
                                    (id, caminho_ficha, ficha_completa, num_inspecao) 
                                VALUES 
                                    (%s, %s, 'true', 0);
                            END IF;
                        END $$;"""

            values_ficha_completa = (
                    id_inspecao,
                    id_inspecao,
                    arquivos,
                    id_inspecao,
                    id_inspecao,
                    arquivos
                )
            
            self.cur.execute(query_ficha_completa, values_ficha_completa)
        
        self.conn.commit()
        print("processar_ficha_inspecao")

    def fechar_conexao(self):
        self.cur.close()
        self.conn.close()
