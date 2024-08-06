import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configurar a chave da API do OpenAI
openai.api_key = 'YOUR_OPENAI_API_KEY'

def formatar_moeda(valor):
    """Formata um valor numérico para o formato de moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class ServicoPrecificacao:
    def __init__(self, custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, horas_trabalhadas_professor, aulas_por_aluno_mes, jornada_trabalho_diaria, fator_produtividade):
        self.custos_fixos = custos_fixos
        self.custos_variaveis = custos_variaveis
        self.capacidade_maxima = capacidade_maxima
        self.lucro_desejado = lucro_desejado
        self.impostos = impostos
        self.transporte_alimentacao_por_dia = transporte_alimentacao_por_dia
        self.horas_trabalhadas_professor = horas_trabalhadas_professor
        self.aulas_por_aluno_mes = aulas_por_aluno_mes
        self.jornada_trabalho_diaria = jornada_trabalho_diaria
        self.fator_produtividade = fator_produtividade
        self.alunos_por_professor = self.calcular_alunos_por_professor()
        self.volume_horas_disponiveis = self.calcular_volume_horas_disponiveis()

    def calcular_custos_fixos_mensais(self):
        """Calcula o custo fixo mensal total."""
        return sum(self.custos_fixos.values())

    def calcular_custos_variaveis_por_professor_mes(self):
        """Calcula os custos variáveis mensais por professor."""
        dias_trabalhados = self.horas_trabalhadas_professor / self.jornada_trabalho_diaria
        return (self.custos_variaveis['Professor'] * self.horas_trabalhadas_professor + 
                self.transporte_alimentacao_por_dia * dias_trabalhados + 
                self.custos_variaveis.get('Outras Despesas', 0))

    def calcular_alunos_por_professor(self):
        """Calcula o número de alunos que um professor pode atender por mês."""
        capacidade_por_hora = self.capacidade_maxima
        horas_por_aluno_mes = self.aulas_por_aluno_mes
        total_horas_trabalho_mes = self.horas_trabalhadas_professor
        return (total_horas_trabalho_mes // horas_por_aluno_mes) * capacidade_por_hora

    def calcular_numero_professores(self, numero_alunos):
        """Calcula o número de professores necessários."""
        if self.alunos_por_professor == 0:
            return 1  # Evita divisão por zero
        return max(1, (numero_alunos + self.alunos_por_professor - 1) // self.alunos_por_professor)

    def calcular_custo_total(self, numero_alunos, preco_por_aluno_mes):
        """Calcula o custo total mensal."""
        custos_fixos = self.calcular_custos_fixos_mensais()
        numero_professores = self.calcular_numero_professores(numero_alunos)
        custos_variaveis = self.calcular_custos_variaveis_por_professor_mes() * numero_professores
        receita = numero_alunos * preco_por_aluno_mes
        impostos = receita * self.impostos
        return custos_fixos + custos_variaveis + impostos

    def calcular_lucro(self, numero_alunos, preco_por_aluno_mes):
        """Calcula o lucro mensal."""
        receita = numero_alunos * preco_por_aluno_mes
        custo_total = self.calcular_custo_total(numero_alunos, preco_por_aluno_mes)
        return receita - custo_total

    def calcular_ponto_equilibrio(self, preco_por_aluno_mes):
        """Calcula o ponto de equilíbrio."""
        custos_fixos = self.calcular_custos_fixos_mensais()
        custo_variavel_por_aluno = self.calcular_custos_variaveis_por_professor_mes() / self.alunos_por_professor
        return custos_fixos / (preco_por_aluno_mes * (1 - self.impostos) - custo_variavel_por_aluno)

    def calcular_ganho_professor_mes(self):
        """Calcula o ganho mensal por professor."""
        dias_trabalhados = self.horas_trabalhadas_professor / self.jornada_trabalho_diaria
        return self.custos_variaveis['Professor'] * self.horas_trabalhadas_professor + self.transporte_alimentacao_por_dia * dias_trabalhados

    def calcular_volume_horas_disponiveis(self):
        """Calcula o volume de horas disponíveis para trabalho."""
        return self.horas_trabalhadas_professor * self.fator_produtividade

    def calcular_preco_hora_alvo(self, resultado_mensal_esperado):
        """Calcula o preço hora alvo."""
        return resultado_mensal_esperado / self.calcular_volume_horas_disponiveis()

@st.cache_data
def carregar_logo():
    """Carrega a logo da empresa."""
    return "logo.png"

def exibir_sidebar():
    """Exibe a barra lateral com os parâmetros gerais."""
    st.sidebar.header("Parâmetros Gerais")
    custos_fixos = {
        "Pessoal": st.sidebar.number_input("Custo Fixo - Pessoal", value=20000, step=1000),
        "Aluguel": st.sidebar.number_input("Custo Fixo - Aluguel", value=10000, step=1000),
        "Outras Despesas": st.sidebar.number_input("Custo Fixo - Outras Despesas", value=10000, step=1000)
    }
    custo_professor = st.sidebar.number_input("Custo Variável - Professor (por hora)", value=80, step=10)
    custo_outras_despesas = st.sidebar.number_input("Custo Variável - Outras Despesas", value=1000, step=100)
    custos_variaveis = {"Professor": custo_professor, "Outras Despesas": custo_outras_despesas}
    capacidade_maxima = st.sidebar.number_input("Capacidade Máxima por Aula", value=20, step=1)
    lucro_desejado = st.sidebar.slider("Lucro Desejado (%)", 0, 100, 20) / 100
    impostos = st.sidebar.slider("Impostos (%)", 0, 100, 15) / 100
    transporte_alimentacao_por_dia = st.sidebar.number_input("Transporte e Alimentação por dia", value=40, step=5)
    jornada_trabalho_diaria = st.sidebar.number_input("Jornada de Trabalho Diária (horas)", value=8, step=1)
    fator_produtividade = st.sidebar.slider("Fator de Produtividade (%)", 0, 100, 100) / 100
    resultado_mensal_esperado = st.sidebar.number_input("Resultado Mensal Esperado", value=10000, step=1000)
    
    return custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, jornada_trabalho_diaria, fator_produtividade, resultado_mensal_esperado

def gerar_resumo_e_sugestoes(servico, numero_alunos, preco_por_aluno_mes_ajustado, resultado_mensal_esperado):
    """Gera um resumo e sugestões usando a API do OpenAI GPT-3."""
    resumo = f"""
    Análise de Precificação e Lucro - Resumo

    Número de Alunos: {numero_alunos}
    Preço por Aluno/Mês: {formatar_moeda(preco_por_aluno_mes_ajustado)}
    Receita Total: {formatar_moeda(numero_alunos * preco_por_aluno_mes_ajustado)}
    Custo Total: {formatar_moeda(servico.calcular_custo_total(numero_alunos, preco_por_aluno_mes_ajustado))}
    Lucro: {formatar_moeda(servico.calcular_lucro(numero_alunos, preco_por_aluno_mes_ajustado))}
    Margem de Lucro: {(servico.calcular_lucro(numero_alunos, preco_por_aluno_mes_ajustado) / (numero_alunos * preco_por_aluno_mes_ajustado)):.2%}
    Professores Necessários: {servico.calcular_numero_professores(numero_alunos)}
    Ganho por Professor/Mês: {formatar_moeda(servico.calcular_ganho_professor_mes())}
    Volume de Horas Disponíveis: {servico.calcular_volume_horas_disponiveis()}
    Preço Hora Alvo: {formatar_moeda(servico.calcular_preco_hora_alvo(resultado_mensal_esperado))}
    """

    prompt = f"Analise o seguinte resumo financeiro e forneça sugestões para melhorar os resultados:\n\n{resumo}"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7,
    )

    sugestoes = response.choices[0].text.strip()
    return resumo, sugestoes

def exibir_cenario_empresa(i, custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, jornada_trabalho_diaria, fator_produtividade, resultado_mensal_esperado):
    """Exibe a análise de cenário para uma empresa específica."""
    st.subheader(f"Empresa {i+1}")
    
    horas_trabalhadas_professor = st.number_input(f"Horas Trabalhadas por Professor por Mês - Empresa {i+1}", value=160, step=8)
    aulas_por_aluno_mes = st.number_input(f"Aulas por Aluno por Mês - Empresa {i+1}", value=8, step=1)
    
    servico = ServicoPrecificacao(custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, horas_trabalhadas_professor, aulas_por_aluno_mes, jornada_trabalho_diaria, fator_produtividade)
    
    numero_alunos = st.number_input(f"Número de Alunos na Empresa {i+1}", 1, 1000, 500)

    preco_por_aluno_mes = servico.calcular_custos_variaveis_por_professor_mes() / servico.alunos_por_professor
    preco_por_aluno_mes *= (1 + lucro_desejado) / (1 - impostos)
    st.write(f"Preço calculado por Aluno/Mês: {formatar_moeda(preco_por_aluno_mes)}")
    
    preco_por_aluno_mes_ajustado = st.number_input(f"Ajuste o Preço por Aluno/Mês para Empresa {i+1}", value=preco_por_aluno_mes, step=10.0)

    lucro = servico.calcular_lucro(numero_alunos, preco_por_aluno_mes_ajustado)
    receita_total = numero_alunos * preco_por_aluno_mes_ajustado
    custo_total = servico.calcular_custo_total(numero_alunos, preco_por_aluno_mes_ajustado)
    impostos_total = receita_total * impostos
    margem_lucro = lucro / receita_total if receita_total > 0 else 0
    numero_professores = servico.calcular_numero_professores(numero_alunos)
    ganho_professor_mes = servico.calcular_ganho_professor_mes()
    volume_horas_disponiveis = servico.calcular_volume_horas_disponiveis()
    preco_hora_alvo = servico.calcular_preco_hora_alvo(resultado_mensal_esperado)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Receita Total**<br><span style='font-size:1.5em'>{formatar_moeda(receita_total)}</span>", unsafe_allow_html=True)
    col1.markdown(f"**Custo Total**<br><span style='font-size:1.5em'>{formatar_moeda(custo_total)}</span>", unsafe_allow_html=True)
    col1.markdown(f"**Lucro**<br><span style='font-size:1.5em'>{formatar_moeda(lucro)}</span>", unsafe_allow_html=True)
    
    col2.markdown(f"**Margem de Lucro**<br><span style='font-size:1.5em'>{margem_lucro:.2%}</span>", unsafe_allow_html=True)
    col2.markdown(f"**Professores Necessários**<br><span style='font-size:1.5em'>{numero_professores}</span>", unsafe_allow_html=True)
    col2.markdown(f"**Ganho por Professor/Mês**<br><span style='font-size:1.5em'>{formatar_moeda(ganho_professor_mes)}</span>", unsafe_allow_html=True)
    
    col3.markdown(f"**Preço por Aluno/Mês**<br><span style='font-size:1.5em'>{formatar_moeda(preco_por_aluno_mes_ajustado)}</span>", unsafe_allow_html=True)
    col3.markdown(f"**Alunos por Professor**<br><span style='font-size:1.5em'>{servico.alunos_por_professor}</span>", unsafe_allow_html=True)
    col3.markdown(f"**Impostos Totais**<br><span style='font-size:1.5em'>{formatar_moeda(impostos_total)}</span>", unsafe_allow_html=True)
    col3.markdown(f"**Volume de Horas Disponíveis**<br><span style='font-size:1.5em'>{volume_horas_disponiveis}</span>", unsafe_allow_html=True)
    col3.markdown(f"**Preço Hora Alvo**<br><span style='font-size:1.5em'>{formatar_moeda(preco_hora_alvo)}</span>", unsafe_allow_html=True)

    # Ponto de Equilíbrio
    ponto_equilibrio = servico.calcular_ponto_equilibrio(preco_por_aluno_mes_ajustado)
    st.write(f"Para o preço de {formatar_moeda(preco_por_aluno_mes_ajustado)} por aluno/mês, o ponto de equilíbrio é de {ponto_equilibrio:.2f} alunos.")

    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    alunos_range = range(1, int(numero_alunos * 1.5))
    precos = [preco_por_aluno_mes_ajustado for _ in alunos_range]
    lucros = [servico.calcular_lucro(a, preco_por_aluno_mes_ajustado) for a in alunos_range]

    ax.plot(alunos_range, precos, label="Preço por Aluno/Mês")
    ax.plot(alunos_range, lucros, label="Lucro")
    ax.axhline(y=0, color='r', linestyle='--')
    ax.set_xlabel("Número de Alunos")
    ax.set_ylabel("Valor (R$)")
    ax.set_title(f"Análise de Precificação e Lucro - Empresa {i+1}")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Tabela de dados
    df = pd.DataFrame({
        "Número de Alunos": alunos_range,
        "Preço por Aluno/Mês": [formatar_moeda(p) for p in precos],
        "Lucro": [formatar_moeda(l) for l in lucros]
    })
    st.dataframe(df)

    # Gerar Resumo e Sugestões
    resumo, sugestoes = gerar_resumo_e_sugestoes(servico, numero_alunos, preco_por_aluno_mes_ajustado, resultado_mensal_esperado)
    st.subheader("Resumo e Sugestões")
    st.text(resumo)
    st.text(sugestoes)

def main():
    st.title("Análise de Precificação - BJJ CORP")

    # Carregar e exibir a logo
    logo = carregar_logo()
    st.sidebar.image(logo, use_column_width=True)

    # Exibir parâmetros gerais na barra lateral
    custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, jornada_trabalho_diaria, fator_produtividade, resultado_mensal_esperado = exibir_sidebar()

    # Análise de cenários
    st.header("Análise de Cenários por Empresa")
    
    num_empresas = st.number_input("Número de Empresas", 1, 10, 1)
    
    for i in range(num_empresas):
        exibir_cenario_empresa(i, custos_fixos, custos_variaveis, capacidade_maxima, lucro_desejado, impostos, transporte_alimentacao_por_dia, jornada_trabalho_diaria, fator_produtividade, resultado_mensal_esperado)

if __name__ == "__main__":
    main()