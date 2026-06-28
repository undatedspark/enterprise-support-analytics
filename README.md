# ⚡ Enterprise Support Analytics Platform

Plataforma integrada de monitoramento analítico, inteligência estatística, conformidade de SLA e governança de dados para Help Desk corporativo.

Este ecossistema mimetiza uma pipeline de produção real (Data Pipeline ETL), englobando desde a simulação de ingestão de dados brutos até a camada analítica avançada e auditoria de metadados.

---

## 🚀 Arquitetura e Engenharia do Sistema

O projeto foi inteiramente estruturado em **Python**, dividindo-se em frentes de alta engenharia de dados e negócios:

- **Data Ingestion & Cleansing (Pandas):** Algoritmos para tratamento estrito de integridade de dados, conversão de tipos temporais, higienização de strings corrompidas e expurgo automático de registros duplicados.
- **Inteligência Estatística (Machine Learning Proativo):** Aplicação de técnicas de suavização por médias móveis (janelas de 7 e 14 dias) em séries temporais para detecção de tendências de demanda de curto/médio prazo e eliminação de ruídos sazonais.
- **Governança Corporativa de TI (Framework ITIL):** Modelagem de matrizes de decisão para validação de conformidade de SLA (Service Level Agreement), cálculo dinâmico de MTTR (Mean Time to Resolution) e score analítico de satisfação do usuário (CSAT).
- **Interface e Otimização de Memória (UI/UX Streamlit & Plotly):** Layout premium com injeção de CSS customizado, gerenciamento estruturado de estado de sessão (`st.session_state`) e aceleração de performance via cache volátil em memória RAM (`@st.cache_data`).

---

## 📊 Módulos Estruturais do Dashboard

A plataforma é dividida em 4 painéis estratégicos de navegação interna (Tabs):

1. **📈 Operational Dashboard:** Monitoramento contínuo de KPIs vitais da operação, dispersão temporal de incidentes com linhas de tendência de IA e representatividade por canais de entrada (WhatsApp, E-mail, Telefone).
2. **🔥 Matriz de Risco (Heatmap):** Tabela de contingência bidimensional cruzando Categorias de Incidentes vs. Níveis de Severidade para identificar falhas crônicas de infraestrutura que causam impacto financeiro.
3. **🏆 Gestão de Atendentes:** Leaderboard de produtividade e eficiência técnica individual dos analistas de suporte, integrando filtros em conformidade com a LGPD e motor nativo para exportação de relatórios regulatórios (Excel/CSV).
4. **🔍 Governança & Auditoria:** Logs automáticos de qualidade de dados (Data Quality Checks) que monitoram a integridade e o esquema do banco de dados ativo.

---

## 🛠️ Como Executar a Aplicação Localmente

### 1. Pré-requisitos
Certifique-se de ter o Python instalado. Instale as bibliotecas necessárias executando no terminal:
```bash
pip install streamlit pandas plotly openpyxl