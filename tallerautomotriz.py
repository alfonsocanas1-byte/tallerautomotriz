import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Taller", layout="wide")

# Base de datos local simple
DB_FILE = "ordenes.csv"

def guardar_datos(datos):
    df = pd.DataFrame([datos])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False)

st.title("🛠️ Orden de Servicio")

# Estados de los carritos
if 'items' not in st.session_state: st.session_state.items = []

# 1. Datos Generales
col1, col2 = st.columns(2)
with col1:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.write(f"**Fecha:** {fecha}")
    motivo = st.text_input("Motivo ingreso")
    estado = st.selectbox("Estado", ["Abierta", "Cerrada"])
with col2:
    inspeccion = st.text_area("Inspección inicial")
    comentarios = st.text_area("Repuestos / Comentarios")

st.divider()

# 2. Carrito Único (Repuestos y Mano de Obra)
st.subheader("🛒 Agregar a la Orden")
c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
with c1: desc = st.text_input("Descripción (Repuesto o Acción)")
with c2: marca = st.text_input("Marca / Proveedor")
with c3: valor = st.number_input("Valor", min_value=0.0)
with c4: 
    if st.button("Add"):
        st.session_state.items.append({"Descripción": desc, "Marca": marca, "Valor": valor})

if st.session_state.items:
    df_items = pd.DataFrame(st.session_state.items)
    st.table(df_items)
    total = df_items["Valor"].sum()
    st.write(f"**Total: ${total:,.0f}**")

st.divider()

# 3. Guardar
if st.button("💾 REGISTRAR ORDEN", type="primary"):
    data = {
        "fecha": fecha, "motivo": motivo, "estado": estado,
        "inspeccion": inspeccion, "comentarios": comentarios,
        "total": total if st.session_state.items else 0
    }
    guardar_datos(data)
    st.success("Guardado en ordenes.csv")
    st.session_state.items = []