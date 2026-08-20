import os
import zipfile
import shutil
import math
import urllib.request
import warnings
import re
import logging
import geopandas as gpd
from shapely.geometry import Point
import segyio

# Silencia avisos do Pandas referentes a CRS
warnings.filterwarnings('ignore', message='.*Geometry is in a geographic CRS.*')

# Configuracao do Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processamento.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Caminhos de diretorio
CAMINHO_ORIGEM = './dados_entrada' 
PASTA_BASE_SAIDA = './dados_saida/Organizados'
PASTA_ZIPS = './dados_saida/ZIPS_POR_ESTADO'
CAMINHO_MAPA = './dados_saida/brazil-states.geojson'

logging.info("Carregando o mapa geometrico do Brasil...")

os.makedirs(os.path.dirname(CAMINHO_MAPA), exist_ok=True)

if not os.path.exists(CAMINHO_MAPA):
    url_mapa = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    try:
        urllib.request.urlretrieve(url_mapa, CAMINHO_MAPA)
    except Exception as e:
        logging.error(f"Erro ao baixar o mapa: {e}")

gdf_estados = gpd.read_file(CAMINHO_MAPA)

# Marcos para referencia costeira
MARCOS_COSTEIROS = [
    (4.43, -51.45, "Cabo Orange (Amapá)"),
    (0.05, -49.95, "Foz do Rio Amazonas / Macapá"),
    (-0.85, -48.30, "Baía de Marajó"),
    (-0.63, -47.63, "Marudá"),
    (-0.61, -47.35, "Salinópolis"),
    (-2.53, -44.30, "Baía de São Marcos (São Luís)"),
    (-2.75, -42.82, "Rio Preguiças (Lençóis Maranhenses)"),
    (-2.75, -41.82, "Delta do Rio Parnaíba"),
    (-2.87, -41.66, "Luís Correia"),
    (-2.79, -40.51, "Jericoacoara"),
    (-3.73, -38.52, "Fortaleza"),
    (-4.56, -37.76, "Aracati (Rio Jaguaribe)"),
    (-3.86, -33.80, "Atol das Rocas"),
    (-3.84, -32.40, "Fernando de Noronha"),
    (0.91, -29.34, "Arquipélago de São Pedro e São Paulo"),
    (-4.95, -37.13, "Areia Branca"),
    (-4.95, -36.88, "Ponta do Mel"),
    (-5.11, -36.63, "Macau"),
    (-5.48, -35.26, "Cabo de São Roque"),
    (-5.87, -35.17, "Natal (Ponta Negra)"),
    (-6.96, -34.83, "Foz do Rio Paraíba (Cabedelo)"),
    (-7.14, -34.79, "Cabo Branco"),
    (-8.28, -34.94, "Cabo de Santo Agostinho"),
    (-8.50, -34.99, "Porto de Galinhas"),
    (-8.72, -35.09, "Foz do Rio Formoso"),
    (-9.01, -35.22, "Maragogi"),
    (-9.66, -35.73, "Maceió"),
    (-10.40, -36.45, "Piaçabuçu"),
    (-10.50, -36.40, "Foz do Rio São Francisco"),
    (-10.97, -37.04, "Aracaju"),
    (-11.45, -37.38, "Foz do Rio Real / Vaza-Barris"),
    (-12.58, -38.00, "Praia do Forte"),
    (-13.00, -38.50, "Baía de Todos os Santos (Salvador)"),
    (-14.81, -39.03, "Ilhéus"),
    (-16.44, -39.06, "Porto Seguro"),
    (-17.96, -38.70, "Arquipélago de Abrolhos")
]

def converter_nmea_para_decimal(valor_string, direcao):
    if not valor_string or not direcao: return 0.0
    try:
        ponto_idx = valor_string.find('.')
        if ponto_idx == -1: return 0.0
        minutos_str = valor_string[ponto_idx-2:]
        graus_str = valor_string[:ponto_idx-2]
        graus = float(graus_str) if graus_str else 0.0
        decimal = graus + (float(minutos_str) / 60.0)
        if direcao in ['S', 'W']: decimal = -decimal
        return round(decimal, 6)
    except: return 0.0

