import psycopg2
import psycopg2.extras
import pandas as pd

# Configurações do banco de dados
DB_HOST = "database-1.cdcogkfzajf0.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "15512332"

# Conexão com o banco de dados
try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)
    exit()

df_conjuntos_inspecionados = pd.read_csv('RQ CQ-012-000 (Controle de Inspeção da Solda) - LISTA DE PEÇAS _ CONJUNTOS.csv')

# Listas para armazenar os resultados das inserções
success = []
errors = []

# print(df_conjuntos_inspecionados)

# Inserção dos dados
for index, row in df_conjuntos_inspecionados.iterrows():

    try:
        codigo = str(row['codigo']).zfill(6)
        cur.execute("""
            INSERT INTO pcp.conjuntos_inspecionados (codigo, descricao)
            VALUES (%s, %s);
        """, (codigo, row['descricao']))
        conn.commit()
        success.append((codigo, row['descricao']))
    except Exception as e:
        conn.rollback()  # Reverte a transação em caso de erro
        errors.append((codigo, row['descricao'], str(e)))

# Impressão dos resultados
print("Inserções bem-sucedidas:")
for codigo, descricao in success:
    print(f"Código: {codigo}, Descrição: {descricao}")

print("\nErros durante a inserção:")
for codigo, descricao, error in errors:
    print(f"Código: {codigo}, Descrição: {descricao}, Erro: {error}")

# Fechar a conexão
cur.close()
conn.close()
