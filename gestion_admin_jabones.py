import datetime
import io
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA (EXCLUSIVA ADMINISTRADORA)
# ==========================================
st.set_page_config(
    page_title="Control de Pedidos y Ganancias - Jabones Artesanales",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo visual personalizado (Elegante, Botánico y Privado)
st.markdown(
    """
    <style>
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2E5A44;
        text-align: center;
        padding: 5px 0;
    }
    .sub-header {
        color: #4A7A61;
        font-weight: 300;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2E5A44;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# FUNCIÓN AUXILIAR PARA GENERAR ARCHIVO EXCEL DESCARGABLE
def generar_excel_descarga(df, nombre_hoja="Ventas"):
    """Genera un buffer binario en formato Excel (.xlsx) listo para descargar."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
    return buffer.getvalue()


# ==========================================
# CONEXIÓN A GOOGLE SHEETS / DRIVE
# ==========================================
@st.cache_resource
def obtener_conexion_google_sheets():
    """Conecta con Google Sheets usando los secretos TOML configurados en Streamlit Cloud."""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        client = gspread.authorize(credentials)
        sh = client.open("Control Jabones Artesanales")
        return sh
    except Exception as e:
        return None


sh_drive = obtener_conexion_google_sheets()

# MAPA BOTÁNICO: Tipo de piel -> Aceites Esenciales & Aromas Permitidos
MAPA_BOTANICO = {
    "Piel Grasa / Mixta": {
        "aceites": [
            "Zacate de Limón",
            "Árbol de Té",
            "Menta Piperita",
            "Salvia",
            "Albahaca",
        ],
        "aromas": [
            "Lemon Grass",
            "Maracuyá",
            "Árbol de Manzana",
            "Ciprés Navideño",
            "Navidad Dorada",
            "Bambú Otoñal",
            "Herbal",
        ],
        "color": "#F39C12",
    },
    "Piel Sensible": {
        "aceites": ["Manzanilla", "Lavanda", "Eucalipto Limón"],
        "aromas": [
            "Frappuchino",
            "Árbol de Manzana",
            "Ciprés Navideño",
            "Navidad Dorada",
            "Bambú Otoñal",
            "Herbal",
            "Brisa de Mar",
        ],
        "color": "#9B59B6",
    },
    "Piel Madura": {
        "aceites": ["Rosas Damascena", "Salvia"],
        "aromas": ["Sandía", "Manzana con Canela", "Brisa de Mar"],
        "color": "#E84393",
    },
    "Piel Seca": {
        "aceites": ["Jengibre", "Albahaca"],
        "aromas": [
            "Frambuesa",
            "Chicle",
            "Sandía",
            "Manzana con Canela",
        ],
        "color": "#E67E22",
    },
}

# PRECIOS CORREGIDOS SEGÚN ARCHIVO FUENTE Y COSTOS DE REFERENCIA
PRECIOS_POR_TAMANO = {
    "Pequeño": 1000,
    "Mediano": 2000,
    "Grande": 3000
}

COSTOS_ESTIMADOS = {
    "Pequeño": 500,
    "Mediano": 800,
    "Grande": 1000
}

# ESTRUCTURA DE TABLAS (EN BLANCO)
COLUMNAS_PEDIDOS = [
    "id_pedido", "fecha", "cliente", "telefono", "email", "direccion",
    "producto", "tipo_piel", "aceite_esencial", "aroma", "tamano",
    "cantidad", "precio_unitario", "total_venta", "costo_total",
    "ganancia_neta", "metodo_pago", "estado"
]

COLUMNAS_INVENTARIO = [
    "id", "nombre", "tipo_piel", "aceite_esencial", "aroma",
    "tamano", "precio_colones", "stock"
]

COLUMNAS_CLIENTES = [
    "id_cliente", "nombre", "telefono", "email", "direccion",
    "total_acumulado", "compras_realizadas"
]

# INICIALIZACIÓN EN BLANCO EN SESSION_STATE
if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=COLUMNAS_PEDIDOS)

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=COLUMNAS_INVENTARIO)

if "customers" not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=COLUMNAS_CLIENTES)

