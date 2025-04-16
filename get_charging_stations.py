import requests
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API
BASE_URL = "https://api.openchargemap.io/v3/poi"

# Obter a chave API do ambiente
API_KEY = os.getenv('OPENCHARGE_API_KEY')

if not API_KEY:
    print("Erro: Chave API não encontrada!")
    print("Por favor, crie um arquivo .env com sua chave API.")
    print("Você pode usar o arquivo .env.example como template.")
    sys.exit(1)

HEADERS = {
    "X-API-Key": API_KEY
}

# Parâmetros para Portugal
params = {
    "countrycode": "PT",
    "maxresults": 10000,
    "compact": True,
    "verbose": False,
    "output": "json"
}

def get_charging_stations():
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar dados: {e}")
        return None

def process_stations(stations):
    processed_data = []
    
    for station in stations:
        # Extrair informações básicas
        address_info = station.get("AddressInfo", {})
        
        # Processar conexões
        connections = station.get("Connections", [])
        total_power = sum(conn.get("PowerKW", 0) for conn in connections if conn.get("PowerKW"))
        
        station_data = {
            "ID": station.get("ID"),
            "Nome": address_info.get("Title"),
            "Operador": station.get("OperatorInfo", {}).get("Title"),
            "Endereço": address_info.get("AddressLine1"),
            "Cidade": address_info.get("Town"),
            "Código Postal": address_info.get("Postcode"),
            "Latitude": address_info.get("Latitude"),
            "Longitude": address_info.get("Longitude"),
            "Número de Pontos": len(connections),
            "Potência Total (kW)": total_power,
            "Data Atualização": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        processed_data.append(station_data)
    
    return processed_data

def save_data(data, csv_file="postos_carregamento.csv", json_file="postos_carregamento.json"):
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    # Salvar como CSV
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Dados salvos em {csv_file}")
    
    # Salvar como JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Dados salvos em {json_file}")

def main():
    print("Buscando dados dos postos de carregamento em Portugal...")
    stations = get_charging_stations()
    
    if stations:
        print(f"Encontrados {len(stations)} postos de carregamento.")
        processed_data = process_stations(stations)
        save_data(processed_data)
    else:
        print("Não foi possível obter os dados dos postos de carregamento.")

if __name__ == "__main__":
    main() 