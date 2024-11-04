import psycopg2
import psycopg2.extras

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

# Dados das peças a serem inseridos
pecas = [
    ("026885", "PISO DA PLATAFORMA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027159", "CHAP LAT DUTO DE REFUGO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027160", "CHAPEAM FRONTAL DUTO DE REFUGO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027161", "CHAPEAM TRAS DUTO DE REFUGO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027277", "APOIO DESLIZANTE - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027283", "APOIO INCLINADO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027404", "ORELHA BRAÇO DE TORÇÃO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027276", "LONGARINA REFUGO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027509A", "LONGARINA INFERIOR- SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("027509B", "LONGARINA INFERIOR- SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("027510A", "LONGARINA SUPERIOR- SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("027510B", "LONGARINA SUPERIOR- SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("027617", "ORELHA SAÍDA BALANÇA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027740A", "CALHA MAIOR- SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("027740B", "CALHA MAIOR- SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("027671", "BASE PLATAF DE REFUGO - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027738", "FECHAM LAT CONT- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027660", "TRAVA FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028174", "FECHA LAT.- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027843", "BASE DO SUPORTE DE SAÍDA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027849", "GUIA DO CONJ DE SAÍDA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028046A", "PROTEÇÃO DO TRILHO CENTRAL- SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("028046B", "PROTEÇÃO DO TRILHO CENTRAL- SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("028231", "REF DA COLUNA TRASEIRA - SUP ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028128A", "LONGARINA CENTRAL- SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("028128B", "LONGARINA CENTRAL- SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("028234", "COMPL BANDEJA - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028235", "COMPL BANDEJA FURADO - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028236", "FECHAMENTO BANDEJA - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027106", "BASE DO MANCAL TRAS - ELEV MAIOR /SUP SUP ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028115", "CORPO DO CHASSI - ELEVADOR MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028242", "REF COLUNA SUP - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028246", "COMPLEMREFCOLUNA SUP - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028221", "ORELHA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028220", "CANTDE FIXAÇÃO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028238", "ORELHA MAIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028223", "TRAVESSA INTERNA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028227", "LONGARINA LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028219", "TRAVESSA DIANT./TRAS.- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028218", "LONGARINA CENTRAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030726", "TRAVESSA INTERMEDIÁRIA - BAIA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030726", "TRAVESSA INTERMEDIÁRIA - BAIA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029830", "CALHA MÓD MOTOR RETROFIT - MÓD MOTOR RETROFIT - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028133", "CANTONEIRA DE REFORÇO MÃO FRANCESA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027659", "ORELHA SUPERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028187", "U DE APOIO SEM FUROS - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027892", "CANTONEIRA DO MOTOREDUTOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029947", "'U' DE APOIO RETROFIT - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027410", "LONGARINA SUPERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029677", "CHAPA DE ENTRADA DA CORRENTE - MÓDULO MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027411", "LONGARINA INFERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028156", "LONGARINA CENTRAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030647", "PERFIL DE APOIO DA ESTEIRA - ESTRUTURA ESTEIRA DAS BAIAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027560", "CANTONEIRA DO MANCAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027845", "ORELHA DO TUBO DE LIGAÇÃO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027795", "CALÇO BALANÇA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028351", "COLUNA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028340", "DISTANCIADOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028366", "CHAPA VIRADA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028365", "CANTONEIRA FURADA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028080", "PERFIL GUIA DA BANDEJA MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028080", "PERFIL GUIA DA BANDEJA MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028050", "PERFIL GUIA DA BANDEJA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028221", "ORELHA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028713", "CALHA SINGULADOR - SINGULADOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028346", "BASE VIRADA COM RASGO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028368", "CHAPA VIRADA SUPERIOR (ESBARRO)- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028348", "BASE MANCAL MOTOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028350", "ORELHA MANCAL MOTOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028335", "LONGARINA RECORTADA LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028475", "BANDEJA SINGULADOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028423", "BASE MANCAL MOTOR - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028421", "LONGARINA - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028442", "DISTANCIADOR - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028353", "SUPORTE CALHA DIANTEIRA - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028354", "CALHA - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027671", "BASE PLATAF DE REFUGO - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028415", "BANDEJA - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028418", "CALHA - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028703", "CHAPA LAT FECHAM ANTERIOR - ELEVADOR MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028705", "CHAPA TRANSV FECHAM ANTERIOR - ELEVADOR MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028438", "CHAPA SUP MOTOR - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027106", "BASE DO MANCAL TRAS - ELEV MAIOR /SUP SUP ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027107", "BASE DO MANCAL DIANT- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027199", "TRILHO CURVADO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027176", "FECHAM LATERAL MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027212", "FECHAM LAT INTERMEDIARIO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027099", "CORPO MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027100", "CORPO MAIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027105", "FECHAM MAIOR INF- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027103", "COMPLEM LATERAL FECHAM MAIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027101", "FECHAM MENOR INFERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027102", "COMPLEM LAT DO FECHAM MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027361", "SUPORTE MANCAIS DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027243", "COLUNA DA LAVADORA - LAV / SUP SUP ELEV MENOR / SUP ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027222", "APOIO CENTRAL DA BANDEJA - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027245", "DISTANCIADOR LATERAL - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027251", "COLUNA SUPORTE MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027221", "APOIO LATERAL DA BANDEJA- LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027362", "CHAPA DOBRADA REFORÇO - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("026894", "DEGRAU DA ESCADA - PLATAFORMA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028672", "CANTONEIRA DE LIGAÇÃO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029601A", "TAMPA DA CALHA - MÓDULO CENTRAL - SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("029601B", "TAMPA DA CALHA - MÓDULO CENTRAL - SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("029648", "FIXAÇÃO TABLET - BAIA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029707", "TRANSVERSINA BASE DO QUADRO ELÉTRICO - BASE DO QUADRO ELÉTRICO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029706", "LONGARINA BASE DO QUADRO ELÉTRICO - BASE DO QUADRO ELÉTRICO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029705", "COLUNA BASE DO QUADRO ELÉTRICO - BASE DO QUADRO ELÉTRICO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027753A", "COMPLEMLISO COLUNA LAVADORA - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027753", "COMPLEMLISO COLUNA LAVADORA - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027985", "CHAPA SUPORTE REGULAGEM MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027906", "BASE SUPORTE DO MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029927", "CHAPA APOIO DA ESPONJA - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029927", "CHAPA APOIO DA ESPONJA - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028133", "CANTONEIRA DE REFORÇO MÃO FRANCESA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027892", "CANTONEIRA DO MOTOREDUTOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028187", "U DE APOIO SEM FUROS - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029947", "'U' DE APOIO RETROFIT - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027773", "ENCAIXE DA TRAVA DO FECHAMENTO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028197", "FECHAMENTO DA ESTEIRA MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027660", "TRAVA FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028196", "FECHAMENTO DA ESTEIRA MAIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027660", "TRAVA FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027417", "FECHAM DA ESTEIRA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027417", "FECHAM DA ESTEIRA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028691", "CALHA MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028133", "CANTONEIRA DE REFORÇO MÃO FRANCESA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028187", "U DE APOIO SEM FUROS - SIZER - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027559", "CHAPA SUP LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027687", "CHAPA DO ESTICADOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027565A", "LONGARINA SUPERIOR - CONJ SOLDADO MÓD MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027596", "PERFIL U TRANS MAIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030486", "PASSA CABO INTERMEDIÁRIO - CONJ SOLDADO MÓD MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027562", "LONGARINA INFERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027565", "LONGARINA SUPERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028131", "LONGARINA CENTRAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027773", "ENCAIXE DA TRAVA DO FECHAMENTO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027695", "SUPORTE DA GUIA CENTRAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027598", "SUPORTE PERFIL C- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027739", "CALHA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027689", "APOIO CONTADOR DE ROT- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027660", "TRAVA FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027923", "FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027660", "TRAVA FECHAMENTO LATERAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028137", "FECHAMENTO LATERAL MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030306A", "LONGARINA SUPERIOR ESQUERDA - CONJUNTO SOLDADO MÓDULO CENTRAL - SELECIONADORA DE FRUTAS (A)", "Estamparia", "ativo"),
    ("030306B", "LONGARINA SUPERIOR ESQUERDA - CONJUNTO SOLDADO MÓDULO CENTRAL - SELECIONADORA DE FRUTAS (B)", "Estamparia", "ativo"),
    ("028693", "CALHA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029733", "FECHAMENTO CALHA 200 PARTE 2 - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029732", "FECHAMENTO CALHA 200 PARTE 1 - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028221", "ORELHA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030736", "CANTONEIRA DO ESTICADOR MÓD MOTOR - ESTICADOR SUPERIOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030742", "CANTONEIRA DE FIXAÇÃO - APOIO DO QUADRO ELÉTRICO MENOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027289", "FECHAM MÓVEL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028199", "COMPL FECHAM LATERAL - ELEV MENOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028466", "CHAPA SUPORTE DO MOTOR - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028288", "COMPLEMENTO FECHAMENTO - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028289", "COMPLEM FECHAM MENOR - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028459", "FECH LONG LONGITUDINAL - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028461", "CANTONEIRA SUPERIOR - ESTEIRA HORIZONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028208", "FECHAMENTO CENTRAL (TRAS.)- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028209", "FECHAMENTO TRASEIRO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028207", "FECHAMENTO DIANTEIRO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028206", "FECHAMENTO LATERAL BAIA- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027939", "CHAPA DE DESCIDA EST DAS BAIAS- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027546", "CANTONEIRA DE APOIO DO MANCAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027623", "CANTONEIRA INFERIOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029829", "RAMPA RETROFIT- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028007", "CALHA CENTRAL- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030219", "FECHAMENTO LATERAL MOTOR - MÓDULO MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027734", "PROTEÇÃO DO EIXO MOVIDO- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028239", "FECHAMENTO EIXO DAS ESTEIRAS- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028377", "FECHAMENTO EIXO DAS ESTEIRAS MOD MOTOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030222", "FECHAMENTO LATERAL MOVIDO - MÓD MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028470", "FECHAMENTO CALHA MENOR - MÓDULO MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027177", "CORPO DO LIMPADOR- SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027246", "BANDEJA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029882", "FECHAMENTO INFERIOR - LAVADORA DE ESCOVAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027358", "FECHAMENTO FRONTAL LAVADORA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027623", "CANTONEIRA INFERIOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029829", "RAMPA RETROFIT - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028239", "FECHAMENTO EIXO DAS ESTEIRAS - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028200", "FECHAMENTO EIXO MOTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027734", "PROTEÇÃO DO EIXO MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("030166", "PROTEÇÃO DA CORRENTE - MÓDULO MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027684", "CHAPA SUPERIOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027889", "CALHA CENTRAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027701", "PERFIL L DA GUIA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028424", "ESTICADOR MOD MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028425", "BASE CONT ROTAÇÃO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027904", "GUIA BANDEJA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("027696", "CHAPA GUIA LATERAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028513", "CANTONEIRA DO PLÁSTICO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("029731", "FECHAMENTO CALHA MENOR - MÓDULO MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028468", "FECHAMENTO CALHA MEDIANA - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028519", "FECHAMENTO LATERAL MAIOR - MÓDULO MOVIDO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028672", "CANTONEIRA DE LIGAÇÃO - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028428", "CHAPA SUPORTE MOTOREDUTOR - SELECIONADORA DE FRUTAS", "Estamparia", "ativo"),
    ("028381", "FECHAMENTO FRONTAL - SELECIONADORA DE FRUTAS", "Estamparia", "ativo")
]

# Listas para armazenar os resultados das inserções
success = []
errors = []

# Inserção dos dados
for codigo, descricao, setor, status in pecas:
    try:
        cur.execute("""
            INSERT INTO pcp.base_pecas (codigo, descricao, setor, status)
            VALUES (%s, %s, %s, %s);
        """, (codigo, descricao, setor, status))
        conn.commit()
        success.append((codigo, descricao))
    except Exception as e:
        conn.rollback()  # Reverte a transação em caso de erro
        errors.append((codigo, descricao, str(e)))

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