# ENCABEZADO
st.markdown(
    "<h1 class='main-header'>👑 Panel Privado de Administración</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-header'>Gestión Exclusiva de Pedidos, Inventario y Ganancias (Control Jabones Artesanales)</p>",
    unsafe_allow_html=True,
)

# MENÚ NAVEGACIÓN PRIVADA (ORDEN SOLICITADO)
st.sidebar.title("📌 Menú Administradora")
menu = st.sidebar.radio(
    "Selecciona Módulo:",
    [
        "📝 Registrar Nuevo Pedido",
        "📦 Control de Inventario",
        "👥 Directorio de Clientes",
        "📊 Panel de Ventas & Ganancias",
        "☁️ Conexión Google Drive / Sheets",
    ],
)

# ==========================================
# MÓDULO 1: REGISTRAR NUEVO PEDIDO
# ==========================================
if menu == "📝 Registrar Nuevo Pedido":
    st.header("📝 Registro Directo de Pedidos")
    st.caption("Los aceites esenciales, aromas y precios se ajustan automáticamente según el tipo de piel y el tamaño seleccionado.")

    # GUÍA BOTÁNICA EN IMAGEN (DESPLEGABLE / EXPANDER PARA CONSULTA RÁPIDA)
    with st.expander("🖼️ Ver Guía Botánica de Referencia (Catálogo de Esencias y Aromas)", expanded=False):
        try:
            st.image("Catalogo_jabones-esencias-aromas.jpg", caption="Catálogo Botánico de Referencia - Tipo de Piel, Aceites y Aromas", use_container_width=True)
        except Exception:
            st.info("ℹ️ Imagen de referencia 'Catalogo_jabones-esencias-aromas.jpg' (colócala en la misma carpeta raíz del proyecto).")

    st.subheader("1. Datos del Cliente")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        nombre_cliente = st.text_input("Nombre Completo del Cliente *")
        tel_cliente = st.text_input("Teléfono / WhatsApp *")
    with col_c2:
        email_cliente = st.text_input("Correo Electrónico")
        dir_cliente = st.text_area("Dirección Exacta de Envío *")

    st.markdown("---")
    st.subheader("2. Especificación del Jabón Artesanal")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        tipo_piel_sel = st.selectbox("Tipo de Piel *", list(MAPA_BOTANICO.keys()))

    # Filtrado dinámico real en tiempo real de Aceites y Aromas
    aceites_disponibles = MAPA_BOTANICO[tipo_piel_sel]["aceites"]
    aromas_disponibles = MAPA_BOTANICO[tipo_piel_sel]["aromas"]

    with col_p2:
        aceite_sel = st.selectbox("Aceite Esencial Compatible *", aceites_disponibles)
    with col_p3:
        aroma_sel = st.selectbox("Aroma Compatible *", aromas_disponibles)

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        tamano_sel = st.selectbox("Tamaño del Jabón *", ["Pequeño", "Mediano", "Grande"])
    
    # Precio base sugerido según tamaño corregido (1000, 2000, 3000 CRC)
    precio_sugerido = PRECIOS_POR_TAMANO[tamano_sel]

    with col_s2:
        cant = st.number_input("Cantidad *", min_value=1, value=1, step=1)
    with col_s3:
        p_unit = st.number_input("Precio Venta Unitario (₡) *", min_value=100, value=precio_sugerido, step=100)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        metodo_pago_sel = st.radio("Método de Pago *", ["Transferencia / SINPE", "Efectivo", "Tarjeta"], horizontal=True)
    with col_f2:
        estado_sel = st.selectbox("Estado del Pedido *", ["Pendiente", "En Preparación", "Enviado", "Entregado"])

    tot_vta = p_unit * cant
    costo_est_u = COSTOS_ESTIMADOS[tamano_sel]
    tot_costo = costo_est_u * cant
    ganancia_calc = tot_vta - tot_costo

    st.markdown(f"### 💰 **Total Venta:** ₡{tot_vta:,} CRC | **Ganancia Neta Estimada:** ₡{ganancia_calc:,} CRC")

    if st.button("💾 Guardar Pedido", type="primary"):
        if not nombre_cliente or not tel_cliente or not dir_cliente:
            st.error("⚠️ Los campos de cliente (Nombre, Teléfono, Dirección) son obligatorios.")
        else:
            id_p = f"PED-{int(datetime.datetime.now().timestamp())}"
            nuevo_p = {
                "id_pedido": id_p,
                "fecha": datetime.date.today().strftime("%Y-%m-%d"),
                "cliente": nombre_cliente,
                "telefono": tel_cliente,
                "email": email_cliente,
                "direccion": dir_cliente,
                "producto": f"Jabón {aceite_sel} ({tamano_sel})",
                "tipo_piel": tipo_piel_sel,
                "aceite_esencial": aceite_sel,
                "aroma": aroma_sel,
                "tamano": tamano_sel,
                "cantidad": cant,
                "precio_unitario": p_unit,
                "total_venta": tot_vta,
                "costo_total": tot_costo,
                "ganancia_neta": ganancia_calc,
                "metodo_pago": metodo_pago_sel,
                "estado": estado_sel,
            }

            # Guardar localmente en session_state
            st.session_state.orders = pd.concat(
                [st.session_state.orders, pd.DataFrame([nuevo_p])], ignore_index=True
            )

            # Sincronización con Google Sheets si existe la conexión
            if sh_drive:
                try:
                    ws_ventas = sh_drive.worksheet("Ventas")
                    ws_ventas.append_row(list(nuevo_p.values()))
                    st.success(f"🎉 ¡Pedido `{id_p}` guardado y sincronizado en Google Sheets!")
                except Exception as e:
                    st.warning(f"Guardado localmente. No se pudo actualizar Google Sheets: {e}")
            else:
                st.success(f"🎉 ¡Pedido `{id_p}` guardado con éxito!")

            # Actualizar directorio de clientes
            if len(st.session_state.customers) > 0 and nombre_cliente in st.session_state.customers["nombre"].values:
                idx_c = st.session_state.customers[st.session_state.customers["nombre"] == nombre_cliente].index[0]
                st.session_state.customers.loc[idx_c, "total_acumulado"] += tot_vta
                st.session_state.customers.loc[idx_c, "compras_realizadas"] += 1
            else:
                nuevo_c = {
                    "id_cliente": str(int(datetime.datetime.now().timestamp())),
                    "nombre": nombre_cliente,
                    "telefono": tel_cliente,
                    "email": email_cliente,
                    "direccion": dir_cliente,
                    "total_acumulado": tot_vta,
                    "compras_realizadas": 1,
                }
                st.session_state.customers = pd.concat(
                    [st.session_state.customers, pd.DataFrame([nuevo_c])], ignore_index=True
                )

