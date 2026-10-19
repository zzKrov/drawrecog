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
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# ESTADO DEL LIENZO PARA RESET LIMPIO
# ------------------------------------------------------------
if "sketch_canvas_ver" not in st.session_state:
    st.session_state.sketch_canvas_ver = 0

# =========================================================
# ESTILOS VISUALES: CIBER-NEÓN, FONDO LÍQUIDO Y CENTRADO
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

/* Fondo líquido acelerado por GPU */
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
    max-width: 760px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    margin: 0 auto !important;
}

/* Centrado simétrico del lienzo */
div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 680px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(255, 0, 127, 0.45) !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 0, 127, 0.2) !important;
    transition: all 0.25s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #00f3ff !important;
    box-shadow: 0 14px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 243, 255, 0.4) !important;
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

.resp-box {
    background: rgba(18, 9, 36, 0.85);
    border-left: 4px solid #00f3ff;
    padding: 20px;
    border-radius: 8px;
    margin-top: 18px;
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuración")
    api_key = st.text_input("OpenAI API Key:", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    stroke_w = st.slider("Grosor de lápiz:", 2, 30, 8)
    stroke_c = st.color_picker("Color de trazo:", "#000000")
    bg_c = st.color_picker("Color de fondo:", "#ffffff")

st.markdown('<div class="brand-signature">Krov Industries · Visión</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Tablero de Bocetos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja una figura o concepto y la IA interpretará su significado</div>', unsafe_allow_html=True)

canvas_data = st_canvas(
    fill_color="rgba(255, 0, 127, 0.2)",
    stroke_width=stroke_w,
    stroke_color=stroke_c,
    background_color=bg_c,
    height=380,
    width=680,
    drawing_mode="freedraw",
    key=f"boceto_canvas_v{st.session_state.sketch_canvas_ver}",
)

st.write("")
b_c1, b_c2 = st.columns([3, 1])
with b_c1:
    analizar_btn = st.button("Identificar boceto", type="primary", use_container_width=True)
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
    # Verificación explícita que previene el error openai.OpenAIError
    if not key_val:
        st.warning("Introduce tu clave de API de OpenAI en la barra lateral para continuar.")
    elif canvas_data.image_data is None or not np.any(canvas_data.image_data[:, :, 3] > 0):
        st.warning("Dibuja una figura antes de solicitar el análisis.")
    else:
        with st.spinner("Interpretando trazos..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                b64 = encode_canvas(canvas_data.image_data)
                prompt = "Identifica en español qué representa este dibujo. Explica brevemente los detalles observados."
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                    max_tokens=400
                )
                st.markdown(
                    f'<div class="resp-box"><b>Interpretación:</b><br>{resp.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Error al conectar con OpenAI: {e}")
