from preparacao_ambiente import *
import json

# ============================================================================
# CARREGAMENTO DOS DADOS
# ============================================================================

print_section("CRIAÇÃO DE MÉTRICAS PARA POWER BI")

df = pd.read_csv('data/processed/03_dados_limpos.csv')
print(f"✅ Dados carregados: {len(df):,} linhas")

# Garantir que temos as colunas necessárias
if 'Churn' in df.columns:
    df['Churn_Num'] = df['Churn'].astype(int)
    df['Churn_Label'] = df['Churn'].map({True: 'Saiu', False: 'Permaneceu'})

# ============================================================================
# 1. MÉTRICAS CONSOLIDADAS (KPIs PRINCIPAIS)
# ============================================================================

print_section("1. KPIs PRINCIPAIS PARA DASHBOARD")

# Calcular KPIs gerais
total_clientes = len(df)
total_churners = df['Churn'].sum()
total_ativos = total_clientes - total_churners
taxa_churn = (total_churners / total_clientes) * 100
taxa_retencao = 100 - taxa_churn

# Receitas (baseado em charges)
receita_total_dia = df['Total day charge'].sum()
receita_total_noite = df['Total eve charge'].sum()
receita_total_madrugada = df['Total night charge'].sum()
receita_total_intl = df['Total intl charge'].sum()
receita_total = receita_total_dia + receita_total_noite + receita_total_madrugada + receita_total_intl

# Receita média por cliente
receita_media_cliente = receita_total / total_clientes

# Receita média por churner vs não-churner
receita_media_churner = df[df['Churn'] == True][['Total day charge', 'Total eve charge',
                                                   'Total night charge', 'Total intl charge']].sum(axis=1).mean()
receita_media_ativo = df[df['Churn'] == False][['Total day charge', 'Total eve charge',
                                                  'Total night charge', 'Total intl charge']].sum(axis=1).mean()

# Criar dicionário de KPIs
kpis = {
    'total_clientes': int(total_clientes),
    'total_churners': int(total_churners),
    'total_ativos': int(total_ativos),
    'taxa_churn_%': round(float(taxa_churn), 2),
    'taxa_retencao_%': round(float(taxa_retencao), 2),
    'receita_total': round(float(receita_total), 2),
    'receita_media_cliente': round(float(receita_media_cliente), 2),
    'receita_media_churner': round(float(receita_media_churner), 2),
    'receita_media_ativo': round(float(receita_media_ativo), 2),
    'perda_receita_estimada': round(float(receita_media_churner * total_churners), 2)
}

# Exibir KPIs
print("\n📊 KPIs PRINCIPAIS:")
print(f"   Total de Clientes: {kpis['total_clientes']:,}")
print(f"   Clientes Ativos: {kpis['total_ativos']:,}")
print(f"   Churners: {kpis['total_churners']:,}")
print(f"   Taxa de Churn: {kpis['taxa_churn_%']:.2f}%")
print(f"   Taxa de Retenção: {kpis['taxa_retencao_%']:.2f}%")
print(f"\n💰 MÉTRICAS FINANCEIRAS:")
print(f"   Receita Total: ${kpis['receita_total']:,.2f}")
print(f"   Receita Média/Cliente: ${kpis['receita_media_cliente']:.2f}")
print(f"   Receita Média Churner: ${kpis['receita_media_churner']:.2f}")
print(f"   Receita Média Ativo: ${kpis['receita_media_ativo']:.2f}")
print(f"   Perda Estimada (Churn): ${kpis['perda_receita_estimada']:,.2f}")

# Salvar KPIs
with open('outputs/metrics/12_kpis_dashboard.json', 'w') as f:
    json.dump(kpis, f, indent=4)
print("\n✅ KPIs salvos: outputs/metrics/12_kpis_dashboard.json")

# ============================================================================
# 2. TABELA: ANÁLISE DE RECEITA POR STATUS
# ============================================================================

print_section("2. ANÁLISE DE RECEITA POR STATUS DE CHURN")

