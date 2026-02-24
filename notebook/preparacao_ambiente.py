# ============================================================================
# IMPORTAÇÕES
# ============================================================================

# Manipulação de dados
import pandas as pd
import numpy as np

# Visualizações
import matplotlib.pyplot as plt
import seaborn as sns

# Sistema operacional
import os
import warnings

# Data e hora
from datetime import datetime

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================

# Ignorar warnings desnecessários
warnings.filterwarnings('ignore')

# Configurações do Pandas
pd.set_option('display.max_columns', None)  # Mostrar todas as colunas
pd.set_option('display.max_rows', 100)  # Mostrar até 100 linhas
pd.set_option('display.float_format', '{:.2f}'.format)  # 2 casas decimais
pd.set_option('display.width', 1000)  # Largura da exibição

# Configurações de visualização
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)
sns.set_palette("husl")

# Configuração de cores personalizadas
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'churn_yes': '#e74c3c',
    'churn_no': '#27ae60'
}

# ============================================================================
# ESTRUTURA DE PASTAS
# ============================================================================

def criar_estrutura_pastas():
    """
    Cria a estrutura de pastas do projeto se não existir

     Returns:
        None
    """
    pastas = [
        'data',
        'data/raw',
        'data/processed',
        'data/dashboard',
        'outputs',
        'outputs/plots',
        'outputs/metrics'
    ]

    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"✅ Pasta criada/verificada: {pasta}")

# Executar criação de pastas
criar_estrutura_pastas()

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def print_section(title):
    """
    Imprime um cabeçalho de seção formatado
    """
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_subsection(title):
    """
    Imprime um sub cabeçalho formatado
    """
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80 + "\n")

def salvar_info_execucao(arquivo, mensagem):
    """
    Salva informações sobre a execução em um arquivo de log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('outputs/log_execucao.txt', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {arquivo}: {mensagem}\n")

# ============================================================================
# INFORMAÇÕES DO PROJETO
# ============================================================================

print_section("AMBIENTE PREPARADO COM SUCESSO!")

print("📦 Bibliotecas carregadas:")
print("   ✓ pandas, numpy")
print("   ✓ matplotlib, seaborn")
print("   ✓ os, warnings, datetime")
print(f"   ✓ pandas {pd.__version__}, numpy {np.__version__}")

print("\n📁 Estrutura de pastas criada/verificada")

print("\n🚀 Pronto para começar a análise!")

# Registrar no log
salvar_info_execucao("preparacao_ambiente.py", "Ambiente configurado com sucesso")