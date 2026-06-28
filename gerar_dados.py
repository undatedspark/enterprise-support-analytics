import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

# Inicializa o gerador de dados fictícios
fake = Faker('pt_BR')
Faker.seed(42)
random.seed(42)

num_chamados = 1000

# Listas de apoio para consistência dos dados
canais = ['WhatsApp', 'E-mail', 'Portal de TI', 'Telefone']
status_lista = ['Em andamento', 'Resolvido', 'Fechado', 'Reaberto']
categorias = {
    'Redes': ['Wi-Fi instável', 'Cabo de rede desconectado', 'Lentidão na VPN'],
    'Hardware': ['Computador não liga', 'Impressora travada', 'Teclado com defeito'],
    'Software/ERP': ['Erro ao emitir nota', 'Acesso negado no sistema', 'Instalação de software'],
    'Acessos': ['Reset de senha AD', 'Permissão de pasta em rede', 'Criar novo usuário']
}
tecnicos = ['Ana Silva', 'Bruno Costa', 'Carlos Souza', 'Daniela Lima']
departamentos = ['RH', 'Financeiro', 'Comercial', 'Logística', 'Operações']

dados = []

for i in range(1, num_chamados + 1):
    id_chamado = f"CH{i:05d}"
    
    # Datas de abertura (simulando os últimos 60 dias)
    data_abertura = fake.date_time_between(start_date='-60d', end_date='now')
    
    # Definição do status (Distribuído de forma realista)
    status = random.choices(status_lista, weights=[15, 55, 25, 5], k=1)[0]
    
    # Definição da prioridade (Garante que todo chamado tenha uma)
    prioridade = random.choices(['Baixa', 'Média', 'Alta', 'Crítica'], weights=[40, 40, 15, 5], k=1)[0]
    
    # Lógica de negócio baseada no Status
    if status == 'Em andamento':
        data_fechamento = None
        tempo_resolucao = None
        dentro_sla = "Pendente"
        nota_csat = None
    else:
        # Resolvidos, Fechados ou Reabertos possuem tempo de resolução e fechamento
        horas_resolucao = round(random.uniform(0.5, 48), 1)
        data_fechamento = data_abertura + timedelta(hours=horas_resolucao)
        tempo_resolucao = horas_resolucao
        
        # Regra de negócio para o SLA (Alta/Crítica precisam ser resolvidas rápido)
        limite_sla = 4 if prioridade in ['Alta', 'Crítica'] else 24
        dentro_sla = "Sim" if horas_resolucao <= limite_sla else "Não"
        
        # Nota de satisfação do usuário (CSAT) de 1 a 5
        nota_csat = random.choices([5, 4, 3, 2, 1], weights=[60, 25, 8, 4, 3], k=1)[0]

    # Escolha da categoria e subcategoria de TI
    cat_escolhida = random.choice(list(categorias.keys()))
    subcat_escolhida = random.choice(categorias[cat_escolhida])

    dados.append({
        'ID_Chamado': id_chamado,
        'Usuario': fake.name(),
        'Departamento': random.choice(departamentos),
        'Data_Abertura': data_abertura.strftime('%Y-%m-%d %H:%M:%S'),
        'Data_Fechamento': data_fechamento.strftime('%Y-%m-%d %H:%M:%S') if data_fechamento else '',
        'Categoria': cat_escolhida,
        'Subcategoria': subcat_escolhida,
        'Canal_Atendimento': random.choice(canais),
        'Prioridade': prioridade,
        'Status': status,
        'Tecnico': random.choice(tecnicos),
        'Tempo_Resolucao_Horas': tempo_resolucao,
        'Dentro_SLA': dentro_sla,
        'Nota_CSAT': nota_csat
    })

# Cria o DataFrame do pandas e salva em CSV pronto para o Power BI
df = pd.DataFrame(dados)
df.to_csv('base_suporte_ti.csv', index=False, encoding='utf-8-sig')

print("---")
print("✅ Tudo pronto! O arquivo 'base_suporte_ti.csv' foi gerado com sucesso.")
print("---")