# ============================================================================
# IMPORTAÇÕES
# ============================================================================

# Importar configurações do arquivo anterior (SINTAXE CORRETA)
import sys
import os

# Adicionar o diretório atual ao path (se necessário)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar do arquivo 01 (SEM .py na extensão!)
from preparacao_ambiente import *

# Biblioteca adicional para JSON
import json

# ============================================================================
# CARREGAMENTO DOS DADOS
# ============================================================================

print_section("CARREGAMENTO DOS DADOS")

# Carregar o arquivo
try:
    # Tentar caminho relativo primeiro
    df = pd.read_csv('data/raw/telecom_churn_raw.csv')
    print("✅ Arquivo carregado de: data/raw/telecom_churn_raw.csv")
except FileNotFoundError:
    print("❌ ERRO: Arquivo não encontrado em data/raw/")
    print("   Coloque 'telecom_churn_raw.csv' na pasta data/raw/ e execute novamente.")
    sys.exit(1)

print(f"   📊 Dimensões: {df.shape[0]:,} linhas × {df.shape[1]} colunas")

# ============================================================================
# INSPEÇÃO INICIAL
# ============================================================================

print_section("INSPEÇÃO INICIAL DOS DADOS")

# Primeiras linhas
print_subsection("📋 PRIMEIRAS 5 LINHAS")
print(df.head())

# Últimas linhas
print_subsection("📋 ÚLTIMAS 5 LINHAS")
print(df.tail())

# Informações gerais
print_subsection("ℹ️ INFORMAÇÕES GERAIS")
print(df.info())

# Estatísticas descritivas
print_subsection("📈 ESTATÍSTICAS DESCRITIVAS")
print(df.describe())

# ============================================================================
# ANÁLISE DAS COLUNAS
# ============================================================================

print_section("ANÁLISE DETALHADA DAS COLUNAS")

# Tipos de dados
print_subsection("📊 TIPOS DE DADOS")
tipos = df.dtypes.to_frame(name='Tipo')
tipos['Tipo'] = tipos['Tipo'].astype(str)
print(tipos)

# Colunas numéricas e categóricas
colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
colunas_categoricas = df.select_dtypes(include=['object', 'bool']).columns.tolist()

print(f"\n✅ Colunas numéricas ({len(colunas_numericas)}):")
for col in colunas_numericas:
    print(f"   • {col}")

print(f"\n✅ Colunas categóricas ({len(colunas_categoricas)}):")
for col in colunas_categoricas:
    print(f"   • {col}")

# ============================================================================
# VALORES ÚNICOS
# ============================================================================

print_section("VALORES ÚNICOS POR COLUNA")

for col in df.columns:
    n_unicos = df[col].nunique()
    print(f"📌 {col:30s} → {n_unicos:5d} valores únicos")

    # Se for categórica com poucos valores, mostrar quais são
    if n_unicos <= 10 and col != 'State':
        valores = df[col].unique()
        print(f"   Valores: {valores}")

    # Se for a coluna 'State', mostrar os 5 mais frequentes
    if col == 'State':
        top5 = df[col].value_counts().head().to_dict()
        print(f"   Top 5 estados: {top5}")

# ============================================================================
# VALORES FALTANTES
# ============================================================================

print_section("ANÁLISE DE VALORES FALTANTES")

valores_faltantes = df.isnull().sum()
pct_faltantes = (df.isnull().sum() / len(df)) * 100

resumo_faltantes = pd.DataFrame({
    'Coluna': valores_faltantes.index,
    'Valores Faltantes': valores_faltantes.values,
    'Percentual (%)': pct_faltantes.values
})

print(resumo_faltantes[resumo_faltantes['Valores Faltantes'] > 0])

if valores_faltantes.sum() == 0:
    print("✅ EXCELENTE! Não há valores faltantes no dataset.")
else:
    print(f"⚠️  Total de valores faltantes: {valores_faltantes.sum()}")

# ============================================================================
# DUPLICATAS
# ============================================================================

print_section("ANÁLISE DE DUPLICATAS")

duplicatas = df.duplicated().sum()
print(f"🔍 Número de linhas duplicadas: {duplicatas}")