def seg_coord_para_decimal(coord_str):
    if not coord_str: return 0.0
    partes = re.split(r'[°\' ]+', coord_str)
    try:
        graus = float(partes[0])
        minutos = float(partes[1])
        direcao = partes[2]
        decimal = graus + (minutos / 60.0)
        if direcao in ['S', 'W']: decimal = -decimal
        return round(decimal, 6)
    except: return 0.0

def limpar_nome_pasta(nome):
    for char in '<>:"/\\|?*': nome = nome.replace(char, '')
    return nome.strip()

def identificar_geometria(lat, lon, gdf):
    ponto = Point(lon, lat)
    distancias = gdf.geometry.distance(ponto)
    distancia_minima = distancias.min()
    
    if distancia_minima > 5.0:
        return "Águas Internacionais", "Oceano Global", True
    
    indice_estado_proximo = distancias.idxmin()
    estado = gdf.loc[indice_estado_proximo, 'name']
    eh_offshore = distancia_minima > 0.01
    
    dist_min_marco = float('inf')
    referencia_temporaria = "Litoral Não Mapeado"
    
    for m_lat, m_lon, m_nome in MARCOS_COSTEIROS:
        dist_euclidiana = math.sqrt((lat - m_lat)**2 + (lon - m_lon)**2)
        if dist_euclidiana < dist_min_marco:
            dist_min_marco = dist_euclidiana
            referencia_temporaria = m_nome
            
    if dist_min_marco < 1.5:
        referencia = referencia_temporaria
    else:
        referencia = "Costa Não Mapeada"
            
    palavras_aguas_abrigadas = ["Rio", "Foz", "Delta", "Baía", "Piaçabuçu"]
    if any(palavra in referencia for palavra in palavras_aguas_abrigadas):
        eh_offshore = False

    return estado, referencia, eh_offshore

nav_pattern_seg = re.compile(
    r"(?P<data>\d{2}/\d{2}/\d{2})\s+"
    r"(?P<hora>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<lat>\d{2}°\s+\d{2}\.\d+'\s+[NS])\s+"
    r"(?P<lon>\d{3}°\s+\d{2}\.\d+'\s+[EW])"
)

def extrair_trajeto(caminho_arquivo):
    coordenadas = []
    extensao = caminho_arquivo.lower()

    def varredura_texto_bruto():
        coords_texto = []
        with open(caminho_arquivo, 'rb') as f_bin:
            for linha_binaria in f_bin:
                try:
                    linha = linha_binaria.decode('ascii', errors='ignore')
                    
                    if '$GP' in linha:
                        start = linha.find('$GP')
                        linha_limpa = linha[start:].strip()
                        partes = linha_limpa.split(',')
                        lat, lon = 0.0, 0.0
                        
                        if linha_limpa.startswith('$GPGGA') and len(partes) > 5:
                            lat = converter_nmea_para_decimal(partes[2], partes[3])
                            lon = converter_nmea_para_decimal(partes[4], partes[5])
                        elif linha_limpa.startswith('$GPRMC') and len(partes) > 6 and partes[2] == 'A':
                            lat = converter_nmea_para_decimal(partes[3], partes[4])
                            lon = converter_nmea_para_decimal(partes[5], partes[6])
                        elif linha_limpa.startswith('$GPGLL') and len(partes) > 4:
                            lat = converter_nmea_para_decimal(partes[1], partes[2])
                            lon = converter_nmea_para_decimal(partes[3], partes[4])
                        
                        if lat != 0 and lon != 0:
                            coords_texto.append((lat, lon))
                            continue
                            
                    match = nav_pattern_seg.search(linha)
                    if match:
                        lat = seg_coord_para_decimal(match.group('lat'))
                        lon = seg_coord_para_decimal(match.group('lon'))
                        if lat != 0 and lon != 0:
                            coords_texto.append((lat, lon))
                except:
                    continue
        return coords_texto

    if extensao.endswith('.jsf'):
        coordenadas = varredura_texto_bruto()
        
    elif extensao.endswith('.seg'):
        try:
            with segyio.open(caminho_arquivo, "r", ignore_geometry=True, strict=False) as f:
                for trace in f.header:
                    sx = trace[segyio.TraceField.SourceX]
                    sy = trace[segyio.TraceField.SourceY]
                    
                    if sx == 0 and sy == 0:
                        sx = trace[segyio.TraceField.GroupX]
                        sy = trace[segyio.TraceField.GroupY]
                    if sx == 0 and sy == 0:
                        sx = trace[segyio.TraceField.CDP_X]
                        sy = trace[segyio.TraceField.CDP_Y]

                    scalar = trace[segyio.TraceField.SourceGroupScalar]
                    
                    if sx != 0 or sy != 0:
                        if scalar < 0:
                            lon = sx / abs(scalar)
                            lat = sy / abs(scalar)
                        elif scalar > 0:
                            lon = sx * scalar
                            lat = sy * scalar
                        else:
                            lon, lat = sx, sy
                        
                        if abs(lat) > 90 or abs(lon) > 180:
                            lat = lat / 3600.0
                            lon = lon / 3600.0
                        
                        if -90 <= lat <= 90 and -180 <= lon <= 180 and lat != 0 and lon != 0:
                            coordenadas.append((lat, lon))
        except Exception:
            pass
            
        if len(coordenadas) == 0:
            coordenadas = varredura_texto_bruto()
    
    trajeto_limpo = []
    for c in coordenadas:
        if not trajeto_limpo or trajeto_limpo[-1] != c:
            trajeto_limpo.append(c)
            
    return trajeto_limpo

