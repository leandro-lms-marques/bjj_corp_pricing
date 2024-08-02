# Análise de Precificação - BJJ CORP

Este repositório contém um aplicativo Streamlit para análise de precificação de serviços, desenvolvido para a BJJ CORP. O aplicativo permite calcular o custo total, lucro, ponto de equilíbrio e outros parâmetros financeiros com base em diversos inputs fornecidos pelo usuário.

## Funcionalidades

- **Cálculo de Custos Fixos e Variáveis**: Calcula os custos fixos e variáveis mensais.
- **Análise de Cenários**: Permite a análise de múltiplos cenários para diferentes empresas.
- **Cálculo de Alunos por Professor**: Calcula o número de alunos que cada professor pode atender por mês.
- **Cálculo de Professores Necessários**: Determina o número de professores necessários para atender todos os alunos.
- **Visualização de Dados**: Exibe gráficos e tabelas para melhor compreensão dos dados financeiros.
- **Personalização de Inputs**: Permite ao usuário ajustar parâmetros como custos, capacidade, lucro desejado, impostos, etc.
- **Exibição de Logo**: Exibe a logo da empresa no frontend.

## Instalação

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

### Passos

1. Clone o repositório:

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Crie um ambiente virtual (opcional, mas recomendado):

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Execute o aplicativo Streamlit:

    ```bash
    streamlit run main.py
    ```