import datetime
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
    # Abrir la hoja de cálculo por su nombre exacto en Google Drive
    sh = client.open("Control Jabones Artesanales")
    return sh
  except Exception as e:
    st.error(
        "⚠️ No se pudo conectar a Google Sheets. Revisa la configuración de"
        f" Secrets en Streamlit Cloud. Error: {e}"
    )
    return None


# Intento de conexión
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
            "Manzana Canela",
            "Sandía",
            "Manzana con Canela",
        ],
        "color": "#E67E22",
    },
}

# DATOS EN MEMORIA / FALLBACK
if "orders" not in st.session_state:
  st.session_state.orders = pd.DataFrame([{
      "id_pedido": "PED-1791504650728",
      "fecha": "2026-10-08",
      "cliente": "Mauricio Padilla",
      "telefono": "88691955",
      "email": "mauricio.padillau@gmail.com",
      "direccion": "Ipís, Goicoechea, San José",
      "producto": "Jabón Zacate de Limón (Mediano)",
      "tipo_piel": "Piel Grasa / Mixta",
      "aceite_esencial": "Zacate de Limón",
      "aroma": "Lemon Grass",
      "tamano": "Mediano (100g)",
      "cantidad": 2,
      "precio_unitario": 2000,
      "costo_unitario": 850,
      "total_venta": 4000,
      "costo_total": 1700,
      "ganancia_neta": 2300,
      "metodo_pago": "Transferencia / SINPE",
      "estado": "Entregado",
  }])

if "inventory" not in st.session_state:
  st.session_state.inventory = pd.DataFrame([
      {
          "id": "1791504585160",
          "nombre": "Jabón Zacate de Limón",
          "tipo_piel": "Piel Grasa / Mixta",
          "aceite_esencial": "Zacate de Limón",
          "aroma": "Lemon Grass",
          "tamano": "Mediano (100g)",
          "precio_colones": 2000,
          "costo_est_colones": 850,
          "stock": 15,
      },
      {
          "id": "1791504585161",
          "nombre": "Jabón Manzanilla Calma",
          "tipo_piel": "Piel Sensible",
          "aceite_esencial": "Manzanilla",
          "aroma": "Herbal",
          "tamano": "Grande (150g)",
          "precio_colones": 2500,
          "costo_est_colones": 1000,
          "stock": 10,
      },
  ])

if "customers" not in st.session_state:
  st.session_state.customers = pd.DataFrame([{
      "id_cliente": "1791504635575",
      "nombre": "Mauricio Padilla",
      "telefono": "88691955",
      "email": "mauricio.padillau@gmail.com",
      "direccion": "Ipís, Goicoechea, San José",
      "total_acumulado": 4000,
      "compras_realizadas": 1,
  }])

# ENCABEZADO
st.markdown(
    "<h1 class='main-header'>👑 Panel Privado de Administración</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-header'>Gestión Exclusiva de Pedidos, Inventario y Ganancias"
    " (Almacenado en Google Drive)</p>",
    unsafe_allow_html=True,
)

# MENÚ NAVEGACIÓN PRIVADA
st.sidebar.title("📌 Menú Administradora")
menu = st.sidebar.radio(
    "Selecciona Módulo:",
    [
        "📊 Panel de Ventas & Ganancias",
        "📝 Registrar Nuevo Pedido",
        "📦 Control de Inventario",
        "👥 Directorio de Clientes",
        "☁️ Conexión Google Drive / Sheets",
    ],
)

# MÓDULO 1: VENTAS Y GANANCIAS
if menu == "📊 Panel de Ventas & Ganancias":
  st.header("📈 Resumen Contable y Ganancias")
  if len(st.session_state.orders) > 0:
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
    st.dataframe(
        st.session_state.orders[[
            "id_pedido",
            "fecha",
            "cliente",
            "producto",
            "tipo_piel",
            "aceite_esencial",
            "aroma",
            "tamano",
            "cantidad",
            "total_venta",
            "costo_total",
            "ganancia_neta",
            "metodo_pago",
            "estado",
        ]],
        use_container_width=True,
    )

