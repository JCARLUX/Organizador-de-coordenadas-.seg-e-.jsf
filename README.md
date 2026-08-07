# Organizador de coordenadas .seg e .jsf

## Sumário
* [Resumo](#resumo)
* [Objetivo](#objetivo)
* [Tecnologias](#tecnologias)
* [Funcionalidades](#funcionalidades)
* [Como Executar](#como-executar)
    * [1. Pré-requisitos](#1-pré-requisitos)
    * [2. Instalação das Dependências](#2-instalação-das-dependências)

---

## Resumo
Pipeline em Python para a extração de coordenadas e organização espacial automática de arquivos geofísicos (`.seg`, `.jsf`), incluindo a geração de rotas em formato KML. O script transforma dados brutos e desorganizados em uma estrutura de diretórios baseada a partir da localização geográfica da coleta.

## Objetivo
Pesquisadores e profissionais lidam frequentemente com grandes volumes de dados marinhos e geofísicos gerados por sonares e equipamentos de navegação. Muitas vezes, esses arquivos perdem sua organização espacial de origem. Este projeto resolve o problema mapeando as coordenadas internas dos arquivos e realocando-os automaticamente em pastas correspondentes ao Estado brasileiro ou região costeira mais próxima, otimizando o fluxo de trabalho em centros de pesquisa.

## Tecnologias
* **Python 3**
* **GeoPandas & Shapely:** Análise e processamento geoespacial.
* **Segyio:** Leitura e extração de cabeçalhos de arquivos sísmicos/geofísicos.
* **Expressões Regulares (Regex):** Extração de padrões NMEA.

## Funcionalidades
* A principal funcionalidade está na leitura universal dos arquivos, conseguindo extrair informações tanto de arquivos de texto simples como o `.jsf` quanto de binários complexos como o `.seg`.
* O script consegue cruzar coordenadas dos arquivos com um mapa GeoJSON do Brasil, identificando o estado e se a coleta ocorreu na costa, em alto mar ou em águas internacionais.
* O projeto também possui a capacidade de compactar os resultados em arquivos `.zip` divididos por estado, prontos para armazenamento ou distribuição.

## Como Executar

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.8+** instalado em sua máquina. O gerenciamento de pacotes será feito via `pip`.

### 2. Instalação das Dependências
Para que o script consiga ler os arquivos binários e processar os dados geoespaciais, instale as bibliotecas necessárias abrindo o seu terminal e executando:

```bash
pip install -r requirements.txt