# ==========================================
# MÓDULO 2: CONTROL DE INVENTARIO
# ==========================================
elif menu == "📦 Control de Inventario":
    st.header("📦 Control de Stock e Inventario")
    
    if len(st.session_state.inventory) == 0:
        st.info("ℹ️ El inventario se encuentra actualmente en blanco.")
        st.dataframe(pd.DataFrame(columns=COLUMNAS_INVENTARIO), use_container_width=True)
    else:
        st.dataframe(st.session_state.inventory, use_container_width=True)

    st.markdown("---")
    st.subheader("➕ Agregar Producto al Inventario")

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        i_nombre = st.text_input("Nombre Identificador del Jabón")
        i_tipo_piel = st.selectbox("Tipo de Piel", list(MAPA_BOTANICO.keys()))
    
    i_aceites = MAPA_BOTANICO[i_tipo_piel]["aceites"]
    i_aromas = MAPA_BOTANICO[i_tipo_piel]["aromas"]

    with col_i2:
        i_aceite = st.selectbox("Aceite Esencial", i_aceites)
        i_aroma = st.selectbox("Aroma", i_aromas)

    col_i3, col_i4, col_i5 = st.columns(3)
    with col_i3:
        i_tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"])
    
    precio_inv_def = PRECIOS_POR_TAMANO[i_tamano]

    with col_i4:
        i_precio = st.number_input("Precio Venta (₡)", value=precio_inv_def, step=100)
    with col_i5:
        i_stock = st.number_input("Stock Inicial (Unidades)", value=10, min_value=0)

    if st.button("➕ Añadir al Inventario", type="primary"):
        nuevo_item = {
            "id": str(int(datetime.datetime.now().timestamp())),
            "nombre": i_nombre if i_nombre else f"Jabón {i_aceite} ({i_tamano})",
            "tipo_piel": i_tipo_piel,
            "aceite_esencial": i_aceite,
            "aroma": i_aroma,
            "tamano": i_tamano,
            "precio_colones": i_precio,
            "stock": i_stock,
        }
        st.session_state.inventory = pd.concat(
            [st.session_state.inventory, pd.DataFrame([nuevo_item])], ignore_index=True
        )
        st.success(f"✔️ Producto '{nuevo_item['nombre']}' añadido al inventario.")