if os.path.isdir(CAMINHO_ORIGEM):
    arquivos = [f for f in os.listdir(CAMINHO_ORIGEM) if f.lower().endswith(('.jsf', '.seg'))]
    
    os.makedirs(PASTA_ZIPS, exist_ok=True)
    os.makedirs(PASTA_BASE_SAIDA, exist_ok=True) 
    
    for arquivo in arquivos:
        caminho_completo = os.path.join(CAMINHO_ORIGEM, arquivo)
        logging.info(f"Processando: {arquivo}")
        
        trajeto = extrair_trajeto(caminho_completo)
        
        if trajeto:
            ponto_central = trajeto[len(trajeto)//2]
            estado, local, eh_offshore = identificar_geometria(ponto_central[0], ponto_central[1], gdf_estados)

            estado_limpo = limpar_nome_pasta(estado)
            local_limpo = limpar_nome_pasta(local)
            
            if eh_offshore:
                pasta_destino = os.path.join(PASTA_BASE_SAIDA, estado_limpo, "Alto Mar", local_limpo)
                status_log = f"{estado_limpo} -> Alto Mar -> {local_limpo}"
            else:
                pasta_destino = os.path.join(PASTA_BASE_SAIDA, estado_limpo, local_limpo)
                status_log = f"{estado_limpo} -> {local_limpo}"

            os.makedirs(pasta_destino, exist_ok=True)
            
            shutil.copy2(caminho_completo, os.path.join(pasta_destino, arquivo))
            
            coordenadas_kml = " ".join([f"{lon},{lat},0" for lat, lon in trajeto])
            nome_kml = os.path.splitext(arquivo)[0] + "_trajeto.kml"
            
            kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>{arquivo}</name><Placemark><name>Trajeto</name>
<LineString><tessellate>1</tessellate><coordinates>{coordenadas_kml}</coordinates></LineString>
</Placemark></Document></kml>"""
            
            with open(os.path.join(pasta_destino, nome_kml), 'w', encoding='utf-8') as f_kml:
                f_kml.write(kml_content)
            
            logging.info(f"Sucesso: {status_log} | Pontos no KML: {len(trajeto)}")
        else:
            logging.warning(f"Nenhuma coordenada valida encontrada no arquivo {arquivo}. Ignorado.")

    logging.info("Gerando ZIPs por Estado/Regiao...")
    for item in os.listdir(PASTA_BASE_SAIDA):
        caminho_item = os.path.join(PASTA_BASE_SAIDA, item)
        if os.path.isdir(caminho_item):
            nome_zip = limpar_nome_pasta(item)
            shutil.make_archive(os.path.join(PASTA_ZIPS, nome_zip), 'zip', caminho_item)
            logging.info(f"Pacote criado: {nome_zip}.zip")

    logging.info(f"Processamento concluido. Arquivos disponiveis em '{PASTA_ZIPS}'.")
else:
    logging.error(f"Erro: O diretorio de origem nao foi encontrado. Verifique a variavel 'CAMINHO_ORIGEM'.")
