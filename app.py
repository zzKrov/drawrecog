import base64
import io
import os
import numpy as np
from openai import OpenAI
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL (LAYOUT WIDE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tablero Creativo de Bocetos // Krov Industries",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# LÍNEA BASE VISUAL: GRADIENTES CIBER-NEÓN Y FLUIDOS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #05020c !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* 1. Malla continua de gradientes vivos */
.stApp {
    background: linear-gradient(135deg, #05020c 0%, #170428 30%, #290520 60%, #060210 100%) !important;
    background-size: 300% 300% !important;
    animation: neonShift 18s ease infinite alternate !important;
}

@keyframes neonShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Fluidos orgánicos de neón */
.fluid-neon-1 {
    position: fixed;
    top: 15%;
    left: -120px;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, rgba(255, 0, 127, 0.16) 0%, rgba(0, 243, 255, 0.04) 55%, transparent 75%);
    border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
    filter: blur(85px);
    animation: neonDrift1 20s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

.fluid-neon-2 {
    position: fixed;
    bottom: 5%;
    right: -100px;
    width: 560px;
    height: 560px;
    background: radial-gradient(circle, rgba(0, 243, 255, 0.14) 0%, rgba(255, 0, 127, 0.03) 55%, transparent 75%);
    border-radius: 60% 40% 50% 50% / 40% 50% 60% 50%;
    filter: blur(90px);
    animation: neonDrift2 24s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

@keyframes neonDrift1 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(120px, 70px) scale(1.15); }
    100% { transform: translate(40px, 140px) scale(0.95); }
}

@keyframes neonDrift2 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-110px, -80px) scale(1.2); }
    100% { transform: translate(-30px, -120px) scale(0.9); }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00f3ff;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 30px rgba(0, 243, 255, 0.45);
}

.sub-lead {
    text-align: center;
    color: #00f3ff;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
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
    border-radius: 12px !important;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.8), 0 0 25px rgba(255, 0, 127, 0.25) !important;
    transition: all 0.3s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #00f3ff !important;
    box-shadow: 0 18px 55px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 243, 255, 0.45) !important;
}

div.stButton > button {
    background: linear-gradient(135deg, #ff007f 0%, #7928ca 50%, #00f3ff 100%) !important;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 25px rgba(255, 0, 127, 0.4) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 40px rgba(0, 243, 255, 0.8) !important;
}

.response-box {
    background: rgba(18, 9, 36, 0.85);
    border-left: 4px solid #00f3ff;
    padding: 22px;
    border-radius: 10px;
    margin-top: 20px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6);
}
</style>

<div class="fluid-neon-1"></div>
<div class="fluid-neon-2"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BARRA LATERAL (HERRAMIENTAS DE TRAZO)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### Configuración de Trazo")
    api_key_input = st.text_input(
        "Clave de API de OpenAI",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", "")
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.markdown("---")
    stroke_width = st.slider("Calibre del lápiz", min_value=2, max_value=30, value=7)
    stroke_color = st.color_picker("Tinta de trazo", "#000000")
    bg_color = st.color_picker("Color del plano", "#ffffff")

st.markdown('<div class="brand-signature">Krov Industries · Visión Creativa</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Tablero Creativo de Bocetos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja una figura o concepto y la IA deducirá el significado en tiempo real</div>', unsafe_allow_html=True)

_, col_c, _ = st.columns([1, 4.5, 1])

with col_c:
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 127, 0.2)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=380,
        width=680,
        drawing_mode="freedraw",
        key="creative_sketch_canvas",
    )
    
    st.write("")
    analyze_button = st.button("Identificar boceto con IA", use_container_width=True)

def process_and_encode_canvas(image_data: np.ndarray) -> str:
    img = Image.fromarray(image_data.astype("uint8"), "RGBA")
    buffered = io.BytesIO()
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3])
    rgb_img.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

if analyze_button:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.warning("Introduce una clave de API de OpenAI en la barra lateral para continuar.")
    elif canvas_result.image_data is None or not np.any(canvas_result.image_data[:, :, 3] > 0):
        st.warning("El lienzo parece estar vacío. Realiza un trazo antes de solicitar el análisis.")
    else:
        with col_c:
            with st.spinner("Interpretando trazos con GPT-4o-mini..."):
                try:
                    b64_img = process_and_encode_canvas(canvas_result.image_data)
                    client = OpenAI(api_key=api_key)
                    prompt_text = (
                        "Interpreta de forma creativa, estructurada y en español qué representa este dibujo. "
                        "Describe los detalles identificados y explica tu deducción con claridad."
                    )
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt_text},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                                ]
                            }
                        ],
                        max_tokens=500
                    )
                    st.markdown(
                        f"""
                        <div class="response-box">
                            <h4 style="color:#00f3ff; margin-top:0;">Interpretación del Boceto:</h4>
                            <div style="font-size:1.02rem; line-height:1.6;">{resp.choices[0].message.content}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Error al conectar con la API de OpenAI: {e}")
