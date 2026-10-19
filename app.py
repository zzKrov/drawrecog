import base64
import io
import os
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# =========================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR)
# =========================================================
st.set_page_config(
    page_title="Estudio de Bocetos // Krov Industries",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "ver_boceto" not in st.session_state:
    st.session_state.ver_boceto = 0

# =========================================================
# ESTILOS: ESTUDIO DE ARTE CIBER-NEÓN CON PALETA FLOTANTE
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #06020c 0%, #1a042a 40%, #28031d 70%, #06020c 100%) !important;
    background-size: 300% 300% !important;
    animation: neonStudioShift 15s ease infinite alternate !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

@keyframes neonStudioShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #ff007f;
    text-transform: uppercase;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(255, 0, 127, 0.45);
}

.sub-lead {
    text-align: center;
    color: #cbd5e1;
    font-size: 0.95rem;
    margin-bottom: 1.4rem;
}

.block-container {
    max-width: 820px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}

/* Paleta superior estilo Photoshop */
.tools-banner {
    background: rgba(18, 9, 32, 0.92);
    border: 1px solid rgba(255, 0, 127, 0.35);
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 14px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}

/* Centrado simétrico del lienzo */
div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 720px !important;
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
    box-shadow: 0 16px 50px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 243, 255, 0.45) !important;
}

/* Botones con brillo neón */
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

.critique-card {
    background: rgba(18, 9, 36, 0.92);
    border-left: 4px solid #00f3ff;
    padding: 22px;
    border-radius: 8px;
    margin-top: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    line-height: 1.65;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-signature">Krov Industries · Visión Creativa</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Estudio de Bocetos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Lienzo de dibujo artístico e interpretación visual mediante inteligencia artificial</div>', unsafe_allow_html=True)

# BARRA DE HERRAMIENTAS TIPO PHOTOSHOP
st.markdown('<div class="tools-banner">', unsafe_allow_html=True)
c_tool, c_color, c_fill, c_size = st.columns([1.6, 0.9, 0.9, 1.1])

with c_tool:
    herramienta = st.selectbox(
        "Herramienta activa:",
        ["✏️ Lápiz libre", "📏 Línea recta", "⏹️ Rectángulo", "⭕ Círculo", "🔺 Polígono / Triángulo", "🧹 Borrador"]
    )
with c_color:
    color_trazo = st.color_picker("Tinta:", "#000000")
with c_fill:
    relleno_on = st.checkbox("Relleno", value=False)
with c_size:
    grosor = st.slider("Calibre:", 2, 35, 6)
st.markdown('</div>', unsafe_allow_html=True)

if "Lápiz" in herramienta:
    modo = "freedraw"
    tinta = color_trazo
elif "Línea" in herramienta:
    modo = "line"
    tinta = color_trazo
elif "Rectángulo" in herramienta:
    modo = "rect"
    tinta = color_trazo
elif "Círculo" in herramienta:
    modo = "circle"
    tinta = color_trazo
elif "Polígono" in herramienta:
    modo = "polygon"
    tinta = color_trazo
else:
    modo = "freedraw"
    tinta = "#ffffff"

color_fill = color_trazo + "55" if (relleno_on and "Borrador" not in herramienta) else "rgba(0,0,0,0)"

canvas_data = st_canvas(
    fill_color=color_fill,
    stroke_width=grosor,
    stroke_color=tinta,
    background_color="#ffffff",
    height=380,
    width=720,
    drawing_mode=modo,
    key=f"boceto_art_v{st.session_state.ver_boceto}",
)

st.write("")
b1, b2 = st.columns([3, 1])
with b1:
    btn_analizar = st.button("Interpretar boceto con IA", type="primary", use_container_width=True)
with b2:
    btn_limpiar = st.button("Limpiar lienzo", type="secondary", use_container_width=True)

if btn_limpiar:
    st.session_state.ver_boceto += 1
    if "analisis_boceto" in st.session_state:
        del st.session_state.analisis_boceto
    st.rerun()

def codificar_canvas(img_arr):
    img = Image.fromarray(img_arr.astype("uint8"), "RGBA")
    buf = io.BytesIO()
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[3])
    rgb.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

if btn_analizar:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        st.warning("Configura tu variable de entorno OPENAI_API_KEY para habilitar la visión por computadora.")
    elif canvas_data.image_data is None or not np.any(canvas_data.image_data[:, :, 3] > 0):
        st.warning("El lienzo está vacío. Realiza un trazo antes de solicitar la interpretación.")
    else:
        prog = st.progress(0, text="Codificando matriz visual...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prog.progress(40, text="Analizando composición y trazos...")
            b64 = codificar_canvas(canvas_data.image_data)
            prompt = (
                "Eres un crítico experto e intérprete visual de bocetos rápidos. "
                "Analiza este dibujo de forma creativa, clara y en español natural. "
                "Identifica qué representa, sus detalles clave y describe tu deducción artística."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                max_tokens=450
            )
            prog.progress(100, text="Interpretación completada.")
            st.session_state.analisis_boceto = resp.choices[0].message.content
        except Exception as e:
            st.error(f"Error al conectar con OpenAI: {e}")

if "analisis_boceto" in st.session_state:
    st.markdown(f'<div class="critique-card"><h4>Evaluación Artística del Boceto:</h4><br>{st.session_state.analisis_boceto}</div>', unsafe_allow_html=True)
