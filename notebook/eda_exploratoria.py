from preparacao_ambiente import *
import json

# ============================================================================
# 1. CARREGAMENTO DOS DADOS LIMPOS
# ============================================================================

print_section("ANÁLISE EXPLORATÓRIA DE DADOS (EDA)")

df = pd.read_csv('data/processed/03_dados_limpos.csv')
print(f"✅ Dados limpos carregados: {len(df):,} linhas × {df.shape[1]} colunas")

# Converter Churn para valores mais descritivos para visualização
df['Churn_Label'] = df['Churn'].map({True: 'Saiu', False: 'Permaneceu'})

# Separar colunas por tipo
colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
colunas_categoricas = ['State', 'International plan', 'Voice mail plan', 'Churn', 'Churn_Label']

print(f"\n📊 Colunas numéricas: {len(colunas_numericas)}")
print(f"📊 Colunas categóricas: {len(colunas_categoricas)}")

# ============================================================================
# 2. ANÁLISE UNIVARIADA - DISTRIBUIÇÕES
# ============================================================================

print_section("2. ANÁLISE UNIVARIADA - DISTRIBUIÇÕES")

# 2.1 Variáveis Numéricas - Estatísticas
print_subsection("2.1 Estatísticas Descritivas das Variáveis Numéricas")

stats_numericas = df[colunas_numericas].describe().T
stats_numericas['CV'] = (stats_numericas['std'] / stats_numericas['mean']) * 100  # Coeficiente de Variação

print(stats_numericas[['mean', 'std', 'min', 'max', 'CV']].round(2))

# Salvar estatísticas
stats_numericas.to_csv('outputs/metrics/03_estatisticas_numericas.csv')
print("\n✅ Estatísticas salvas em: outputs/metrics/03_estatisticas_numericas.csv")

# 2.2 Visualizar distribuições das principais variáveis numéricas
print_subsection("2.2 Distribuições das Variáveis Numéricas")

# Selecionar principais variáveis para visualizar
variaveis_principais = [
    'Account length',
    'Total day minutes',
    'Total eve minutes',
    'Total night minutes',
    'Total intl minutes',
    'Customer service calls'
]

# Criar subplots para histogramas
fig, axes = plt.subplots(3, 2, figsize=(15, 12))
axes = axes.ravel()

for idx, col in enumerate(variaveis_principais):
    if col in df.columns:
        axes[idx].hist(df[col], bins=30, color=COLORS['primary'], alpha=0.7, edgecolor='black')
        axes[idx].set_title(f'Distribuição: {col}', fontweight='bold')
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel('Frequência')
        axes[idx].grid(axis='y', alpha=0.3)

        # Adicionar linha da média
        media = df[col].mean()
        axes[idx].axvline(media, color='red', linestyle='--', linewidth=2, label=f'Média: {media:.1f}')
        axes[idx].legend()

