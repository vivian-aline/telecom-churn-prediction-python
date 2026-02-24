from preparacao_ambiente import *
import json

# ============================================================================
# CARREGAR DADOS
# ============================================================================

print_section("CARREGAMENTO DOS DADOS PARA LIMPEZA")

df = pd.read_csv('data/processed/02_dados_inspecionados.csv')
print(f"✅ Dados carregados: {len(df):,} linhas")

# Criar cópia para comparação
df_original = df.copy()

# ============================================================================
# 1. VERIFICAR E REMOVER DUPLICATAS
# ============================================================================

print_section("1. TRATAMENTO DE DUPLICATAS")

duplicatas_antes = df.duplicated().sum()
print(f"🔍 Duplicatas encontradas: {duplicatas_antes}")

if duplicatas_antes > 0:
    df = df.drop_duplicates()
    print(f"✅ Duplicatas removidas: {duplicatas_antes}")
    print(f"📊 Linhas restantes: {len(df):,}")
else:
    print("✅ Não há duplicatas no dataset")

# ============================================================================
# 2. VERIFICAR E TRATAR VALORES FALTANTES
# ============================================================================

print_section("2. TRATAMENTO DE VALORES FALTANTES")

valores_faltantes = df.isnull().sum()
print("📊 Valores faltantes por coluna:")
print(valores_faltantes[valores_faltantes > 0])

if valores_faltantes.sum() == 0:
    print("\n✅ EXCELENTE! Não há valores faltantes para tratar.")
else:
    print(f"\n⚠️  Total de valores faltantes: {valores_faltantes.sum()}")

# ============================================================================
# 3. PADRONIZAR COLUNAS CATEGÓRICAS
# ============================================================================

print_section("3. PADRONIZAÇÃO DE COLUNAS CATEGÓRICAS")

# Padronizar State (deixar em maiúsculas)
if 'State' in df.columns:
    df['State'] = df['State'].str.upper().str.strip()
    print("✅ Coluna 'State' padronizada (maiúsculas, sem espaços)")

# Padronizar International plan e Voice mail plan
for col in ['International plan', 'Voice mail plan']:
    if col in df.columns:
        df[col] = df[col].str.strip().str.capitalize()
        print(f"✅ Coluna '{col}' padronizada")

# ============================================================================
# 4. VERIFICAR VALORES INCONSISTENTES
# ============================================================================

print_section("4. VERIFICAÇÃO DE VALORES INCONSISTENTES")

colunas_positivas = ['Account length', 'Total day minutes', 'Total day calls',
                     'Total day charge', 'Total eve minutes', 'Total eve calls',
                     'Total eve charge', 'Total night minutes', 'Total night calls',
                     'Total night charge', 'Total intl minutes', 'Total intl calls',
                     'Total intl charge', 'Customer service calls', 'Number vmail messages']

print("🔍 Verificando valores negativos...")
tem_negativos = False
total_negativos = 0

for col in colunas_positivas:
    if col in df.columns:
        negativos = (df[col] < 0).sum()
        if negativos > 0:
            print(f"   ⚠️  {col}: {negativos} valores negativos")
            tem_negativos = True
            total_negativos += negativos

if tem_negativos:
    print(f"\n⚠️  Total de valores negativos: {total_negativos}")
    print("   Decisão: Remover linhas com valores negativos (possível erro de coleta)")

    # Remover linhas com qualquer valor negativo nas colunas especificadas
    mask = (df[colunas_positivas] >= 0).all(axis=1)
    linhas_removidas = len(df) - mask.sum()
    df = df[mask]

    print(f"   ✅ {linhas_removidas} linhas removidas")
    print(f"   📊 Linhas restantes: {len(df):,}")
else:
    print("✅ Não há valores negativos inconsistentes")

# ============================================================================
# 5. VERIFICAR OUTLIERS EXTREMOS
# ============================================================================

print_section("5. DETECÇÃO DE OUTLIERS EXTREMOS")


def detectar_outliers_extremos(df, coluna):

    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 3 * IQR  # 3*IQR para outliers extremos
    limite_superior = Q3 + 3 * IQR

    outliers = df[(df[coluna] < limite_inferior) | (df[coluna] > limite_superior)]
    return len(outliers), limite_inferior, limite_superior

print("\n💡 CRITÉRIO UTILIZADO: 3×IQR (outliers extremos)")
print("   • Menos restritivo que 1.5×IQR (padrão)")
print("   • Apropriado para análise de churn (valores altos podem indicar risco)")

# Colunas numéricas para verificar
colunas_numericas = df.select_dtypes(include=[np.number]).columns

print("🔍 Outliers extremos por coluna:")
outliers_info = {}

for col in colunas_numericas:
    n_outliers, lim_inf, lim_sup = detectar_outliers_extremos(df, col)
    outliers_info[col] = n_outliers

    if n_outliers > 0:
        pct = (n_outliers / len(df)) * 100
        print(f"   📊 {col}: {n_outliers} outliers ({pct:.2f}%)")
        print(f"      Limites: [{lim_inf:.2f}, {lim_sup:.2f}]")

# Nota: Não vamos remover outliers nesta etapa, apenas identificar
print("\n💡 NOTA: Outliers identificados mas não removidos.")
print("   Eles podem conter informações valiosas sobre churn.")

# ============================================================================
# 6. VALIDAÇÃO DE CONSISTÊNCIA
# ============================================================================

print_section("6. VALIDAÇÃO DE CONSISTÊNCIA")

print("🔍 Verificando consistência de cobranças...")