# ==========================================
# MÓDULO 3: DIRECTORIO DE CLIENTES
# ==========================================
elif menu == "👥 Directorio de Clientes":
    st.header("👥 Directorio Consolidado de Clientes")
    if len(st.session_state.customers) == 0:
        st.info("ℹ️ No hay clientes registrados aún. Se añadirán automáticamente conforme registres pedidos.")
        st.dataframe(pd.DataFrame(columns=COLUMNAS_CLIENTES), use_container_width=True)
    else:
        st.dataframe(st.session_state.customers, use_container_width=True)

# ==========================================
# MÓDULO 4: PANEL DE VENTAS & GANANCIAS
# ==========================================
elif menu == "📊 Panel de Ventas & Ganancias":
    st.header("📈 Resumen Contable y Ganancias")
    
    if len(st.session_state.orders) == 0:
        st.info("ℹ️ No hay pedidos registrados aún.")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Ingresos (Ventas)", "₡0 CRC")
        c2.metric("Total Costos Producción", "₡0 CRC")
        c3.metric("Ganancia Neta 💰", "₡0 CRC")
        c4.metric("Pedidos Totales", "0")
        
        st.markdown("---")
        st.subheader("📋 Historial Completo de Pedidos")
        st.dataframe(pd.DataFrame(columns=COLUMNAS_PEDIDOS), use_container_width=True)
    else:
        total_ingresos = st.session_state.orders["total_venta"].sum()
        total_costos = st.session_state.orders["costo_total"].sum()
        ganancia_neta = st.session_state.orders["ganancia_neta"].sum()
        num_pedidos = len(st.session_state.orders)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Ingresos (Ventas)", f"₡{total_ingresos:,} CRC")
        c2.metric("Total Costos Producción", f"₡{total_costos:,} CRC")
        c3.metric("Ganancia Neta 💰", f"₡{ganancia_neta:,} CRC")
        c4.metric("Pedidos Totales", f"{num_pedidos}")

        st.markdown("---")
        st.subheader("📋 Historial Completo de Pedidos")

        # BOTÓN DE DESCARGA EN EXCEL (.XLSX)
        excel_data = generar_excel_descarga(st.session_state.orders, nombre_hoja="Historial_Pedidos")
        st.download_button(
            label="📊 Descargar Reporte Completo de Ventas en Excel (.xlsx)",
            data=excel_data,
            file_name=f"Reporte_Ventas_Jabones_{datetime.date.today().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        st.markdown("")
        st.dataframe(st.session_state.orders, use_container_width=True)

# ==========================================
# MÓDULO 5: CONEXIÓN GOOGLE DRIVE / SHEETS
# ==========================================
elif menu == "☁️ Conexión Google Drive / Sheets":
    st.header("☁️ Sincronización Automática con Google Drive")
    if sh_drive:
        st.success("✅ ¡Conexión exitosa con la hoja de cálculo **'Control Jabones Artesanales'** en Google Drive!")
    else:
        st.warning("⚠️ No hay conexión activa actualmente con Google Drive. La app está funcionando en modo local.")
        st.info("Para conectar con tu Google Sheet 'Control Jabones Artesanales', agrega las credenciales JSON en la sección Secrets de Streamlit Cloud.")
