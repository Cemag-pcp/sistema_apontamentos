import psycopg2
import psycopg2.extras
import os
import boto3
from werkzeug.utils import secure_filename
from flask import request
from dotenv import load_dotenv

load_dotenv('.env')

AWS_BUCKET_NAME = "sistema-apontamento"
AWS_REGION = "sa-east-1"
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=AWS_REGION
)

class InspecaoEstanqueidade:

    def __init__(self, db_name, db_user, db_pass, db_host, upload_folder):
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.upload_folder = upload_folder
        self.conectar()  # Inicializa a conexão
    
    def upload_to_s3(self, file_path, filename,path):
        s3_key = f'{path}/{filename}'
        try:
            s3_client.upload_file(file_path, AWS_BUCKET_NAME, s3_key)
            file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            return file_url
        except Exception as e:
            print(f"Erro ao fazer upload para S3: {e}")
            return None
    
    def conectar(self):
        self.conn = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_pass, host=self.db_host)

    def verificar_conexao(self):
        if self.conn.closed:  # Verifica se a conexão está fechada
            self.conectar()

    def inserir_inspecao_estanqueidade(self, dados_inspecao_estanqueidade):

        try:
            self.verificar_conexao()
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                sql = """INSERT INTO pcp.inspecao_estanqueidade (codigo, descricao, inspecao, data_carga) 
                        VALUES (%s, %s, %s, %s)
                        RETURNING id;"""
                    
                values = (
                    dados_inspecao_estanqueidade['codigo'],
                    dados_inspecao_estanqueidade['descricao'], 
                    dados_inspecao_estanqueidade['tipo_inspecao'],
                    dados_inspecao_estanqueidade['data_carga']
                )

                cur.execute(sql, values)
                id = cur.fetchone()['id']
                
            self.conn.commit()
            print("inserir_inspecao_estanqueidade",id)

            return id
        
        except Exception as e:
            print(f"Unexpected error in inserir_inspecao_estanqueidade: {str(e)}")
            raise

    def inserir_execucoes_inspecao_estanqueidade(self, dados_execucoes_inspecao_estanqueidade, id_inspecao_estanqueidade):

        try:
            self.verificar_conexao()

            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                sql_get_max_execucao = """
                SELECT COALESCE(MAX(numero_execucao), -1) AS max_execucao
                FROM pcp.execucoes_inspecao_estanqueidade
                WHERE inspecao_id = %s;
                """
                cur.execute(sql_get_max_execucao, (id_inspecao_estanqueidade,))
                max_execucao = cur.fetchone()['max_execucao']

                numero_execucao = max_execucao + 1

                sql = """INSERT INTO pcp.execucoes_inspecao_estanqueidade 
                        (inspecao_id, numero_execucao, nao_conforme, nao_conforme_refugo, quantidade_inspecionada, inspetor, motivo, observacao, ficha) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;"""
                
                values = (
                    id_inspecao_estanqueidade,
                    numero_execucao,
                    dados_execucoes_inspecao_estanqueidade['nao_conforme_retrabalho'],
                    dados_execucoes_inspecao_estanqueidade['nao_conforme_refugo'],
                    dados_execucoes_inspecao_estanqueidade['quantidade_inspecionada'],
                    dados_execucoes_inspecao_estanqueidade['inspetor'],
                    dados_execucoes_inspecao_estanqueidade['motivo'],
                    dados_execucoes_inspecao_estanqueidade['observacao'],
                    dados_execucoes_inspecao_estanqueidade['ficha']
                )

                cur.execute(sql, values)
                id = cur.fetchone()['id']

            self.conn.commit()

            print("inserir_execucoes_inspecao_estanqueidade", id)

            return id

        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")
    
    def inserir_reinspecao_estanqueidade(self, ids_estanqueidade):

        try:
            self.verificar_conexao()

            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                sql = """INSERT INTO pcp.reinspecao_estanqueidade (inspecao_id) VALUES (%s)"""
                values = (
                    ids_estanqueidade['id_inspecao_estanqueidade'],
                )

                cur.execute(sql, values)

            self.conn.commit()

            print("inserir_reinspecao_estanqueidade")

        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")

    def inserir_reteste_estanqueidade(self, dados_reteste_estanqueidade,ids_estanqueidade):

        try:
            self.verificar_conexao()
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                for causa in dados_reteste_estanqueidade['causas']:
                    sql = """
                    INSERT INTO pcp.reteste_estanqueidade 
                    (causa, execucoes_inspecao_estanqueidade_id, foto_da_causa, quantidade) 
                    VALUES (%s, %s, %s, %s)
                    """
                    foto_da_causa = causa['arquivos'][0] if causa['arquivos'] else None
                    values = (
                        causa['causa'],  # Causa
                        ids_estanqueidade['id_execucoes_inspecao_estanqueidade'],  # ID relacionado
                        foto_da_causa,  # Arquivo (foto da causa)
                        causa['quantidade']  # Quantidade relacionada à causa
                    )

                    cur.execute(sql, values)

            self.conn.commit()
            print("inserir_reteste_estanqueidade")

        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")
    
    def excluir_reinspecao_estanqueidade(self,id_estanqueidade):

        try:
            self.verificar_conexao()
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                sql = """DELETE FROM pcp.reinspecao_estanqueidade
                        WHERE inspecao_id = %s"""
                cur.execute(sql,(id_estanqueidade['id_inspecao_estanqueidade'],))

            self.conn.commit()
        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")
        
    def inserir_execucoes_inspecao_estanqueidade_tanque(self,dados_estanqueidade_tanque,id_inspecao_estanqueidade_tanque):

        try:

            self.verificar_conexao()
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:

                sql_get_max_execucao = """
                SELECT COALESCE(MAX(numero_execucao), -1) AS max_execucao
                FROM pcp.execucoes_inspecao_estanqueidade_tanque
                WHERE inspecao_id = %s;
                """
                cur.execute(sql_get_max_execucao, (id_inspecao_estanqueidade_tanque,))
                max_execucao = cur.fetchone()['max_execucao']

                numero_execucao = max_execucao + 1
            
                query = """
                INSERT INTO pcp.execucoes_inspecao_estanqueidade_tanque 
                (inspecao_id, numero_execucao, inspetor)
                VALUES (%s, %s, %s)
                RETURNING id;
                """

                values = (
                    id_inspecao_estanqueidade_tanque,
                    numero_execucao,
                    dados_estanqueidade_tanque['inspetor'],
                )

                cur.execute(query, values)
                id = cur.fetchone()['id']

            self.conn.commit()
            print("inserir_execucoes_inspecao_estanqueidade_tanque")

            return id
        
        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")
        
    def inserir_detalhes_execucao_inspecao_estanqueidade_tanque(self,id_execucao_estanqueidade_tanque,primeiro_teste,segundo_teste=None):

        try:

            self.verificar_conexao()
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            
                query = """
                INSERT INTO pcp.detalhes_pressao_estanqueidade_tanque 
                (execucao_id, pressao_inicial, pressao_final, nao_conformidade, tipo_teste, hora_execucao)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                primeiro_teste['vazamento'] = True if primeiro_teste['vazamento'] == 'Sim' else False

                values_primeiro = (
                    id_execucao_estanqueidade_tanque,
                    primeiro_teste['pressao_inicial'],
                    primeiro_teste['pressao_final'],
                    primeiro_teste['vazamento'],
                    primeiro_teste['tipo_teste'],                
                    primeiro_teste['duracao'],                
                )

                cur.execute(query, values_primeiro)

                if segundo_teste != None:
                    segundo_teste['vazamento'] = True if segundo_teste['vazamento'] == 'Sim' else False

                    values_segundo = (
                        id_execucao_estanqueidade_tanque,
                        segundo_teste['pressao_inicial'],
                        segundo_teste['pressao_final'],
                        segundo_teste['vazamento'],
                        segundo_teste['tipo_teste'],                
                        segundo_teste['duracao'],                
                    )

                    cur.execute(query, values_segundo)

            self.conn.commit()
            print("inserir_detalhes_execucao_inspecao_estanqueidade_tanque")
        
        except Exception as e:
            raise RuntimeError(f"Erro na execução: {e}")