plt.tight_layout()
plt.savefig('outputs/plots/02_distribuicoes_univariadas.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/02_distribuicoes_univariadas.png")
plt.close()

# 2.3 Análise de variáveis categóricas
print_subsection("2.3 Distribuição das Variáveis Categóricas")

# International Plan
print("📊 International Plan:")
print(df['International plan'].value_counts())
print(f"   Percentual: {(df['International plan'].value_counts(normalize=True) * 100).round(2).to_dict()}")

# Voice Mail Plan
print("\n📊 Voice Mail Plan:")
print(df['Voice mail plan'].value_counts())
print(f"   Percentual: {(df['Voice mail plan'].value_counts(normalize=True) * 100).round(2).to_dict()}")

# Top 10 Estados
print("\n📊 Top 10 Estados com mais clientes:")
print(df['State'].value_counts().head(10))

# ============================================================================
# 3. ANÁLISE BIVARIADA - RELAÇÃO COM CHURN
# ============================================================================

print_section("3. ANÁLISE BIVARIADA - RELAÇÃO COM CHURN")

# 3.1 Taxa de Churn por Plano Internacional
print_subsection("3.1 Churn por International Plan")

churn_intl = pd.crosstab(df['International plan'], df['Churn'], normalize='index') * 100
print("\nTaxa de Churn (%):")
print(churn_intl.round(2))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
churn_intl_count = pd.crosstab(df['International plan'], df['Churn_Label'])
churn_intl_count.plot(kind='bar', ax=ax, color=[COLORS['churn_no'], COLORS['churn_yes']])
ax.set_title('Churn por International Plan', fontsize=14, fontweight='bold')
ax.set_xlabel('International Plan')
ax.set_ylabel('Número de Clientes')
ax.legend(title='Status')
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('outputs/plots/03_churn_international_plan.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/03_churn_international_plan.png")
plt.close()

# 3.2 Taxa de Churn por Voice Mail Plan
print_subsection("3.2 Churn por Voice Mail Plan")

churn_vmail = pd.crosstab(df['Voice mail plan'], df['Churn'], normalize='index') * 100
print("\nTaxa de Churn (%):")
print(churn_vmail.round(2))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
churn_vmail_count = pd.crosstab(df['Voice mail plan'], df['Churn_Label'])
churn_vmail_count.plot(kind='bar', ax=ax, color=[COLORS['churn_no'], COLORS['churn_yes']])
ax.set_title('Churn por Voice Mail Plan', fontsize=14, fontweight='bold')
ax.set_xlabel('Voice Mail Plan')
ax.set_ylabel('Número de Clientes')
ax.legend(title='Status')
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('outputs/plots/04_churn_voicemail_plan.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/04_churn_voicemail_plan.png")
plt.close()

# 3.3 Churn por Customer Service Calls
print_subsection("3.3 Churn por Customer Service Calls")

churn_cs = pd.crosstab(df['Customer service calls'], df['Churn'], normalize='index') * 100
print("\nTaxa de Churn por número de chamadas (%):")
print(churn_cs.round(2))

# Visualização
fig, ax = plt.subplots(figsize=(12, 6))
churn_cs_count = pd.crosstab(df['Customer service calls'], df['Churn_Label'])
churn_cs_count.plot(kind='bar', ax=ax, color=[COLORS['churn_no'], COLORS['churn_yes']], width=0.8)
ax.set_title('Churn por Número de Chamadas ao Suporte', fontsize=14, fontweight='bold')
ax.set_xlabel('Número de Chamadas')
ax.set_ylabel('Número de Clientes')
ax.legend(title='Status')
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('outputs/plots/05_churn_customer_service.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/05_churn_customer_service.png")
plt.close()

# Insight importante
chamadas_altas = df[df['Customer service calls'] >= 4]['Churn'].mean() * 100
chamadas_baixas = df[df['Customer service calls'] < 4]['Churn'].mean() * 100
print(f"\n💡 INSIGHT: Clientes com ≥4 chamadas têm {chamadas_altas:.1f}% de churn")
print(f"            Clientes com <4 chamadas têm {chamadas_baixas:.1f}% de churn")

# ============================================================================
# 4. ANÁLISE DE CORRELAÇÕES
# ============================================================================

print_section("4. ANÁLISE DE CORRELAÇÕES")

# 4.1 Converter Churn para numérico (0 e 1) para correlação
df['Churn_Num'] = df['Churn'].astype(int)

# 4.2 Selecionar apenas colunas numéricas relevantes
colunas_para_correlacao = [
    'Account length',
    'Number vmail messages',
    'Total day minutes',
    'Total day calls',
    'Total day charge',
    'Total eve minutes',
    'Total eve calls',
    'Total eve charge',
    'Total night minutes',
    'Total night calls',
    'Total night charge',
    'Total intl minutes',
    'Total intl calls',
    'Total intl charge',
    'Customer service calls',
    'Churn_Num'
]

# Filtrar apenas colunas que existem
colunas_existentes = [col for col in colunas_para_correlacao if col in df.columns]

# 4.3 Calcular matriz de correlação
print_subsection("4.1 Matriz de Correlação")

correlacao = df[colunas_existentes].corr()

# Mostrar correlações com Churn (ordenadas)
corr_churn = correlacao['Churn_Num'].sort_values(ascending=False)
print("\n📊 Correlação das variáveis com CHURN:")
print(corr_churn.round(3))

# Salvar correlações
corr_churn.to_csv('outputs/metrics/04_correlacoes_churn.csv', header=['Correlacao'])
print("\n✅ Correlações salvas em: outputs/metrics/04_correlacoes_churn.csv")

# 4.4 Heatmap de Correlação
print_subsection("4.2 Heatmap de Correlação")

# Criar heatmap focado (apenas variáveis mais relevantes)
variaveis_heatmap = [
    'Total day minutes',
    'Total day charge',
    'Total eve minutes',
    'Total eve charge',
    'Total intl minutes',
    'Total intl charge',
    'Customer service calls',
    'Churn_Num'
]

# Filtrar apenas existentes
variaveis_heatmap_existentes = [col for col in variaveis_heatmap if col in df.columns]

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(df[variaveis_heatmap_existentes].corr(),
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax)
ax.set_title('Matriz de Correlação - Principais Variáveis', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/plots/06_heatmap_correlacao.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/06_heatmap_correlacao.png")
plt.close()

# 4.5 Identificar correlações importantes
print_subsection("4.3 Insights de Correlação")

# Correlações altas com Churn (excluindo o próprio Churn)
corr_alta = corr_churn[corr_churn.abs() > 0.1].drop('Churn_Num', errors='ignore')

if len(corr_alta) > 0:
    print("\n💡 Variáveis com correlação moderada/alta com Churn (>0.1):")
    for var, valor in corr_alta.items():
        direcao = "positiva" if valor > 0 else "negativa"
        print(f"   • {var}: {valor:.3f} ({direcao})")
else:
    print("\n💡 Não há correlações lineares fortes com Churn")
    print("   (Isso é comum - churn pode depender de combinações de fatores)")

# ============================================================================
# 5. COMPARAÇÃO: CHURNERS vs NÃO-CHURNERS
# ============================================================================

print_section("5. COMPARAÇÃO: CHURNERS vs NÃO-CHURNERS")

# 5.1 Estatísticas comparativas
print_subsection("5.1 Médias por Grupo")

# Comparar médias das principais variáveis
variaveis_comparacao = [
    'Account length',
    'Total day minutes',
    'Total eve minutes',
    'Total night minutes',
    'Total intl minutes',
    'Customer service calls',
    'Total day charge',
    'Number vmail messages'
]

# Filtrar existentes
variaveis_comp_existentes = [col for col in variaveis_comparacao if col in df.columns]

# Criar tabela comparativa
comparacao = df.groupby('Churn_Label')[variaveis_comp_existentes].mean().T
comparacao['Diferenca'] = comparacao['Saiu'] - comparacao['Permaneceu']
comparacao['Diferenca_%'] = (comparacao['Diferenca'] / comparacao['Permaneceu']) * 100

print("\n📊 Comparação de Médias:")
print(comparacao.round(2))

# Salvar comparação
comparacao.to_csv('outputs/metrics/05_comparacao_churners.csv')
print("\n✅ Comparação salva em: outputs/metrics/05_comparacao_churners.csv")

# 5.2 Insights principais
print_subsection("5.2 Principais Diferenças")

# Encontrar maiores diferenças percentuais
maiores_diferencas = comparacao['Diferenca_%'].abs().sort_values(ascending=False).head(5)

print("\n💡 TOP 5 Maiores Diferenças entre Churners e Não-Churners:")
for var, diff in maiores_diferencas.items():
    valor_churn = comparacao.loc[var, 'Saiu']
    valor_nao_churn = comparacao.loc[var, 'Permaneceu']

    if comparacao.loc[var, 'Diferenca'] > 0:
        print(f"\n   • {var}:")
        print(f"     Churners: {valor_churn:.2f} | Não-Churners: {valor_nao_churn:.2f}")
        print(f"     Churners têm {abs(diff):.1f}% A MAIS")
    else:
        print(f"\n   • {var}:")
        print(f"     Churners: {valor_churn:.2f} | Não-Churners: {valor_nao_churn:.2f}")
        print(f"     Churners têm {abs(diff):.1f}% A MENOS")

# 5.3 Boxplots comparativos
print_subsection("5.3 Boxplots Comparativos")

# Selecionar 6 variáveis mais importantes para boxplot
variaveis_boxplot = [
    'Total day minutes',
    'Total eve minutes',
    'Total intl minutes',
    'Customer service calls',
    'Total day charge',
    'Number vmail messages'
]

# Filtrar existentes
variaveis_box_existentes = [col for col in variaveis_boxplot if col in df.columns]

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.ravel()

for idx, col in enumerate(variaveis_box_existentes):
    # Boxplot
    df.boxplot(column=col, by='Churn_Label', ax=axes[idx],
               patch_artist=True,
               boxprops=dict(facecolor=COLORS['primary'], alpha=0.6),
               medianprops=dict(color='red', linewidth=2))

    axes[idx].set_title(f'{col}', fontweight='bold', fontsize=11)
    axes[idx].set_xlabel('')
    axes[idx].set_ylabel(col, fontsize=9)
    axes[idx].grid(axis='y', alpha=0.3)

    # Remover título automático do pandas
    plt.suptitle('')

plt.tight_layout()
plt.savefig('outputs/plots/07_boxplots_comparacao.png', dpi=300, bbox_inches='tight')
print("✅ Gráfico salvo: outputs/plots/07_boxplots_comparacao.png")
plt.close()

# ============================================================================
# 6. ANÁLISE DE SEGMENTOS E PADRÕES
# ============================================================================

print_section("6. ANÁLISE DE SEGMENTOS E PADRÕES")

# 6.1 Criar segmentos de risco
print_subsection("6.1 Segmentação de Clientes por Risco de Churn")

# Definir critérios de risco
df['Risco_Churn'] = 'Baixo'

# Risco Médio: International plan = Yes OU Customer service calls >= 3
condicao_medio = (
    (df['International plan'] == 'Yes') |
    (df['Customer service calls'] >= 3)
)
df.loc[condicao_medio, 'Risco_Churn'] = 'Médio'

# Risco Alto: International plan = Yes E Customer service calls >= 4
condicao_alto = (
    (df['International plan'] == 'Yes') &
    (df['Customer service calls'] >= 4)
)
df.loc[condicao_alto, 'Risco_Churn'] = 'Alto'

# Distribuição por segmento
print("\n📊 Distribuição de Clientes por Risco:")
print(df['Risco_Churn'].value_counts().sort_index())

# Taxa de churn por segmento
print("\n📊 Taxa de Churn por Segmento de Risco:")
churn_por_risco = df.groupby('Risco_Churn')['Churn'].agg(['sum', 'count', 'mean'])
churn_por_risco.columns = ['Churners', 'Total', 'Taxa_Churn']
churn_por_risco['Taxa_Churn_%'] = churn_por_risco['Taxa_Churn'] * 100
print(churn_por_risco[['Churners', 'Total', 'Taxa_Churn_%']].round(2))

# Visualização
fig, ax = plt.subplots(figsize=(10, 6))
churn_risco = pd.crosstab(df['Risco_Churn'], df['Churn_Label'])
churn_risco = churn_risco.reindex(['Baixo', 'Médio', 'Alto'])  # Ordenar
churn_risco.plot(kind='bar', ax=ax, color=[COLORS['churn_no'], COLORS['churn_yes']], width=0.7)
ax.set_title('Churn por Segmento de Risco', fontsize=14, fontweight='bold')
ax.set_xlabel('Segmento de Risco')
ax.set_ylabel('Número de Clientes')
ax.legend(title='Status')
ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('outputs/plots/08_churn_segmento_risco.png', dpi=300, bbox_inches='tight')
print("\n✅ Gráfico salvo: outputs/plots/08_churn_segmento_risco.png")
plt.close()

# 6.2 Top Estados com maior churn
print_subsection("6.2 Top 10 Estados com Maior Taxa de Churn")

churn_por_estado = df.groupby('State').agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)

churn_por_estado.columns = ['Churners', 'Total_Clientes', 'Taxa_Churn']
churn_por_estado['Taxa_Churn_%'] = churn_por_estado['Taxa_Churn'] * 100

# Filtrar estados com pelo menos 10 clientes
churn_por_estado_filtrado = churn_por_estado[churn_por_estado['Total_Clientes'] >= 10]
top10_estados = churn_por_estado_filtrado.nlargest(10, 'Taxa_Churn_%')

print(top10_estados[['Total_Clientes', 'Churners', 'Taxa_Churn_%']].round(2))

# Salvar análise por estado
churn_por_estado.sort_values('Taxa_Churn_%', ascending=False).to_csv('outputs/metrics/06_churn_por_estado.csv')
print("\n✅ Análise por estado salva: outputs/metrics/06_churn_por_estado.csv")

# ============================================================================
# 7. RESUMO DE INSIGHTS PARA POWER BI
# ============================================================================

print_section("7. PREPARAÇÃO DE DADOS PARA POWER BI")

# 7.1 Criar dataset agregado para dashboard
print_subsection("7.1 Criando Tabelas Agregadas")

import json

# Tabela 1: Métricas gerais
metricas_gerais = {
    'total_clientes': int(len(df)),
    'total_churners': int(df['Churn'].sum()),
    'taxa_churn_%': float(df['Churn'].mean() * 100),
    'clientes_intl_plan': int((df['International plan'] == 'Yes').sum()),
    'clientes_voicemail': int((df['Voice mail plan'] == 'Yes').sum()),
    'media_customer_service_calls': float(df['Customer service calls'].mean()),
    'media_total_day_minutes': float(df['Total day minutes'].mean()),
    'media_total_day_charge': float(df['Total day charge'].mean())
}

# Salvar métricas gerais
with open('outputs/metrics/07_metricas_gerais.json', 'w') as f:
    json.dump(metricas_gerais, f, indent=4)

print("✅ Métricas gerais salvas: outputs/metrics/07_metricas_gerais.json")

# Tabela 2: Churn por International Plan
churn_intl_plan = df.groupby('International plan').agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)
churn_intl_plan.columns = ['Churners', 'Total', 'Taxa_Churn']
churn_intl_plan['Taxa_Churn_%'] = churn_intl_plan['Taxa_Churn'] * 100
churn_intl_plan.to_csv('outputs/metrics/08_churn_international_plan.csv')
print("✅ Churn por International Plan: outputs/metrics/08_churn_international_plan.csv")

# Tabela 3: Churn por Voice Mail Plan
churn_vmail_plan = df.groupby('Voice mail plan').agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)
churn_vmail_plan.columns = ['Churners', 'Total', 'Taxa_Churn']
churn_vmail_plan['Taxa_Churn_%'] = churn_vmail_plan['Taxa_Churn'] * 100
churn_vmail_plan.to_csv('outputs/metrics/09_churn_voicemail_plan.csv')
print("✅ Churn por Voice Mail Plan: outputs/metrics/09_churn_voicemail_plan.csv")

# Tabela 4: Churn por Customer Service Calls
churn_cs_calls = df.groupby('Customer service calls').agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)
churn_cs_calls.columns = ['Churners', 'Total', 'Taxa_Churn']
churn_cs_calls['Taxa_Churn_%'] = churn_cs_calls['Taxa_Churn'] * 100
churn_cs_calls.to_csv('outputs/metrics/10_churn_customer_service.csv')
print("✅ Churn por Customer Service Calls: outputs/metrics/10_churn_customer_service.csv")

# Tabela 5: Segmentação de risco
churn_por_risco.to_csv('outputs/metrics/11_churn_segmento_risco.csv')
print("✅ Churn por Segmento de Risco: outputs/metrics/11_churn_segmento_risco.csv")

# 7.2 Dataset principal com segmentação para Power BI
df_powerbi = df.copy()
df_powerbi.to_csv('data/dashboard/telecom_churn_completo.csv', index=False)
print("\n✅ Dataset completo para Power BI: data/dashboard/telecom_churn_completo.csv")

# ============================================================================
# 8. RESUMO FINAL DA EDA
# ============================================================================

print_section("RESUMO FINAL DA ANÁLISE EXPLORATÓRIA")

print("📊 PRINCIPAIS INSIGHTS ENCONTRADOS:\n")

print("1️⃣  INTERNATIONAL PLAN:")
taxa_intl_yes = df[df['International plan'] == 'Yes']['Churn'].mean() * 100
taxa_intl_no = df[df['International plan'] == 'No']['Churn'].mean() * 100
print(f"   • Clientes com plano internacional: {taxa_intl_yes:.1f}% de churn")
print(f"   • Clientes sem plano internacional: {taxa_intl_no:.1f}% de churn")
print(f"   • Diferença: {taxa_intl_yes - taxa_intl_no:.1f} pontos percentuais")

print("\n2️⃣  CUSTOMER SERVICE CALLS:")
taxa_cs_alto = df[df['Customer service calls'] >= 4]['Churn'].mean() * 100
taxa_cs_baixo = df[df['Customer service calls'] < 4]['Churn'].mean() * 100
print(f"   • ≥4 chamadas ao suporte: {taxa_cs_alto:.1f}% de churn")
print(f"   • <4 chamadas ao suporte: {taxa_cs_baixo:.1f}% de churn")
print(f"   • Diferença: {taxa_cs_alto - taxa_cs_baixo:.1f} pontos percentuais")

print("\n3️⃣  VOICE MAIL PLAN:")
taxa_vm_yes = df[df['Voice mail plan'] == 'Yes']['Churn'].mean() * 100
taxa_vm_no = df[df['Voice mail plan'] == 'No']['Churn'].mean() * 100
print(f"   • Clientes com voice mail: {taxa_vm_yes:.1f}% de churn")
print(f"   • Clientes sem voice mail: {taxa_vm_no:.1f}% de churn")
print(f"   • Diferença: {abs(taxa_vm_yes - taxa_vm_no):.1f} pontos percentuais")

print("\n4️⃣  SEGMENTAÇÃO DE RISCO:")
for risco in ['Baixo', 'Médio', 'Alto']:
    if risco in churn_por_risco.index:
        taxa = churn_por_risco.loc[risco, 'Taxa_Churn_%']
        total = churn_por_risco.loc[risco, 'Total']
        print(f"   • Risco {risco}: {taxa:.1f}% de churn ({total} clientes)")

print("\n" + "="*80)
print("✅ ANÁLISE EXPLORATÓRIA CONCLUÍDA COM SUCESSO!")
print("="*80)

# Registrar no log
salvar_info_execucao("eda_exploratoria.py",
                     f"EDA concluída - {len(df)} registros analisados")

# ============================================================================
# FIM DO ARQUIVO 04
# ============================================================================
