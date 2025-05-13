import streamlit as st
from datetime import datetime, timedelta

# Initialize session state
if 'chargers' not in st.session_state:
    st.session_state.chargers = []  # active chargers
if 'waiting_list' not in st.session_state:
    st.session_state.waiting_list = []  # queued cars
if 'history' not in st.session_state:
    st.session_state.history = []  # completed charges

st.title("Sistema de Gerenciamento de Carregamento de Veículos Elétricos")

# Simulation time input
sim_time = st.sidebar.time_input("Horário de Simulação", value=datetime.now().time())
sim_datetime = datetime.combine(datetime.today(), sim_time)

# Car details input
st.header("Adicionar Novo Carro")
resident = st.text_input("Morador", key="resident")
car = st.text_input("Placa/Carro", key="car")
model = st.text_input("Modelo", key="model")
connector = st.selectbox("Tipo de Conector", ["Tipo 1", "Tipo 2", "CCS", "CHAdeMO"], key="connector")
level = st.slider("Nível Atual da Bateria (%)", 0, 100, 20, key="level")

if st.button("Adicionar Carro"):
    # Before adding, update removals
    def update_chargers(current_time):
        to_remove = []
        for ch in st.session_state.chargers:
            # assume rate 1% por hora
            hours_needed = (100 - ch['level']) / 1.0
            full_time = ch['start_time'] + timedelta(hours=hours_needed)
            if full_time <= current_time:
                to_remove.append(ch)
        for ch in to_remove:
            st.session_state.chargers.remove(ch)
            ch['end_time'] = ch['start_time'] + timedelta(hours=(100 - ch['level']))
            ch['final_level'] = 100
            st.session_state.history.append(ch)
        # fill from waiting list
        while len(st.session_state.chargers) < 3 and st.session_state.waiting_list:
            next_car = st.session_state.waiting_list.pop(0)
            next_car['start_time'] = current_time
            next_car['level'] = next_car['level']
            st.session_state.chargers.append(next_car)

    update_chargers(sim_datetime)
    # Add new car
    if len(st.session_state.chargers) < 3:
        new_ch = {
            'resident': resident,
            'car': car,
            'model': model,
            'connector': connector,
            'level': level,
            'start_time': sim_datetime
        }
        st.session_state.chargers.append(new_ch)
    else:
        new_wait = {
            'resident': resident,
            'car': car,
            'model': model,
            'connector': connector,
            'level': level,
            'request_time': sim_datetime
        }
        st.session_state.waiting_list.append(new_wait)
    st.experimental_rerun()

# Display active chargers
st.header("Estações de Carregamento Ativas")
if st.session_state.chargers:
    data = []
    for idx, ch in enumerate(st.session_state.chargers, start=1):
        # calculate estimated full time
        hours_needed = (100 - ch['level']) / 1.0
        full_time = ch['start_time'] + timedelta(hours=hours_needed)
        data.append({
            'Carregador': idx,
            'Morador': ch['resident'],
            'Carro': ch['car'],
            'Modelo': ch['model'],
            'Conector': ch['connector'],
            'Nível Atual (%)': ch['level'],
            'Início': ch['start_time'].strftime('%H:%M'),
            'Previsão de Término': full_time.strftime('%H:%M')
        })
    st.table(data)
else:
    st.write("Nenhum carregamento em andamento.")

# Display waiting list
st.header("Lista de Espera")
if st.session_state.waiting_list:
    st.table([{
        'Posição': i+1,
        'Morador': w['resident'],
        'Carro': w['car'],
        'Modelo': w['model'],
        'Conector': w['connector'],
        'Nível (%)': w['level'],
        'Chegada': w['request_time'].strftime('%H:%M')
    } for i, w in enumerate(st.session_state.waiting_list)])
else:
    st.write("Sem espera no momento.")

# Display history
st.header("Histórico de Carregamentos Concluídos")
if st.session_state.history:
    st.table([{
        'Morador': h['resident'],
        'Carro': h['car'],
        'Modelo': h['model'],
        'Início': h['start_time'].strftime('%H:%M'),
        'Término': h['end_time'].strftime('%H:%M')
    } for h in st.session_state.history])
else:
    st.write("Nenhum histórico ainda.")
