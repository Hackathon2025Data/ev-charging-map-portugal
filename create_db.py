import sqlite3
import json
import os
import numpy as np # Para lidar com potenciais inf em Potencia por Ponto

# --- Configuração ---
JSON_FILE = os.path.join('data', 'postos_carregamento.json')
DB_FILE = 'charging_stations.db'
TABLE_NAME = 'stations'

# --- Funções Auxiliares ---

def create_connection(db_file):
    """ Cria uma conexão com a base de dados SQLite especificada por db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conectado a {db_file} (SQLite versão: {sqlite3.sqlite_version})")
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar à base de dados: {e}")
    return conn

def create_table(conn):
    """ Cria a tabela stations se ela não existir """
    # Usar nomes de colunas SQL standard (snake_case)
    sql_create_stations_table = f""" CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                        id INTEGER PRIMARY KEY,
                                        nome TEXT,
                                        operador TEXT,
                                        endereco TEXT,
                                        cidade TEXT,
                                        codigo_postal TEXT,
                                        latitude REAL NOT NULL,
                                        longitude REAL NOT NULL,
                                        numero_pontos INTEGER,
                                        potencia_total_kw REAL,
                                        data_atualizacao TEXT,
                                        potencia_por_ponto_kw REAL
                                    ); """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_stations_table)
        print(f"Tabela '{TABLE_NAME}' verificada/criada com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao criar a tabela: {e}")

def load_json_data(json_path):
    """ Carrega os dados do ficheiro JSON """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Dados carregados de {json_path} ({len(data)} registos).")
        return data
    except FileNotFoundError:
        print(f"Erro: Ficheiro JSON não encontrado em '{json_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao fazer parse do ficheiro JSON em '{json_path}'")
        return None
    except Exception as e:
        print(f"Erro inesperado ao ler o JSON: {e}")
        return None

def insert_station_data(conn, stations_data):
    """ Insere os dados das estações na tabela """
    if not stations_data:
        return
        
    sql_insert = f''' INSERT OR IGNORE INTO {TABLE_NAME}(
                        id, nome, operador, endereco, cidade, codigo_postal, 
                        latitude, longitude, numero_pontos, potencia_total_kw, 
                        data_atualizacao, potencia_por_ponto_kw
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
    
    cursor = conn.cursor()
    inserted_count = 0
    skipped_count = 0

    for station in stations_data:
        try:
            # Garantir que temos os campos numéricos básicos
            station_id = station.get('ID')
            lat = station.get('Latitude')
            lon = station.get('Longitude')
            num_pontos = station.get('Número de Pontos')
            potencia_total = station.get('Potência Total (kW)')

            if station_id is None or lat is None or lon is None:
                 # print(f"Aviso: Ignorando registo sem ID/Lat/Lon: {station.get('Nome', 'Nome Desconhecido')}")
                 skipped_count += 1
                 continue
                 
            # Converter para tipos numéricos corretos, tratando erros
            try:
                lat = float(lat)
                lon = float(lon)
                num_pontos = int(num_pontos) if num_pontos is not None else 0
                potencia_total = float(potencia_total) if potencia_total is not None else 0.0
            except (ValueError, TypeError):
                 # print(f"Aviso: Ignorando registo com dados numéricos inválidos: ID {station_id}")
                 skipped_count += 1
                 continue

            # Calcular potência por ponto
            potencia_por_ponto = None
            if num_pontos is not None and num_pontos > 0:
                if potencia_total is not None:
                    potencia_por_ponto = potencia_total / num_pontos
                    # Lidar com infinito caso potencia_total seja grande e num_pontos seja 0 (embora já filtrado)
                    if potencia_por_ponto == np.inf or potencia_por_ponto == -np.inf:
                        potencia_por_ponto = None 
            
            data_tuple = (
                station_id,
                station.get('Nome'),
                station.get('Operador'),
                station.get('Endereço'),
                station.get('Cidade'),
                station.get('Código Postal'),
                lat,
                lon,
                num_pontos,
                potencia_total,
                station.get('Data Atualização'),
                potencia_por_ponto
            )
            
            cursor.execute(sql_insert, data_tuple)
            inserted_count += cursor.rowcount # Adiciona 1 se inseriu, 0 se ignorou (ID já existe)
            if cursor.rowcount == 0:
                skipped_count +=1 # Conta como ignorado se o ID já existia

        except sqlite3.Error as e:
            print(f"Erro ao inserir dados para ID {station.get('ID', 'N/A')}: {e}")
            skipped_count += 1
        except Exception as e:
            print(f"Erro inesperado no processamento do registo ID {station.get('ID', 'N/A')}: {e}")
            skipped_count += 1
            
    conn.commit()
    print(f"Inserção concluída. {inserted_count} registos inseridos, {skipped_count} ignorados/com erro.")

# --- Função Principal ---

def main():
    print("Iniciando processo de criação da base de dados SQLite...")
    
    # Carregar dados JSON
    stations_data = load_json_data(JSON_FILE)
    if not stations_data:
        return # Termina se não conseguiu carregar o JSON
        
    # Criar/Conectar à base de dados
    conn = create_connection(DB_FILE)
    if conn is None:
        return # Termina se não conseguiu conectar/criar a DB
        
    # Criar tabela
    create_table(conn)
    
    # Inserir dados
    insert_station_data(conn, stations_data)
    
    # Fechar conexão
    if conn:
        conn.close()
        print("Conexão com a base de dados fechada.")

    print("Processo concluído.")

# --- Execução --- 
if __name__ == '__main__':
    main() 