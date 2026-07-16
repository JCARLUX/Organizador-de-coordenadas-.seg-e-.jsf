# [cite_start]Organizador de coordenadas .seg e .jsf [cite: 2]

## [cite_start]📄 Resumo [cite: 3]
Pipeline em Python para extração de coordenadas e organização espacial automática de arquivos geofísicos (`.seg`, `.jsf`), incluindo a geração de rotas em formato KML. O script transforma dados brutos e sem organização prévia em uma estrutura de diretórios baseada na localização geográfica da coleta.

## [cite_start]💻 Demonstração [cite: 4]
> [cite_start]**Nota:** Adicione aqui uma captura de tela do terminal rodando o script ou um GIF mostrando a pasta de saída sendo populada com os arquivos e os `.kml`. [cite: 5]
> 
> *Exemplo visual: `![Demonstração do Script](link_da_imagem_ou_gif)`*

## [cite_start]🎯 Objetivo [cite: 6]
Pesquisadores e profissionais lidam frequentemente com grandes volumes de dados marinhos e geofísicos gerados por sonares e equipamentos de navegação. Muitas vezes, esses arquivos perdem sua organização espacial de origem. [cite_start]Este projeto resolve o problema mapeando as coordenadas internas dos arquivos e realocando-os automaticamente em pastas correspondentes ao Estado brasileiro ou à região costeira/alto mar mais próxima, otimizando o fluxo de trabalho em laboratórios e centros de pesquisa. [cite: 7]

## [cite_start]🛠️ Tecnologias [cite: 8]
[cite_start]As ferramentas e bibliotecas utilizadas no desenvolvimento incluem: [cite: 9]
* **Python 3**
* **GeoPandas & Shapely** (Análise e processamento geoespacial)
* **Segyio** (Leitura e extração de cabeçalhos de arquivos sísmicos/geofísicos)
* **Expressões Regulares (Regex)** (Extração de padrões NMEA)

## [cite_start]✨ Funcionalidades [cite: 10]
* [cite_start]**Leitura Universal:** Extrai trajetos tanto de arquivos de navegação em texto (`.jsf`) quanto de binários complexos (`.seg`). [cite: 11]
* [cite_start]**Classificação Geográfica:** Cruza as coordenadas do arquivo com um mapa GeoJSON do Brasil, identificando o Estado e se a coleta ocorreu na costa ou em alto mar. [cite: 11]
* [cite_start]**Geração de KML:** Cria automaticamente um arquivo KML para cada trajeto, permitindo a visualização rápida no Google Earth. [cite: 11]
* [cite_start]**Empacotamento Automático:** Compacta os resultados finais em arquivos `.zip` divididos por estado, prontos para armazenamento ou distribuição. [cite: 11]

## [cite_start]🚀 Como Executar [cite: 12]

### [cite_start]Pré-requisitos 
É necessário ter o Python instalado e gerenciar as bibliotecas via `pip`. 

### [cite_start]Instalação 
1. Clone este repositório:
   ```bash
   git clone [https://github.com/seu-usuario/organizador-coordenadas-seg-jsf.git](https://github.com/seu-usuario/organizador-coordenadas-seg-jsf.git)
