import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

st.set_page_config(page_title="Taller Pro", layout="wide")
DB_FILE = "ordenes.csv"
ITEMS_FILE = "items_orden.csv"

# --- FUNCIONES DE PERSISTENCIA ---
def guardar_datos(archivo, datos):
    df = pd.DataFrame([datos])
    if not os.path.isfile(archivo):
        df.to_csv(archivo, index=False)
    else:
        df.to_csv(archivo, mode='a', header=False, index=False)

def actualizar_estado(id_orden, nuevo_estado):
    df = pd.read_csv(DB_FILE)
    df.loc[df['id'] == id_orden, 'estado'] = nuevo_estado
    df.to_csv(DB_FILE, index=False)

# --- INTERFAZ ---
st.title("🛠️ Sistema de Gestión de Talleres")

tab1, tab2 = st.tabs(["🆕 Crear Orden", "📂 Gestionar Orden Abierta"])

# TAB 1: CREACIÓN INICIAL
with tab1:
    st.header("Nueva Orden de Servicio")
    with st.form("crear_orden"):
        motivo = st.text_input("Motivo de Ingreso")
        inspeccion = st.text_area("Inspección Inicial")
        if st.form_submit_button("🔥 CREAR ORDEN"):
            id_nueva = str(uuid.uuid4())[:8].upper()
            data = {
                "id": id_nueva,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "motivo": motivo,
                "inspeccion": inspeccion,
                "estado": "Abierta"
            }
            guardar_datos(DB_FILE, data)
            st.success(f"Orden {id_nueva} creada. búscala en la siguiente pestaña.")

# TAB 2: AGREGAR ITEMS (REPUESTOS/MANO DE OBRA)
with tab2:
    st.header("Actualizar Orden")
    if os.path.exists(DB_FILE):
        df_ordenes = pd.read_csv(DB_FILE)
        ordenes_abiertas = df_ordenes[df_ordenes['estado'] == "Abierta"]['id'].tolist()
        
        id_busqueda = st.selectbox("Selecciona Orden Abierta", [""] + ordenes_abiertas)
        
        if id_busqueda:
            row = df_ordenes[df_ordenes['id'] == id_busqueda].iloc[0]
            st.info(f"**Motivo:** {row['motivo']} | **Fecha:** {row['fecha']}")
            
            # Formulario para agregar items
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1: desc = st.text_input("Descripción (Repuesto/Mano de Obra)")
            with col2: valor = st.number_input("Valor", min_value=0.0)
            with col3:
                if st.button("➕ Añadir"):
                    guardar_datos(ITEMS_FILE, {"id_orden": id_busqueda, "desc": desc, "valor": valor})
                    st.toast("Item agregado")

            # Mostrar items actuales
            if os.path.exists(ITEMS_FILE):
                df_items = pd.read_csv(ITEMS_FILE)
                mis_items = df_items[df_items['id_orden'] == id_busqueda]
                if not mis_items.empty:
                    st.table(mis_items[['desc', 'valor']])
                    st.write(f"**Subtotal: ${mis_items['valor'].sum():,.0f}**")

            st.divider()
            if st.button("🔒 CERRAR ORDEN DEFINITIVAMENTE"):
                actualizar_estado(id_busqueda, "Cerrada")
                st.warning("Orden cerrada. Ya no aparecerá para edición.")
                st.rerun()
    else:
        st.write("No hay órdenes registradas aún.")