if duplicatas == 0:
    print("✅ Não há linhas duplicadas no dataset.")
else:
    print(f"⚠️  Encontradas {duplicatas} linhas duplicadas.")

# ============================================================================
# ANÁLISE DA VARIÁVEL ALVO (CHURN)
# ============================================================================

print_section("ANÁLISE DA VARIÁVEL ALVO - CHURN")

churn_counts = df['Churn'].value_counts()
churn_pct = df['Churn'].value_counts(normalize=True) * 100

print("📊 Distribuição de Churn:")
print(f"\n   Clientes que PERMANECERAM (False): {churn_counts.get(False, 0):,} ({churn_pct.get(False, 0):.2f}%)")
print(f"   Clientes que SAÍRAM (True):        {churn_counts.get(True, 0):,} ({churn_pct.get(True, 0):.2f}%)")

churn_rate = churn_pct.get(True, 0)
print(f"\n🎯 CHURN RATE: {churn_rate:.2f}%")

if churn_rate < 10:
    print("   📉 Churn baixo - empresa retém bem seus clientes")
elif churn_rate < 20:
    print("   📊 Churn moderado - típico do setor de telecom")
else:
    print("   📈 Churn elevado - requer atenção urgente")

# ============================================================================
# VISUALIZAÇÃO INICIAL - CHURN
# ============================================================================

print_subsection("📊 GERANDO VISUALIZAÇÃO DE CHURN")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico de barras
axes[0].bar(['Permaneceu', 'Saiu'],
            [churn_counts.get(False, 0), churn_counts.get(True, 0)],
            color=[COLORS['churn_no'], COLORS['churn_yes']])
axes[0].set_title('Distribuição de Churn (Contagem)', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Número de Clientes')
axes[0].grid(axis='y', alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate([churn_counts.get(False, 0), churn_counts.get(True, 0)]):
    axes[0].text(i, v + 30, f'{v:,}', ha='center', fontweight='bold')

# Gráfico de pizza
axes[1].pie([churn_counts.get(False, 0), churn_counts.get(True, 0)],
            labels=['Permaneceu', 'Saiu'],
            autopct='%1.1f%%',
            colors=[COLORS['churn_no'], COLORS['churn_yes']],
            startangle=90,
            explode=(0, 0.1))
axes[1].set_title('Proporção de Churn', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/plots/01_distribuicao_churn.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico salvo: outputs/plots/01_distribuicao_churn.png")
plt.close()

# ============================================================================
# SALVAR INFORMAÇÕES DA INSPEÇÃO
# ============================================================================

print_section("SALVANDO RESUMO DA INSPEÇÃO")

# Criar resumo
resumo = {
    'total_registros': len(df),
    'total_colunas': len(df.columns),
    'lista_colunas_numericas': colunas_numericas,
    'lista_colunas_categoricas': colunas_categoricas,
    'colunas_numericas': len(colunas_numericas),
    'colunas_categoricas': len(colunas_categoricas),
    'valores_faltantes': int(valores_faltantes.sum()),
    'duplicatas': int(duplicatas),
    'churn_rate': float(churn_rate),
    'clientes_permaneceram': int(churn_counts.get(False, 0)),
    'clientes_sairam': int(churn_counts.get(True, 0))
}

# Salvar como JSON
with open('outputs/metrics/01_resumo_inspecao.json', 'w') as f:
    json.dump(resumo, f, indent=4)

print("✅ Resumo salvo: outputs/metrics/01_resumo_inspecao.json")

# Salvar DataFrame processado
df.to_csv('data/processed/02_dados_inspecionados.csv', index=False)
print("✅ Dados salvos: data/processed/02_dados_inspecionados.csv")

# Registrar no log
salvar_info_execucao("carregamento_inspecao.py",
                     f"Dados carregados: {len(df)} linhas, Churn Rate: {churn_rate:.2f}%")

print("\n🎉 INSPEÇÃO INICIAL CONCLUÍDA COM SUCESSO!")

# ============================================================================
# FIM DO ARQUIVO 02
# ============================================================================