# Criar coluna de receita total por cliente
df['Receita_Total_Cliente'] = (df['Total day charge'] + df['Total eve charge'] +
                                 df['Total night charge'] + df['Total intl charge'])

# Agrupar por status de churn
receita_por_status = df.groupby('Churn_Label').agg({
    'Receita_Total_Cliente': ['sum', 'mean', 'median', 'min', 'max'],
    'Churn': 'count'
}).round(2)

receita_por_status.columns = ['Receita_Total', 'Receita_Media', 'Receita_Mediana',
                               'Receita_Min', 'Receita_Max', 'Num_Clientes']

print("\n📊 Receita por Status:")
print(receita_por_status)

# Salvar
receita_por_status.to_csv('outputs/metrics/13_receita_por_status.csv')
print("✅ Tabela salva: outputs/metrics/13_receita_por_status.csv")

# ============================================================================
# 3. TABELA: CHURN POR FAIXA DE RECEITA
# ============================================================================

print_section("3. CHURN POR FAIXA DE RECEITA")

# Criar faixas de receita
df['Faixa_Receita'] = pd.cut(df['Receita_Total_Cliente'],
                              bins=[0, 40, 60, 80, 100, float('inf')],
                              labels=['Muito Baixa (0-40)', 'Baixa (40-60)',
                                      'Média (60-80)', 'Alta (80-100)',
                                      'Muito Alta (100+)'])

# Calcular churn por faixa
churn_por_receita = df.groupby('Faixa_Receita', observed=True).agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)

churn_por_receita.columns = ['Churners', 'Total_Clientes', 'Taxa_Churn']
churn_por_receita['Taxa_Churn_%'] = churn_por_receita['Taxa_Churn'] * 100

print("\n📊 Churn por Faixa de Receita:")
print(churn_por_receita[['Total_Clientes', 'Churners', 'Taxa_Churn_%']].round(2))

# Salvar
churn_por_receita.to_csv('outputs/metrics/14_churn_por_faixa_receita.csv')
print("✅ Tabela salva: outputs/metrics/14_churn_por_faixa_receita.csv")

# ============================================================================
# 4. TABELA: CHURN POR TEMPO DE CONTA (ACCOUNT LENGTH)
# ============================================================================

print_section("4. CHURN POR TEMPO DE CONTA")

# Criar faixas de tempo de conta
df['Faixa_Tempo_Conta'] = pd.cut(df['Account length'],
                                  bins=[0, 50, 100, 150, 200, float('inf')],
                                  labels=['0-50 dias', '51-100 dias',
                                          '101-150 dias', '151-200 dias',
                                          '200+ dias'])

# Calcular churn por faixa
churn_por_tempo = df.groupby('Faixa_Tempo_Conta', observed=True).agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)

churn_por_tempo.columns = ['Churners', 'Total_Clientes', 'Taxa_Churn']
churn_por_tempo['Taxa_Churn_%'] = churn_por_tempo['Taxa_Churn'] * 100

print("\n📊 Churn por Tempo de Conta:")
print(churn_por_tempo[['Total_Clientes', 'Churners', 'Taxa_Churn_%']].round(2))

# Salvar
churn_por_tempo.to_csv('outputs/metrics/15_churn_por_tempo_conta.csv')
print("✅ Tabela salva: outputs/metrics/15_churn_por_tempo_conta.csv")

# ============================================================================
# 5. TABELA: ANÁLISE DE ÁREA CODE (REGION)
# ============================================================================

print_section("5. CHURN POR ÁREA (AREA CODE)")

# Area code representa regiões
churn_por_area = df.groupby('Area code').agg({
    'Churn': ['sum', 'count', 'mean']
}).round(4)

churn_por_area.columns = ['Churners', 'Total_Clientes', 'Taxa_Churn']
churn_por_area['Taxa_Churn_%'] = churn_por_area['Taxa_Churn'] * 100