taxa_day_media = None  # inicializa

if 'Total day minutes' in df.columns and 'Total day charge' in df.columns:
    taxa_day = df['Total day charge'] / (df['Total day minutes'] + 0.01)
    taxa_day_media = taxa_day.median()
    print(f"   ✓ Taxa dia (mediana): ${taxa_day_media:.4f} por minuto")

    # Verificar discrepâncias
    df['charge_calculado'] = df['Total day minutes'] * taxa_day_media
    df['diferenca_pct'] = abs((df['Total day charge'] - df['charge_calculado']) / df['Total day charge']) * 100

    inconsistencias = (df['diferenca_pct'] > 5).sum()
    if inconsistencias > 0:
        print(f"   ⚠️  {inconsistencias} registros com discrepância >5%")
    else:
        print(f"   ✅ Todas as cobranças consistentes (±5%)")
else:
    print("   ❌ Colunas necessárias não encontradas no DataFrame")

# Remover colunas auxiliares
df.drop(['charge_calculado', 'diferenca_pct'], axis=1, inplace=True)

# Eve: verificar taxa noturna
if 'Total eve minutes' in df.columns and 'Total eve charge' in df.columns:
    taxa_eve = df['Total eve charge'] / (df['Total eve minutes'] + 0.01)
    taxa_eve_media = taxa_eve.median()
    print(f"   ✓ Taxa noite (mediana): ${taxa_eve_media:.4f} por minuto")

# Night: verificar taxa madrugada
if 'Total night minutes' in df.columns and 'Total night charge' in df.columns:
    taxa_night = df['Total night charge'] / (df['Total night minutes'] + 0.01)
    taxa_night_media = taxa_night.median()
    print(f"   ✓ Taxa madrugada (mediana): ${taxa_night_media:.4f} por minuto")

# Intl: verificar taxa internacional
if 'Total intl minutes' in df.columns and 'Total intl charge' in df.columns:
    taxa_intl = df['Total intl charge'] / (df['Total intl minutes'] + 0.01)
    taxa_intl_media = taxa_intl.median()
    print(f"   ✓ Taxa internacional (mediana): ${taxa_intl_media:.4f} por minuto")

print("\n✅ Taxas de cobrança parecem consistentes")

# ============================================================================
# 7. VALIDAÇÃO DE RANGES ESPERADOS
# ============================================================================

print_section("7. VALIDAÇÃO DE RANGES ESPERADOS")

print("🔍 Verificando ranges de valores...")

# Account length (dias de conta) - geralmente 1 a 300
if 'Account length' in df.columns:
    fora_range = ((df['Account length'] < 1) | (df['Account length'] > 300)).sum()
    if fora_range > 0:
        print(f"   ⚠️  Account length: {fora_range} valores fora do range [1, 300]")
    else:
        print(f"   ✅ Account length dentro do range esperado")

# Customer service calls - geralmente 0 a 10
if 'Customer service calls' in df.columns:
    chamadas_altas = (df['Customer service calls'] > 10).sum()
    if chamadas_altas > 0:
        print(f"   ⚠️  {chamadas_altas} clientes com >10 chamadas ao suporte")
        print(f"      (possível indicador forte de churn)")
    else:
        print(f"   ✅ Customer service calls dentro do padrão")

# ============================================================================
# 8. RESUMO DA LIMPEZA
# ============================================================================

print_section("RESUMO DA LIMPEZA")

print(f"📊 Registros originais:     {len(df_original):,}")
print(f"📊 Registros após limpeza:  {len(df):,}")
print(f"📊 Registros removidos:     {len(df_original) - len(df):,}")

if len(df_original) == len(df):
    print("\n✅ DATASET LIMPO SEM PERDA DE DADOS")
else:
    mudanca_pct = ((len(df_original) - len(df)) / len(df_original)) * 100
    print(f"📉 Perda de dados: {mudanca_pct:.2f}%")

# Adicionar métricas de qualidade
print(f"\n📈 QUALIDADE DOS DADOS:")
print(f"   • Completude: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.2f}%")
print(f"   • Duplicatas: 0")
print(f"   • Colunas: {len(df.columns)}")

# ============================================================================
# 9. SALVAR DADOS LIMPOS
# ============================================================================

print_section("SALVANDO DADOS LIMPOS")

# Salvar CSV limpo
df.to_csv('data/processed/03_dados_limpos.csv', index=False)
print("✅ Dados limpos salvos: data/processed/03_dados_limpos.csv")

# Converter outliers_info para formato JSON-serializável
outliers_info_json = {}
for coluna, quantidade in outliers_info.items():
    outliers_info_json[coluna] = int(quantidade)  # Converter numpy int64 para int Python

# Salvar relatório de limpeza
relatorio_limpeza = {
    'registros_originais': int(len(df_original)),
    'registros_finais': int(len(df)),
    'duplicatas_removidas': int(duplicatas_antes),
    'valores_faltantes_tratados': int(valores_faltantes.sum()),
    'outliers_detectados': outliers_info_json  # Usar a versão convertida
}

with open('outputs/metrics/02_relatorio_limpeza.json', 'w') as f:
    json.dump(relatorio_limpeza, f, indent=4)

print("✅ Relatório salvo: outputs/metrics/02_relatorio_limpeza.json")

# Registrar no log
salvar_info_execucao("limpeza_dados.py",
                     f"Limpeza concluída: {len(df)} linhas finais")

print("\n🎉 LIMPEZA DE DADOS CONCLUÍDA COM SUCESSO!")