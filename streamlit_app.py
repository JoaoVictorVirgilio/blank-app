import streamlit as st
from datetime import datetime, timedelta

# Configuração de 10 moradores com dados fixos
dorms = {
    "Morador 1":  {"car": "Tesla",    "model": "Model 3",      "connector": "Tipo 2",   "level": 0.15, "capacity": 75, "eff": 0.90, "cost_kwh": 0.71},
    "Morador 2":  {"car": "Volkswagen","model": "ID.4",         "connector": "CCS Combo", "level": 0.77, "capacity": 70, "eff": 0.86, "cost_kwh": 0.71},
    "Morador 3":  {"car": "Hyundai",   "model": "Kona Electric", "connector": "Tipo 1",   "level": 0.98, "capacity": 60, "eff": 0.94, "cost_kwh": 0.71},
    "Morador 4":  {"car": "Tesla",    "model": "Model 3",      "connector": "CHAdeMO",   "level": 0.71, "capacity": 40, "eff": 0.87, "cost_kwh": 0.71},
    "Morador 5":  {"car": "Mercedes", "model": "EQC",           "connector": "Tipo 2",   "level": 0.99, "capacity": 40, "eff": 0.89, "cost_kwh": 0.71},
    "Morador 6":  {"car": "Tesla",    "model": "Model Y",      "connector": "CHAdeMO",   "level": 0.45, "capacity": 60, "eff": 0.90, "cost_kwh": 0.71},
    "Morador 7":  {"car": "Porsche",  "model": "Taycan",        "connector": "CHAdeMO",   "level": 0.65, "capacity": 40, "eff": 0.88, "cost_kwh": 0.71},
    "Morador 8":  {"car": "Mercedes", "model": "EQC",           "connector": "CCS Combo", "level": 0.78, "capacity": 80, "eff": 0.85, "cost_kwh": 0.71},
    "Morador 9":  {"car": "Renault",  "model": "Zoe",           "connector": "Tipo 1",   "level": 0.10, "capacity": 60, "eff": 0.92, "cost_kwh": 0.71},
    "Morador 10": {"car": "Tesla",    "model": "Model Y",      "connector": "CCS Combo", "level": 0.48, "capacity": 90, "eff": 0.86, "cost_kwh": 0.71},
}

# Inicializa sessões
if 'chargers' not in st.session_state:
    st.session_state.chargers = []  # estações ocupadas
if 'history' not in st.session_state:
    st.session_state.history = []   # registros concluídos
if 'sim_time' not in st.session_state:
    today = datetime.now().date()
    st.session_state.sim_time = datetime.combine(today, datetime.min.time()).replace(hour=7)

st.title("Sistema de Carregadores - 5 Estações")

# Controle de tempo
st.subheader("Tempo de Simulação")
st.write(st.session_state.sim_time.strftime('%d/%m/%Y %H:%M'))
if st.button("Avançar 1 hora"):
    st.session_state.sim_time += timedelta(hours=1)
    for ch in st.session_state.chargers:
        prev = ch['level']
        # taxa fixa de 10% por hora
        new_level = min(1.0, prev + 0.10)
        delta = new_level - prev
        ch['level'] = new_level
        # custo: energia desenhada = capacidade * delta / eficiência
        energy_drawn = ch['capacity'] * delta / ch['eff']
        ch['cost'] += energy_drawn * ch['cost_kwh']

# Alocação de carro
st.header("Alocar Carro")
sel = st.selectbox("Escolha o Morador", [None] + list(dorms.keys()))
if st.button("Alocar"):
    if sel and len(st.session_state.chargers) < 5:
        info = dorms[sel]
        st.session_state.chargers.append({
            'resident': sel,
            'car': info['car'],
            'model': info['model'],
            'connector': info['connector'],
            'level': info['level'],
            'capacity': info['capacity'],
            'eff': info['eff'],
            'cost_kwh': info['cost_kwh'],
            'cost': 0
        })
    else:
        st.warning("Selecione um morador e verifique vagas disponíveis.")

# Visualização das vagas
st.header("Estações")
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        if i < len(st.session_state.chargers):
            ch = st.session_state.chargers[i]
            st.subheader(f"Vaga {i+1}")
            st.write(f"{ch['resident']} - {ch['car']}")
            st.progress(int(ch['level']*100))
            st.write(f"Custo acumulado: R$ {ch['cost']:.2f}")
            if st.button("Remover", key=f"rem{i}"):
                rec = ch.copy()
                rec['removed_at'] = st.session_state.sim_time
                st.session_state.history.append(rec)
                st.session_state.chargers.pop(i)
        else:
            st.subheader(f"Vaga {i+1} (Livre)")

# Histórico
st.header("Histórico de Cargas")
if st.session_state.history:
    for h in st.session_state.history:
        time = h['removed_at'].strftime('%d/%m %H:%M')
        st.write(f"{h['resident']} | Custo total: R$ {h['cost']:.2f} | Removido: {time}")
else:
    st.write("Nenhuma carga concluída ainda.")