print("\n📊 Churn por Área (Area Code):")
print(churn_por_area[['Total_Clientes', 'Churners', 'Taxa_Churn_%']].round(2))

# Salvar
churn_por_area.to_csv('outputs/metrics/16_churn_por_area.csv')
print("✅ Tabela salva: outputs/metrics/16_churn_por_area.csv")

# ============================================================================
# 6. TABELA: PERFIL COMPLETO DE CHURNERS
# ============================================================================

print_section("6. PERFIL DETALHADO DOS CHURNERS")

# Selecionar apenas churners
churners = df[df['Churn'] == True].copy()

# Criar resumo estatístico
perfil_churners = {
    'total_churners': len(churners),
    'idade_conta_media': round(churners['Account length'].mean(), 2),
    'chamadas_suporte_media': round(churners['Customer service calls'].mean(), 2),
    'minutos_dia_media': round(churners['Total day minutes'].mean(), 2),
    'receita_media': round(churners['Receita_Total_Cliente'].mean(), 2),
    'pct_com_intl_plan': round((churners['International plan'] == 'Yes').sum() / len(churners) * 100, 2),
    'pct_com_voicemail': round((churners['Voice mail plan'] == 'Yes').sum() / len(churners) * 100, 2),
    'pct_chamadas_4_mais': round((churners['Customer service calls'] >= 4).sum() / len(churners) * 100, 2)
}

print("\n📊 Perfil dos Churners:")
for key, value in perfil_churners.items():
    print(f"   {key}: {value}")

# Salvar perfil
with open('outputs/metrics/17_perfil_churners.json', 'w') as f:
    json.dump(perfil_churners, f, indent=4)
print("\n✅ Perfil salvo: outputs/metrics/17_perfil_churners.json")

# ============================================================================
# 7. TABELA RESUMO: COMPARATIVO PLANOS
# ============================================================================

print_section("7. COMPARATIVO: COMBINAÇÕES DE PLANOS")

# Criar combinações de planos
df['Combo_Planos'] = df['International plan'] + ' / ' + df['Voice mail plan']

# Análise por combinação
combo_analise = df.groupby('Combo_Planos').agg({
    'Churn': ['sum', 'count', 'mean'],
    'Receita_Total_Cliente': 'mean'
}).round(2)

combo_analise.columns = ['Churners', 'Total', 'Taxa_Churn', 'Receita_Media']
combo_analise['Taxa_Churn_%'] = combo_analise['Taxa_Churn'] * 100
combo_analise = combo_analise[['Total', 'Churners', 'Taxa_Churn_%', 'Receita_Media']]

print("\n📊 Análise por Combinação de Planos:")
print(combo_analise)

# Salvar
combo_analise.to_csv('outputs/metrics/18_analise_combo_planos.csv')
print("✅ Tabela salva: outputs/metrics/18_analise_combo_planos.csv")

# ============================================================================
# 8. RESUMO FINAL
# ============================================================================

print_section("RESUMO - MÉTRICAS CRIADAS PARA POWER BI")

print("""
✅ Arquivos criados:

📊 KPIs e Métricas Gerais:
   12_kpis_dashboard.json
   13_receita_por_status.csv
   17_perfil_churners.json

📊 Análises Segmentadas:
   14_churn_por_faixa_receita.csv
   15_churn_por_tempo_conta.csv
   16_churn_por_area.csv
   18_analise_combo_planos.csv

💡 Total: 7 novos arquivos de métricas prontos para Power BI
""")

# Salvar dataset com novas colunas
df_com_features = df.copy()
df_com_features.to_csv('data/processed/04_dados_com_features.csv', index=False)
print("✅ Dataset atualizado salvo: data/processed/04_dados_com_features.csv")

# Registrar no log
salvar_info_execucao("metricas_powerbi.py",
                     "7 arquivos de métricas criados para dashboard")

print("\n🎉 CRIAÇÃO DE MÉTRICAS CONCLUÍDA!")

# ============================================================================
# FIM DO ARQUIVO 05
# ============================================================================
