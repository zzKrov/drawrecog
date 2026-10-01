import base64
import io
import os
import numpy as np
from openai import OpenAI
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Layout Wide)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Tablero Inteligente Neon-AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILOS CSS HÍPER-SATURADOS, EFECTOS HOVER Y RESPONSIVIDAD
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Rajdhani:wght@500;700&display=swap');

    /* Fondo principal y tipografía */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a0826 0%, #080312 60%, #020108 100%);
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Título con gradiente híper-saturado y brillo de neón */
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff007f, #00f3ff, #ffe600, #ff007f);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite, glow 2s ease-in-out infinite alternate;
        margin-bottom: 0.2rem;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes glow {
        from { filter: drop-shadow(0 0 10px rgba(255, 0, 127, 0.7)); }
        to { filter: drop-shadow(0 0 25px rgba(0, 243, 255, 0.9)); }
    }

    .neon-subtitle {
        text-align: center;
        color: #00f3ff;
        font-size: 1.25rem;
        letter-spacing: 2px;
        margin-bottom: 1.8rem;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.8);
    }

    /* Contenedor del lienzo centrado y ocupando ~80% */
    .canvas-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        padding: 12px;
        background: rgba(15, 5, 29, 0.7);
        border: 2px solid #ff007f;
        border-radius: 24px;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.6), inset 0 0 15px rgba(0, 243, 255, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .canvas-container:hover {
        transform: translateY(-4px) scale(1.008);
        border-color: #00f3ff;
        box-shadow: 0 0 35px rgba(0, 243, 255, 0.9), inset 0 0 25px rgba(255, 0, 127, 0.5);
    }

    /* Adaptabilidad del canvas en pantallas pequeñas */
    div[data-testid="stCanvas"] > canvas {
        border-radius: 18px !important;
        max-width: 100% !important;
        height: auto !important;
    }

    /* Botón de análisis con efecto visual ultra-saturado */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 50%, #00f3ff 100%);
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 0.8rem 2rem;
        border: none;
        border-radius: 14px;
        letter-spacing: 2px;
        cursor: pointer;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.75);
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        transform: scale(1.03) translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 243, 255, 1), 0 0 45px rgba(255, 0, 127, 0.9);
        color: #ffff00;
    }

    /* Tarjeta de Respuesta */
    .response-box {
        background: rgba(18, 9, 36, 0.85);
        border-left: 5px solid #00f3ff;
        border-right: 5px solid #ff007f;
        padding: 22px;
        border-radius: 16px;
        margin-top: 25px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
        font-size: 1.15rem;
        line-height: 1.6;
        animation: fadeIn 0.5s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Sidebar Personalizada */
    section[data-testid="stSidebar"] {
        background: #0a0414;
        border-right: 1px solid rgba(255, 0, 127, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# CABECERA VISUAL
# ---------------------------------------------------------
st.markdown('<h1 class="neon-title">⚡ TABLERO INTELIGENTE ⚡</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="neon-subtitle">DIBUJA TU BOCETO • LA IA RECONOCERÁ TU CREACIÓN EN TIEMPO REAL</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# BARRA LATERAL (CONTROLES Y CONFIGURACIÓN)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Centro de Control")
    api_key_input = st.text_input(
        "Clave de API de OpenAI",
        type="password",
        placeholder="sk-proj-...",
        help="Introduce tu API key para habilitar la visión por IA.",
    )
    
    st.markdown("---")
    st.markdown("### 🖌️ Parámetros del Trazo")
    stroke_width = st.slider("Grosor del lápiz", min_value=2, max_value=35, value=7)
    stroke_color = st.color_picker("Color de trazo", "#000000")
    bg_color = st.color_picker("Color del lienzo", "#FFFFFF")
    
    st.markdown("---")
    st.info("💡 **Tip:** Traza formas simples o complejas y deja que GPT-4o-mini interprete cada detalle.")

# ---------------------------------------------------------
# ÁREA PRINCIPAL: LIENZO CENTRADO AL ~80%
# ---------------------------------------------------------
# 10% margen izq | 80% centro | 10% margen der
col_left, col_canvas, col_right = st.columns([1, 8, 1])

with col_canvas:
    st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 127, 0.2)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=480,
        width=920,
        drawing_mode="freedraw",
        key="super_canvas",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    analyze_button = st.button("🚀 IDENTIFICAR BOCETO", use_container_width=True)

# ---------------------------------------------------------
# PROCESAMIENTO Y RECONOCIMIENTO CON OPENAI
# ---------------------------------------------------------
def process_and_encode_canvas(image_data: np.ndarray) -> str:
    """Convierte la matriz de píxeles del canvas a Base64 en memoria."""
    img = Image.fromarray(image_data.astype("uint8"), "RGBA")
    buffered = io.BytesIO()
    # Convertir a RGB (fondo blanco para compatibilidad si hay transparencias)
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3])
    rgb_img.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


if analyze_button:
    api_key = api_key_input or os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        st.warning("⚠️ Debes proporcionar una API Key de OpenAI en la barra lateral para continuar.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo en el lienzo antes de solicitar el análisis.")
    else:
        # Validar si el usuario dibujó algo (comprobar si hay trazos alfa > 0)
        has_drawing = np.any(canvas_result.image_data[:, :, 3] > 0)
        
        if not has_drawing:
            st.warning("⚠️ El lienzo parece estar vacío. ¡Haz un trazo primero!")
        else:
            with col_canvas:
                with st.spinner("🔮 Decodificando trazos con GPT-4o-mini..."):
                    try:
                        base64_image = process_and_encode_canvas(canvas_result.image_data)
                        client = OpenAI(api_key=api_key)

                        prompt_text = (
                            "Eres un experto crítico e intérprete de bocetos rápidos. "
                            "Analiza la siguiente imagen dibujada por el usuario. "
                            "Identifica con precisión qué representa el boceto, sus detalles clave, "
                            "y explica tu deducción de forma creativa, clara y en español."
                        )

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_text},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}",
                                                "detail": "high"
                                            },
                                        },
                                    ],
                                }
                            ],
                            max_tokens=600,
                            temperature=0.4,
                        )

                        result_content = response.choices[0].message.content

                        st.markdown(
                            f"""
                            <div class="response-box">
                                <h3 style="color: #00f3ff; margin-top:0;">🤖 Interpretación del Boceto:</h3>
                                {result_content}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.error(f"❌ Error al conectar con OpenAI: {str(e)}")
