import streamlit as st
from datetime import datetime, timedelta

# Configuração de moradores predefinidos
dorms = {
    "Morador 1": {"car": "ABC1234", "model": "Tesla Model 3", "connector": "CCS", "level": 20},
    "Morador 2": {"car": "XYZ5678", "model": "Nissan Leaf", "connector": "Tipo 2", "level": 50},
    "Morador 3": {"car": "DEF9012", "model": "Chevrolet Bolt", "connector": "CCS", "level": 30},
}

# Inicializa sessões
if 'chargers' not in st.session_state:
    st.session_state.chargers = []  # carros em carregamento
if 'history' not in st.session_state:
    st.session_state.history = []  # carros removidos
if 'sim_time' not in st.session_state:
    # Inicia simulação hoje às 07:00
    today = datetime.now().date()
    st.session_state.sim_time = datetime.combine(today, datetime.min.time()).replace(hour=7)

st.title("Sistema Simplificado - 5 Estações")

# Controle de tempo
st.subheader("Tempo de Simulação")
st.write(st.session_state.sim_time.strftime('%d/%m/%Y %H:%M'))
if st.button("Avançar 1 hora", key='advance'):
    st.session_state.sim_time += timedelta(hours=1)
    # Atualiza nível e custo de cada carro
    for ch in st.session_state.chargers:
        # taxa de carga (% por hora)
        rate = ch.get('rate', 10)
        prev_level = ch['level']
        ch['level'] = min(100, prev_level + rate)
        # custo por %
        cost_per_percent = st.sidebar.number_input("Custo por % de carga", min_value=0.0, value=2.0, step=0.5, key='costp')
        ch['cost'] = ch.get('cost', 0) + (ch['level'] - prev_level) * cost_per_percent

# Formulário de alocação
st.header("Adicionar Carro")
resident = st.selectbox("Morador", [None] + list(dorms.keys()), key='res')
if resident:
    info = dorms[resident]
    car = info['car']
    model = info['model']
    connector = info['connector']
    level = info['level']
else:
    resident = st.text_input("Morador (novo)", key='res_text')
    car = st.text_input("Placa/Carro", key='car')
    model = st.text_input("Modelo", key='model')
    connector = st.selectbox("Conector", ["Tipo 1","Tipo 2","CCS","CHAdeMO"], key='conn')
    level = st.slider("Nível Inicial (%)", 0, 100, 20, key='level')

if st.button("Alocar Carro", key='add'):
    if len(st.session_state.chargers) < 5:
        st.session_state.chargers.append({
            'resident': resident,
            'car': car,
            'model': model,
            'connector': connector,
            'level': level,
            'rate': 10,         # % por hora
            'cost': 0
        })
    else:
        st.warning("Todas as estações estão ocupadas.")

# Exibição das vagas
st.header("Estações - Status")
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        if i < len(st.session_state.chargers):
            ch = st.session_state.chargers[i]
            st.subheader(f"Vaga {i+1}")
            st.write(f"**Morador:** {ch['resident']}")
            st.write(f"**Carro:** {ch['car']}")
            st.write(f"**Modelo:** {ch['model']}")
            st.write(f"**Conector:** {ch['connector']}")
            st.progress(int(ch['level']))
            st.write(f"Custo até agora: R$ {ch['cost']:.2f}")
            if st.button("Remover", key=f"rem_{i}"):
                # Registra e remove
                record = ch.copy()
                record['removed_at'] = st.session_state.sim_time
                st.session_state.history.append(record)
                st.session_state.chargers.pop(i)
        else:
            st.subheader(f"Vaga {i+1} (Livre)")

# Histórico de remoções
st.header("Histórico de Remoções")
if st.session_state.history:
    for h in st.session_state.history:
        sim_time = h['removed_at'].strftime('%d/%m %H:%M')
        st.write(f"{h['resident']} - {h['car']} | Removido às {sim_time} | Custo total: R$ {h['cost']:.2f}")
else:
    st.write("Nenhum carro removido ainda.")
