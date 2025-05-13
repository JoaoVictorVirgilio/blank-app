import streamlit as st

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

st.title("Sistema Simplificado - 5 Estações")

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
    level = st.slider("Nível (%)", 0, 100, 20, key='level')

if st.button("Alocar Carro", key='add'):
    if len(st.session_state.chargers) < 5:
        st.session_state.chargers.append({
            'resident': resident,
            'car': car,
            'model': model,
            'connector': connector,
            'level': level
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
            st.progress(ch['level'])
            if st.button("Remover", key=f"rem_{i}"):
                st.session_state.history.append(ch)
                st.session_state.chargers.pop(i)
                # Sem experimental_rerun: Streamlit atualiza automaticamente
        else:
            st.subheader(f"Vaga {i+1} (Livre)")

# Histórico de remoções
st.header("Histórico de Remoções")
if st.session_state.history:
    for h in st.session_state.history:
        st.write(f"{h['resident']} - {h['car']} ({h['model']}) - {h['level']}%")
else:
    st.write("Nenhum carro removido ainda.")
