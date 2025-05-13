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
def init_state():
    if 'chargers' not in st.session_state:
        st.session_state.chargers = []
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'sim_time' not in st.session_state:
        today = datetime.now().date()
        st.session_state.sim_time = datetime.combine(today, datetime.min.time()).replace(hour=7)

init_state()

st.set_page_config(page_title="Carregadores EV", layout="wide")
st.title("⚡ Sistema de 3 Carregadores ⚡")

# Controle de tempo
with st.sidebar:
    st.subheader("⏱ Tempo de Simulação")
    st.write(st.session_state.sim_time.strftime('%d/%m/%Y %H:%M'))
    if st.button("Avançar +1h"):
        st.session_state.sim_time += timedelta(hours=1)
        for ch in st.session_state.chargers:
            prev = ch['level']
            new = min(1.0, prev + 0.10)
            delta = new - prev
            ch['level'] = new
            energy = ch['capacity'] * delta / ch['eff']
            ch['cost'] += energy * ch['cost_kwh']

# Alocação de carro
st.sidebar.subheader("🚗 Alocar Carro")
options = ["Adicionar Morador"] + list(dorms.keys())
sel = st.sidebar.selectbox("Morador", options, key='sel')
if st.sidebar.button("Alocar"):
    if sel == "Adicionar Morador":
        st.sidebar.warning("Selecione um morador.")
    elif any(c['resident']==sel for c in st.session_state.chargers):
        st.sidebar.warning(f"{sel} já está em carga.")
    elif len(st.session_state.chargers)>=3:
        st.sidebar.warning("3 estações ocupadas.")
    else:
        info = dorms[sel]
        st.session_state.chargers.append({**info, 'resident': sel, 'cost': 0})

# Exibição das 3 vagas
st.header("🔌 Estações de Carga")
cols = st.columns(3, gap="large")
for i, col in enumerate(cols):
    with col:
        if i < len(st.session_state.chargers):
            ch = st.session_state.chargers[i]
            st.markdown(f"### ⚡ Vaga {i+1}")
            st.markdown(f"**Morador:** {ch['resident']}  
            **Carro:** {ch['car']} {ch['model']}  
            **Conector:** {ch['connector']}")
            st.progress(int(ch['level']*100))
            st.markdown(f"**Custo:** R$ {ch['cost']:.2f}")
            if st.button("🗑 Remover", key=f"rem{i}"):
                rec = ch.copy()
                rec['removed_at'] = st.session_state.sim_time
                st.session_state.history.append(rec)
                st.session_state.chargers.pop(i)
        else:
            st.markdown(f"### 🔋 Vaga {i+1} (Livre)")

# Histórico de cargas
st.header("📜 Histórico")
if st.session_state.history:
    for h in st.session_state.history:
        t = h['removed_at'].strftime('%d/%m %H:%M')
        st.write(f"{h['resident']} | Custo: R$ {h['cost']:.2f} | Removido: {t}")
else:
    st.write("Nenhuma carga concluída.")
