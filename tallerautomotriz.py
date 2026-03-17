import streamlit as st
import pandas as pd
from google.cloud import firestore
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Sistema de Taller Automotriz", layout="wide")

# Conexión a Firestore
# Nota: Asegúrate de tener las credenciales configuradas en tu entorno
db = firestore.Client()

def app():
    st.title("🛠️ Gestión de Orden de Servicio")

    # Inicializar estados de los carritos en la sesión de Streamlit
    if 'repuestos' not in st.session_state:
        st.session_state.repuestos = []
    if 'mano_de_obra' not in st.session_state:
        st.session_state.mano_de_obra = []

    # --- SECCIÓN 1: DATOS GENERALES ---
    st.subheader("Datos de la Orden")
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_solicitud = st.text_input("Fecha de Solicitud (Sistema)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), disabled=True)
        motivo_ingreso = st.text_area("Motivo de Ingreso")
        estado_orden = st.selectbox("Estado de la Orden", ["Abierta", "Cerrada"])

    with col2:
        inspeccion_inicial = st.text_area("Inspección Inicial")
        comentarios_generales = st.text_area("Cuadro de Diálogo (Comentarios adicionales)")

    st.divider()

    # --- SECCIÓN 2: CARRITO DE REPUESTOS ---
    st.subheader("🛒 Agregar Repuestos")
    c_rep1, c_rep2, c_rep3, c_rep4 = st.columns([3, 2, 2, 2])
    
    with c_rep1: nombre_rep = st.text_input("Repuesto")
    with c_rep2: marca_rep = st.text_input("Marca")
    with c_rep3: prov_rep = st.text_input("Proveedor")
    with c_rep4: precio_rep = st.number_input("Precio Repuesto", min_value=0.0, step=1000.0)

    if st.button("Añadir Repuesto"):
        if nombre_rep:
            st.session_state.repuestos.append({
                "Repuesto": nombre_rep, 
                "Marca": marca_rep, 
                "Proveedor": prov_rep, 
                "Precio": precio_rep
            })
        else:
            st.warning("El nombre del repuesto es obligatorio")

    if st.session_state.repuestos:
        df_rep = pd.DataFrame(st.session_state.repuestos)
        st.table(df_rep)
        if st.button("Limpiar Repuestos"):
            st.session_state.repuestos = []
            st.rerun()

    st.divider()

    # --- SECCIÓN 3: CARRITO DE MANO DE OBRA ---
    st.subheader("🔧 Agregar Mano de Obra")
    c_mo1, c_mo2 = st.columns([6, 2])
    
    with c_mo1: accion_mo = st.text_input("Acción / Tarea")
    with c_mo2: valor_mo = st.number_input("Valor Mano de Obra", min_value=0.0, step=1000.0)

    if st.button("Añadir Mano de Obra"):
        if accion_mo:
            st.session_state.mano_de_obra.append({
                "Acción": accion_mo, 
                "Valor": valor_mo
            })
        else:
            st.warning("La acción es obligatoria")

    if st.session_state.mano_de_obra:
        df_mo = pd.DataFrame(st.session_state.mano_de_obra)
        st.table(df_mo)
        if st.button("Limpiar Mano de Obra"):
            st.session_state.mano_de_obra = []
            st.rerun()

    st.divider()

    # --- SECCIÓN FINAL: RESUMEN Y GUARDADO ---
    total_repuestos = sum(item['Precio'] for item in st.session_state.repuestos)
    total_mo = sum(item['Valor'] for item in st.session_state.mano_de_obra)
    total_general = total_repuestos + total_mo

    st.write(f"### Total Orden: ${total_general:,.2f}")

    if st.button("💾 Guardar Orden de Servicio", type="primary"):
        orden_data = {
            "fecha": fecha_solicitud,
            "motivo": motivo_ingreso,
            "inspeccion": inspeccion_inicial,
            "comentarios": comentarios_generales,
            "estado": estado_orden,
            "repuestos": st.session_state.repuestos,
            "mano_de_obra": st.session_state.mano_de_obra,
            "total": total_general
        }
        
        try:
            db.collection("ordenes_servicio").add(orden_data)
            st.success("¡Orden guardada exitosamente en Firestore!")
            # Limpiar sesión tras guardar
            st.session_state.repuestos = []
            st.session_state.mano_de_obra = []
        except Exception as e:
            st.error(f"Error al guardar: {e}")

if __name__ == "__main__":
    app()