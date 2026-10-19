import base64
import io
import os
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Tablero de Bocetos // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# ESTADO DEL LIENZO PARA RESET LIMPIO
# ------------------------------------------------------------
if "sketch_canvas_ver" not in st.session_state:
    st.session_state.sketch_canvas_ver = 0

# =========================================================
# ESTILOS VISUALES: CIBER-NEÓN Y BARRA PHOTOSHOP
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #06020c !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

/* Fondo líquido animado en GPU */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(255, 0, 127, 0.16) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(0, 243, 255, 0.16) 0%, transparent 45%),
        linear-gradient(135deg, #06020c 0%, #150320 50%, #06020c 100%) !important;
    background-size: 200% 200% !important;
    animation: neonLava 14s ease infinite alternate !important;
}

@keyframes neonLava {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 100%; }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00f3ff;
    text-transform: uppercase;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(0, 243, 255, 0.4);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.4rem;
}

.block-container {
    max-width: 780px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}

/* Centrado simétrico del lienzo */
div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 700px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(255, 0, 127, 0.45) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8), 0 0 25px rgba(255, 0, 127, 0.2) !important;
    transition: all 0.25s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #00f3ff !important;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 243, 255, 0.4) !important;
}

/* Barra de herramientas estilo Photoshop */
.ps-toolbar {
    background: rgba(18, 9, 32, 0.9);
    border: 1px solid rgba(0, 243, 255, 0.3);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 12px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.6);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff007f 0%, #7928ca 50%, #00f3ff 100%) !important;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.4) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(0, 243, 255, 0.75) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(18, 20, 35, 0.85) !important;
    color: #e4e4e7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
    padding: 0.8rem 1.6rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

.critique-box {
    background: rgba(18, 9, 36, 0.88);
    border-left: 4px solid #00f3ff;
    padding: 20px;
    border-radius: 8px;
    margin-top: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-signature">Krov Industries · Crítica Visual</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Tablero de Bocetos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Estudio de dibujo libre con barra de herramientas e interpretación artística por IA</div>', unsafe_allow_html=True)

# BARRA DE HERRAMIENTAS TIPO PHOTOSHOP
st.markdown('<div class="ps-toolbar">', unsafe_allow_html=True)
t1, t2, t3, t4 = st.columns([1.6, 1, 1, 1])

with t1:
    herramienta = st.selectbox(
        "Herramienta:",
        ["✏️ Lápiz libre", "📏 Línea recta", "⏹️ Rectángulo", "⭕ Círculo", "🔺 Triángulo / Polígono", "🧹 Borrador"]
    )
with t2:
    color_trazo = st.color_picker("Tinta:", "#000000")
with t3:
    relleno_on = st.checkbox("Relleno", value=False)
with t4:
    grosor = st.slider("Calibre:", 2, 35, 6)

st.markdown('</div>', unsafe_allow_html=True)

# Mapeo de herramientas de Fabric.js
if "Lápiz" in herramienta:
    modo_dibujo = "freedraw"
    color_usado = color_trazo
elif "Línea" in herramienta:
    modo_dibujo = "line"
    color_usado = color_trazo
elif "Rectángulo" in herramienta:
    modo_dibujo = "rect"
    color_usado = color_trazo
elif "Círculo" in herramienta:
    modo_dibujo = "circle"
    color_usado = color_trazo
elif "Triángulo" in herramienta:
    modo_dibujo = "polygon"
    color_usado = color_trazo
else:  # Borrador
    modo_dibujo = "freedraw"
    color_usado = "#ffffff"

color_relleno = color_trazo + "55" if (relleno_on and "Borrador" not in herramienta) else "rgba(0,0,0,0)"

canvas_data = st_canvas(
    fill_color=color_relleno,
    stroke_width=grosor,
    stroke_color=color_usado,
    background_color="#ffffff",
    height=380,
    width=700,
    drawing_mode=modo_dibujo,
    key=f"boceto_canvas_v{st.session_state.sketch_canvas_ver}",
)

st.write("")
b_c1, b_c2 = st.columns([3, 1])
with b_c1:
    analizar_btn = st.button("Analizar boceto con IA", type="primary", use_container_width=True)
with b_c2:
    limpiar_btn = st.button("Limpiar lienzo", type="secondary", use_container_width=True)

if limpiar_btn:
    st.session_state.sketch_canvas_ver += 1
    st.rerun()

def encode_canvas(img_arr):
    img = Image.fromarray(img_arr.astype("uint8"), "RGBA")
    buf = io.BytesIO()
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[3])
    rgb.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

if analizar_btn:
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Introduce tu clave de API de OpenAI en el entorno o introduce una clave válida.")
    elif canvas_data.image_data is None or not np.any(canvas_data.image_data[:, :, 3] > 0):
        st.warning("El lienzo está en blanco. Traza un dibujo antes de solicitar el análisis.")
    else:
        with st.spinner("El crítico de arte IA está analizando tu boceto..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                b64 = encode_canvas(canvas_data.image_data)
                prompt = (
                    "Eres un crítico experto e intérprete visual de bocetos rápidos. "
                    "Analiza este dibujo de forma creativa, clara y en español natural. "
                    "Identifica con precisión qué representa, sus detalles clave y describe tu deducción artística."
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                    max_tokens=450
                )
                st.markdown(
                    f'<div class="critique-box"><h4>Evaluación Crítica del Boceto:</h4><br>{resp.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error al conectar con OpenAI: {e}")