# MÓDULO 2: REGISTRAR NUEVO PEDIDO
elif menu == "📝 Registrar Nuevo Pedido":
  st.header("📝 Registro Directo de Pedidos")
  st.caption(
      "Al seleccionar el Tipo de Piel, los aceites esenciales y los aromas se"
      " filtran automáticamente según la formulación botánica."
  )

  with st.form("form_pedido_admin"):
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

    # Selección de Tipo de Piel
    tipo_piel_sel = st.selectbox("Tipo de Piel *", list(MAPA_BOTANICO.keys()))

    # FILTRADO DINÁMICO DE ACEITES Y AROMAS SEGÚN TIPO DE PIEL
    aceites_disponibles = MAPA_BOTANICO[tipo_piel_sel]["aceites"]
    aromas_disponibles = MAPA_BOTANICO[tipo_piel_sel]["aromas"]

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
      aceite_sel = st.selectbox(
          "Aceite Esencial Compatible *", aceites_disponibles
      )
    with col_p2:
      aroma_sel = st.selectbox("Aroma Compatible *", aromas_disponibles)
    with col_p3:
      tamano_sel = st.selectbox(
          "Tamaño del Jabón *",
          ["Pequeño (50g)", "Mediano (100g)", "Grande (150g)"],
      )

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      cant = st.number_input("Cantidad *", min_value=1, value=1)
    with col_f2:
      p_unit = st.number_input(
          "Precio Venta Unitario (₡)", min_value=500, value=2000, step=100
      )
    with col_f3:
      c_unit = st.number_input(
          "Costo Producción Unitario (₡)", min_value=100, value=850, step=50
      )

    metodo_pago_sel = st.radio(
        "Método de Pago",
        ["Transferencia / SINPE", "Efectivo", "Tarjeta"],
        horizontal=True,
    )
    estado_sel = st.selectbox(
        "Estado del Pedido",
        ["Pendiente", "En Preparación", "Enviado", "Entregado"],
    )

    tot_vta = p_unit * cant
    tot_costo = c_unit * cant
    ganancia_calc = tot_vta - tot_costo

    st.markdown(
        f"### 💰 **Total Venta:** ₡{tot_vta:,} CRC | **Ganancia Neta"
        f" Estimada:** ₡{ganancia_calc:,} CRC"
    )

    btn_guardar = st.form_submit_button("💾 Guardar Pedido")

    if btn_guardar:
      if not nombre_cliente or not tel_cliente or not dir_cliente:
        st.error(
            "⚠️ Los campos de cliente (Nombre, Teléfono, Dirección) son"
            " obligatorios."
        )
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
            "costo_unitario": c_unit,
            "total_venta": tot_vta,
            "costo_total": tot_costo,
            "ganancia_neta": ganancia_calc,
            "metodo_pago": metodo_pago_sel,
            "estado": estado_sel,
        }

        # Guardar localmente en el session_state
        st.session_state.orders = pd.concat(
            [st.session_state.orders, pd.DataFrame([nuevo_p])], ignore_index=True
        )

        # Si hay conexión con Google Sheets, guardar la fila en la hoja 'Ventas'
        if sh_drive:
          try:
            ws_ventas = sh_drive.worksheet("Ventas")
            ws_ventas.append_row(list(nuevo_p.values()))
            st.success(
                f"🎉 ¡Pedido `{id_p}` guardado e insertado correctamente en"
                " Google Sheets!"
            )
          except Exception as e:
            st.warning(
                "El pedido se guardó localmente, pero no se pudo enviar a"
                f" Google Sheets: {e}"
            )
        else:
          st.success(
              f"🎉 ¡Pedido `{id_p}` guardado en la sesión de la aplicación!"
          )

        # Actualizar directorio de cliente
        if nombre_cliente in st.session_state.customers["nombre"].values:
          idx_c = st.session_state.customers[
              st.session_state.customers["nombre"] == nombre_cliente
          ].index[0]
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
              [st.session_state.customers, pd.DataFrame([nuevo_c])],
              ignore_index=True,
          )

# MÓDULO 3: CONTROL DE INVENTARIO
elif menu == "📦 Control de Inventario":
  st.header("📦 Control de Stock e Inventario")
  st.dataframe(st.session_state.inventory, use_container_width=True)

  st.markdown("---")
  st.subheader("➕ Agregar Producto al Inventario")
  with st.form("form_nuevo_inv"):
    i_nombre = st.text_input("Nombre Identificador del Jabón")
    i_tipo_piel = st.selectbox("Tipo de Piel", list(MAPA_BOTANICO.keys()))
    i_aceite = st.selectbox(
        "Aceite Esencial", MAPA_BOTANICO[i_tipo_piel]["aceites"]
    )
    i_aroma = st.selectbox("Aroma", MAPA_BOTANICO[i_tipo_piel]["aromas"])
    i_tamano = st.selectbox(
        "Tamaño", ["Pequeño (50g)", "Mediano (100g)", "Grande (150g)"]
    )
    i_precio = st.number_input("Precio Venta (₡)", value=2000, step=100)
    i_costo = st.number_input("Costo Producción (₡)", value=850, step=50)
    i_stock = st.number_input("Stock Inicial (Unidades)", value=10, min_value=0)

    btn_inv = st.form_submit_button("Añadir al Inventario")
    if btn_inv:
      nuevo_item = {
          "id": str(int(datetime.datetime.now().timestamp())),
          "nombre": i_nombre if i_nombre else f"{i_aceite} ({i_tamano})",
          "tipo_piel": i_tipo_piel,
          "aceite_esencial": i_aceite,
          "aroma": i_aroma,
          "tamano": i_tamano,
          "precio_colones": i_precio,
          "costo_est_colones": i_costo,
          "stock": i_stock,
      }
      st.session_state.inventory = pd.concat(
          [st.session_state.inventory, pd.DataFrame([nuevo_item])],
          ignore_index=True,
      )
      st.success(f"✔️ Producto '{nuevo_item['nombre']}' añadido al inventario.")

# MÓDULO 4: DIRECTORIO DE CLIENTES
elif menu == "👥 Directorio de Clientes":
  st.header("👥 Directorio Consolidado de Clientes")
  st.dataframe(st.session_state.customers, use_container_width=True)

# MÓDULO 5: CONEXIÓN GOOGLE DRIVE / SHEETS
elif menu == "☁️ Conexión Google Drive / Sheets":
  st.header("☁️ Sincronización Automática con Google Drive")
  if sh_drive:
    st.success(
        "✅ ¡Conexión exitosa con la hoja de cálculo **'Control Jabones"
        " Artesanales'** en Google Drive!"
    )
  else:
    st.warning(
        "⚠️ No hay conexión activa con Google Drive. Asegúrate de haber"
        " pegado el bloque TOML correctamente en la sección Secrets de"
        " Streamlit Cloud."
    )

  st.info(
      "💡 Las respuestas, ventas y ganancias quedan almacenadas en tiempo real"
      " sin requerir archivos locales."
  )
