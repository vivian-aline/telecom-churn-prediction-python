# Análise Churn Telecom: Identificação de Clientes de Alto Risco

Análise exploratória completa de 2.666 clientes telecom para identificar padrões de churn (cancelamento) e criar segmentação de risco acionável.

Projeto desenvolvido individualmente como parte do meu portfólio para Analista de Dados Pleno, com Pycharm (Python) e Power BI (11 tabelas KPIs).

---

## 1. Problema de Negócio

Operadora telecom precisa reduzir churn de 14.6% identificando clientes de risco:

**Principais achados:**
- **Plano Internacional**: 43.7% churn vs 11.3% (4x maior!)
- **4+ chamadas suporte**: 52.9% churn (ponto de inflexão)
- **Voice Mail**: PROTEGE (8.9% churn vs 16.7%)
- **22 clientes Alto Risco**: 68% churn → prioridade máxima

**Perguntas centrais:**
> 1. Quais planos e comportamentos causam mais churn?  
> 2. Como segmentar clientes por risco (Baixo/Médio/Alto)?  
> 3. Qual impacto financeiro de reduzir churn nos 22 de alto risco?

---

## 2. Dados Utilizados

**Dataset Kaggle Telecom Churn** (80% treino): 2.666 registros, 20 variáveis.

| Categoria | Variáveis principais | Exemplo |
|-----------|---------------------|---------|
| **Perfil** | State, Account length, Area code | WV (88 clientes), 100 meses médio |
| **Planos** | International plan, Voice mail plan | 10% com plano intl, 27% voice mail |
| **Uso Diurno** | Total day minutes, calls, charge | 179 min/dia, R$ 30,51 charge |
| **Uso Noturno** | Total night minutes, calls, charge | 201 min/noite |
| **Internacional** | Total intl minutes, calls, charge | 10 min/mês |
| **Suporte** | Customer service calls | 1,56 chamadas/mês médio |
| **Target** | Churn (False/True) | 14,6% churn geral

**Qualidade:** Dataset limpo, sem duplicatas/nulos significativos.

**Stack técnica:**
- **Pycharm Python**: pandas, numpy, matplotlib, seaborn
- **Estrutura**: 5 scripts modulares + pastas organizadas
- **BI**: 11 CSVs exportados para Power BI

---

## 3. Metodologia (Pipeline Python Modular)

**Estrutura executada sequencialmente:**

| Script | Função | Saídas |
|--------|--------|--------|
| `01_preparacao_ambiente.py` | Bibliotecas + pastas | 7 pastas criadas |
| `02_carregamento_inspecao.py` | Load + EDA inicial | `outputs/metrics/01_resumo.json` |
| `03_limpeza_dados.py` | Duplicatas + padronização | `data/processed/03_dados_limpos.csv` |
| `04_eda_exploratoria.py` | **Análises completas** | 11 gráficos + 9 tabelas KPIs |
| `05_metricas_powerbi.py` | **KPIs para dashboard** | `data/dashboard/telecom_churn_completo.csv`

**Estrutura de pastas:**

.
├── data/
│   ├── raw/            
│   ├── clean/       
│   └── feature/             
├── notebooks/
│   ├── carregamento_inspecao.py
│   ├── preparacao_ambiente.py
│   ├── limpeza_dados.py
│   ├── eda_exploratoria.py
│   └── metricas_powerbi.py
├── dashboard/
│   └── dashboard_churn_telecom.pdf
└── README.md

---

## 4. Principais Insights (Nível Sênior)

### **4.1. Fatores Críticos de Churn**
| Fator | Churn % | Benchmark Mercado | Insight |
|-------|---------|-------------------|---------|
| **Plano Internacional** | **43.7%** | 40-71% | **4x maior** que plano básico (11.3%) |
| **4 chamadas suporte** | **52.9%** | ~50% | Ponto de inflexão: 0-3 chamadas = 10% |
| **Voice Mail Plan** | **8.9%** | - | **Protege**: reduz 47% churn |
| **8-9 chamadas suporte** | **100%** | - | Clientes já perdidos

### **4.2. Segmentação de Risco (Criada por mim)**
| Segmento | Clientes | Churn % | Critério |
|----------|----------|---------|----------|
| **Alto** | **22** | **68.2%** | Intl Plan + 4+ chamadas |
| **Médio** | **750** | **29.7%** | Intl Plan OU 3+ chamadas |
| **Baixo** | **1.894** | **7.9%** | Sem fatores risco

### **4.3. Correlações com Churn**

**Customer service calls**: +0.203 ⭐ TOP 1
**Total day charge**: +0.196
**Total day minutes**: +0.196
**Voice mail messages: -0.09** (proteção)

### **4.4. Estados Críticos (Top 10 churn)**
| Estado | Taxa Churn | Clientes |
|--------|------------|----------|
| **TX** | **29.1%** | 55 |
| **NJ** | **28.0%** | 50 |
| **AR** | **23.4%** | 47

---

## 5. Impacto Financeiro & Recomendações

**Se focar nos 22 Alto Risco e reduzir churn de 68% para 30%:**

**Clientes salvos**: 8
**Impacto ARPU alto (Intl + suporte)**: R$ 1.200/cliente/mês
**Receita anual preservada**: R$ 115.200

**Ações prioritárias:**
1. **Alerta 3 chamadas**: Intervenção gerente (churn cai 41%)
2. **Revisar Plano Intl**: Downsell para clientes subutilizando
3. **Voice Mail grátis**: 3 meses para novos (retenção +47%)
4. **Campanha Alto Risco**: 22 clientes personalizados

*Desenvolvido por Vivian Aline Inoue | Nov/2025*
