# setup_db.py
import os
from dotenv import load_dotenv
import oracledb
import logging

# Configuração do logging
logging.basicConfig(filename='setup_bd.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def tabela_existe(cursor, nome_tabela):
    """Verifica se uma tabela existe no schema atual."""
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM user_tables
            WHERE table_name = :nome_tabela
        """, nome_tabela=nome_tabela.upper())
        count = cursor.fetchone()[0]
        logging.info(f"Verificação da tabela '{nome_tabela}': {'Existe' if count > 0 else 'Não existe'}")
        return count > 0
    except oracledb.DatabaseError as e:
        logging.error(f"Erro ao verificar existência da tabela {nome_tabela}: {e}")
        return False

def criar_tabelas(conn):
    """Cria as tabelas necessárias no banco de dados Oracle se elas não existirem."""
    cursor = conn.cursor()
    try:
        # Criar tabela Colheita
        if not tabela_existe(cursor, 'COLHEITA'):
            cursor.execute("""
                CREATE TABLE Colheita (
                    ano NUMBER PRIMARY KEY,
                    quantidade_colhida NUMBER NOT NULL
                )
            """)
            logging.info("Tabela 'Colheita' criada com sucesso.")
        else:
            logging.info("Tabela 'Colheita' já existe.")

        # Criar tabela Clima
        if not tabela_existe(cursor, 'CLIMA'):
            cursor.execute("""
                CREATE TABLE Clima (
                    ano NUMBER PRIMARY KEY,
                    temperatura_media NUMBER(5,2),
                    precipitacao NUMBER,
                    CONSTRAINT fk_colheita_clima FOREIGN KEY (ano)
                        REFERENCES Colheita(ano)
                        ON DELETE CASCADE
                )
            """)
            logging.info("Tabela 'Clima' criada com sucesso.")
        else:
            logging.info("Tabela 'Clima' já existe.")

        # Criar tabela MaturidadeCana
        if not tabela_existe(cursor, 'MATURIDADECANA'):
            cursor.execute("""
                CREATE TABLE MaturidadeCana (
                    ano NUMBER PRIMARY KEY,
                    indice_maturidade NUMBER(3,2),
                    CONSTRAINT fk_colheita_maturidade FOREIGN KEY (ano)
                        REFERENCES Colheita(ano)
                        ON DELETE CASCADE
                )
            """)
            logging.info("Tabela 'MaturidadeCana' criada com sucesso.")
        else:
            logging.info("Tabela 'MaturidadeCana' já existe.")

        # Criar tabela CondicoesSolo
        if not tabela_existe(cursor, 'CONDICOESSOLO'):
            cursor.execute("""
                CREATE TABLE CondicoesSolo (
                    ano NUMBER PRIMARY KEY,
                    ph NUMBER(3,1),
                    nutrientes NUMBER(3,2),
                    CONSTRAINT fk_colheita_solo FOREIGN KEY (ano)
                        REFERENCES Colheita(ano)
                        ON DELETE CASCADE
                )
            """)
            logging.info("Tabela 'CondicoesSolo' criada com sucesso.")
        else:
            logging.info("Tabela 'CondicoesSolo' já existe.")
            
        # Criar tabela Recursos Alocados
        if not tabela_existe(cursor, 'RECURSOS_ALOCADOS'):
            cursor.execute("""
                CREATE TABLE Recursos_Alocados (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    colheita_id NUMBER NOT NULL,
                    tipo_recurso VARCHAR2(50) NOT NULL,
                    quantidade NUMBER NOT NULL,
                    data_alocacao DATE DEFAULT SYSDATE,
                    CONSTRAINT fk_colheita_recursos FOREIGN KEY (colheita_id)
                        REFERENCES Colheita(ano)
                        ON DELETE CASCADE
                )
            """)
            logging.info("Tabela 'Recursos_alocados' criada com sucesso.")
        else:
            logging.info("Tabela 'Recursos_alocados' já existe.")

        # Commit das alterações
        conn.commit()
        logging.info("Todas as tabelas foram criadas ou já existiam.")
    except oracledb.DatabaseError as e:
        logging.error(f"Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()


def setup_banco_dados(conn):
    """Função principal para configurar o banco de dados."""
    logging.info("Iniciando configuração do banco de dados")
    criar_tabelas(conn)
    logging.info("Configuração do banco de dados concluída")

if __name__ == "__main__":
    # Este bloco permite que o script seja executado independentemente,
    # útil para testes ou configuração inicial do banco de dados
    load_dotenv()
    
    try:
        conn = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        setup_banco_dados(conn)
    except oracledb.DatabaseError as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
    finally:
        if 'conn' in locals():
            conn.close()