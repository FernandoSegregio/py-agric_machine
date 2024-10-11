import oracledb

def tabela_existe(cursor, nome_tabela, logger):
    #Verifica se uma tabela existe no schema atual.
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM user_tables
            WHERE table_name = :nome_tabela
        """, nome_tabela=nome_tabela.upper())
        count = cursor.fetchone()[0]
        logger.info(f"Verificação da tabela '{nome_tabela}': {'Existe' if count > 0 else 'Não existe'}")
        return count > 0
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao verificar existência da tabela {nome_tabela}: {e}")
        return False

def criar_tabelas(conn, logger):
    #Cria as tabelas necessárias no banco de dados Oracle se elas não existirem.
    
    cursor = conn.cursor()
    try:
        # Criar tabela colheita
        if not tabela_existe(cursor, 'COLHEITA', logger):
            cursor.execute("""
                CREATE TABLE colheita (
                    id_colheita NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    ano NUMBER NOT NULL,
                    quantidade_colhida NUMBER NOT NULL
                )
            """)
            logger.info("Tabela 'colheita' criada com sucesso.")
        else:
            logger.info("Tabela 'colheita' já existe.")

        # Criar tabela clima
        if not tabela_existe(cursor, 'CLIMA', logger):
            cursor.execute("""
                CREATE TABLE clima (
                    id_clima NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    id_colheita NUMBER,
                    temperatura_media NUMBER(5,2),
                    precipitacao NUMBER,
                    CONSTRAINT fk_colheita_clima FOREIGN KEY (id_colheita)
                        REFERENCES colheita(id_colheita)
                        ON DELETE CASCADE
                )
            """)
            logger.info("Tabela 'clima' criada com sucesso.")
        else:
            logger.info("Tabela 'clima' já existe.")

        # Criar tabela maturidade_cana
        if not tabela_existe(cursor, 'MATURIDADE_CANA', logger):
            cursor.execute("""
                CREATE TABLE maturidade_cana (
                    id_maturidade NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    id_colheita NUMBER,
                    indice_maturidade NUMBER(3,2),
                    CONSTRAINT fk_colheita_maturidade FOREIGN KEY (id_colheita)
                        REFERENCES colheita(id_colheita)
                        ON DELETE CASCADE
                )
            """)
            logger.info("Tabela 'maturidade_cana' criada com sucesso.")
        else:
            logger.info("Tabela 'maturidade_cana' já existe.")

        # Criar tabela condicoes_solo
        if not tabela_existe(cursor, 'CONDICOES_SOLO', logger):
            cursor.execute("""
                CREATE TABLE condicoes_solo (
                    id_condicao NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    id_colheita NUMBER,
                    ph NUMBER(3,1),
                    nutrientes NUMBER(3,2),
                    CONSTRAINT fk_colheita_solo FOREIGN KEY (id_colheita)
                        REFERENCES colheita(id_colheita)
                        ON DELETE CASCADE
                )
            """)
            logger.info("Tabela 'condicoes_solo' criada com sucesso.")
        else:
            logger.info("Tabela 'condicoes_solo' já existe.")

        # Commit das alterações
        conn.commit()
        logger.info("Todas as tabelas foram criadas ou já existiam.")
    except oracledb.DatabaseError as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        conn.rollback()
    finally:
        cursor.close()