import streamlit as st
from datetime import datetime, timedelta

# Configuração de moradores predefinidos
dorms = {
    "Morador 1": {"car": "ABC1234", "model": "Tesla Model 3", "connector": "CCS", "initial_level": 20},
    "Morador 2": {"car": "XYZ5678", "model": "Nissan Leaf", "connector": "Tipo 2", "initial_level": 50},
    "Morador 3": {"car": "DEF9012", "model": "Chevrolet Bolt", "connector": "CCS", "initial_level": 30},
    # Adicione quantos moradores quiser aqui
}

# Inicializa estados da sessão
if 'chargers' not in st.session_state:
    st.session_state.chargers = []  # lista de estações ocupadas
if 'history' not in st.session_state:
    st.session_state.history = []

# Título
title = "Sistema de Carregamento - 5 Estações"
st.title(title)

# Controle de horário da simulação (apenas avanço)
if 'sim_time' not in st.session_state:
    st.session_state.sim_time = datetime.now()
new_time = st.sidebar.datetime_input("Horário da Simulação", value=st.session_state.sim_time)
# Garantir só avanço
if new_time >= st.session_state.sim_time:
    st.session_state.sim_time = new_time
current_time = st.session_state.sim_time

# Função para atualizar níveis e mover carros completos para histórico
def update_chargers():
    updated = []
    for ch in st.session_state.chargers:
        hours_passed = (current_time - ch['start_time']).total_seconds() / 3600
        level = min(ch['initial_level'] + hours_passed * ch['rate'], 100)
        ch['current_level'] = level
        if level >= 100 and not ch['auto_removal']:
            ch['complete'] = True
        updated.append(ch)
    st.session_state.chargers = updated

update_chargers()

# Formulário de nova entrada
st.header("Adicionar Carro")
resident = st.selectbox("Morador", [None] + list(dorms.keys()))
if resident:
    info = dorms[resident]
    car = info['car']
    model = info['model']
    connector = info['connector']
    initial_level = info['initial_level']
else:
    car = st.text_input("Placa/Carro")
    model = st.text_input("Modelo")
    connector = st.selectbox("Tipo de Conector", ["Tipo 1", "Tipo 2", "CCS", "CHAdeMO"])
    initial_level = st.slider("Nível Inicial (%)", 0, 100, 20)

if st.button("Alocar no Próximo Carregador"):
    if len(st.session_state.chargers) < 5:
        st.session_state.chargers.append({
            'resident': resident or "-",
            'car': car,
            'model': model,
            'connector': connector,
            'initial_level': initial_level,
            'start_time': current_time,
            'rate': 1.0,  # % por hora
            'current_level': initial_level,
            'auto_removal': False,
            'complete': False
        })
    else:
        st.warning("Todas as 5 estações estão ocupadas.")

# Exibição dos carregadores
st.header("Estações de Carregamento (5)")
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        if i < len(st.session_state.chargers):
            ch = st.session_state.chargers[i]
            st.subheader(f"Vaga {i+1}")
            st.text(f"{ch['resident']}\n{ch['car']}\n{ch['model']}")
            st.progress(int(ch['current_level']))
            # Botão de remoção manual
            if st.button(f"Remover Vaga {i+1}"):
                st.session_state.history.append({
                    **ch,
                    'end_time': current_time
                })
                st.session_state.chargers.pop(i)
                st.experimental_rerun()
        else:
            st.subheader(f"Vaga {i+1}\n(Disponível)")

# Histórico de carregamentos
st.header("Histórico")
if st.session_state.history:
    for h in st.session_state.history:
        duration = (h['end_time'] - h['start_time']).total_seconds() / 3600
        level = min(h['initial_level'] + duration * h['rate'], 100)
        st.write(f"{h['resident']} - {h['car']} | Início: {h['start_time'].strftime('%d/%m %H:%M')} - Fim: {h['end_time'].strftime('%d/%m %H:%M')} | Nível: {int(level)}%")
else:
    st.write("Nenhum carregamento concluído ainda.")
