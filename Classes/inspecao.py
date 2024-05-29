import psycopg2
import psycopg2.extras
import os
from werkzeug.utils import secure_filename
from flask import request

class Inspecao:

    def __init__(self, db_name, db_user, db_pass, db_host, upload_folder):

        self.conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.upload_folder = upload_folder

    def inserir_reinspecao(self, id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico='', categoria='', outraCausaSolda='', origemInspecaoSolda='', observacaoSolda=''):
        
        id_inspecao = str(id_inspecao)

        if setor == 'Pintura':
            
            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true' WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_reinspecao (id, nao_conformidades, causa_reinspecao, inspetor, setor) VALUES (%s, %s, %s, %s, %s)"""
            values = (id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor)

        elif setor == 'Solda':

            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true' WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_reinspecao (id, nao_conformidades, causa_reinspecao, inspetor, setor, conjunto, categoria, outra_causa, origem, observacao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (id_inspecao, n_nao_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico, categoria, outraCausaSolda, origemInspecaoSolda, observacaoSolda)

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

        elif setor == 'Solda':

            delete_table_inspecao = f"""UPDATE pcp.pecas_inspecao SET excluidas = 'true', qt_inspecionada = {qtd_inspecionada} WHERE id = '{id_inspecao}'"""
            self.cur.execute(delete_table_inspecao)

            sql = """INSERT INTO pcp.pecas_inspecionadas (id_inspecao, total_conformidades, nao_conformidades, inspetor, setor, num_inspecao, conjunto, origem, observacao) VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s)"""
            values = (id_inspecao, n_conformidades, n_nao_conformidades, inspetor, setor, conjunto_especifico, origemInspecaoSolda, observacaoSolda)

        self.cur.execute(sql, values)
        self.conn.commit()

        print("inserir_inspecionados")

    def alterar_reinspecao(self, id_inspecao, n_nao_conformidades, qtd_produzida, n_conformidades, causa_reinspecao, inspetor, setor, conjunto_especifico='', categoria='', outraCausaSolda='', origemInspecaoSolda='', observacaoSolda='', operadores=''):
        
        id_inspecao = str(id_inspecao)
        if setor == 'Pintura':
            if n_conformidades == "0":
                
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

            elif n_conformidades > "0" and n_conformidades < qtd_produzida:

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
                
        elif setor == 'Solda':
            if n_conformidades == "0":

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

            elif n_conformidades > "0" and n_conformidades < qtd_produzida:

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

        self.conn.commit()
        print("alterar_reinspecao")

    def dados_inspecionar_reinspecionar(self):

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

    def processar_fotos_inspecao(self, id_inspecao, n_nao_conformidades, list_causas, num_inspecao= ''):


        for i in range(1, n_nao_conformidades + 1):
            file_key = f'foto_inspecao_{i}[]'
            fotos = request.files.getlist(file_key)
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

        self.conn.commit()

    def fechar_conexao(self):
        self.cur.close()
        self.conn.close()
