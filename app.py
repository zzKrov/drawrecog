import base64
import io
import os
import numpy as np
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from streamlit_drawable_canvas import st_canvas

# =========================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR)
# =========================================================
st.set_page_config(
    page_title="Tablero de Bocetos // Krov Industries",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "ver_boceto" not in st.session_state:
    st.session_state.ver_boceto = 0

# =========================================================
# ESTILOS: ESTUDIO DE ARTE CIBER-NEÓN
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .block-container {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

body {
    background-color: #06020c !important;
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

# Fondo interactivo neón animado en Canvas (Cero Lag)
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        if (pWin.__SKETCH_BG_INIT__) return;
        pWin.__SKETCH_BG_INIT__ = true;

        let canvas = pDoc.getElementById('sketch-fluid-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'sketch-fluid-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;background:#06020c;';
            pDoc.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        let w = canvas.width = pWin.innerWidth;
        let h = canvas.height = pWin.innerHeight;

        pWin.addEventListener('resize', () => {
            w = canvas.width = pWin.innerWidth;
            h = canvas.height = pWin.innerHeight;
        });

        const orbs = [
            { x: w * 0.15, y: h * 0.3, r: 260, vx: 0.5, vy: 0.4, color: 'rgba(255, 0, 127, 0.18)' },
            { x: w * 0.8, y: h * 0.4, r: 280, vx: -0.4, vy: 0.5, color: 'rgba(0, 243, 255, 0.16)' },
            { x: w * 0.5, y: h * 0.75, r: 250, vx: 0.4, vy: -0.5, color: 'rgba(121, 40, 202, 0.15)' }
        ];

        function loop() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#06020c';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of orbs) {
                b.x += b.vx;
                b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const g = ctx.createRadialGradient(b.x, b.y, 10, b.x, b.y, b.r);
                g.addColorStop(0, b.color);
                g.addColorStop(1, 'transparent');
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            }
            requestAnimationFrame(loop);
        }
        loop();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · Visión Creativa</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Tablero de Bocetos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Estudio de dibujo libre con barra de herramientas e interpretación artística por IA</div>', unsafe_allow_html=True)

# CAMPO DE CLAVE OPENAI DIRECTO EN PANTALLA
c_key, c_info = st.columns([1.5, 1])
with c_key:
    api_key_input = st.text_input(
        "Clave de API de OpenAI:",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-..."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

# BARRA DE HERRAMIENTAS DIRECTA EN COLUMNAS (SIN CONTENEDOR VACÍO)
c_tool, c_color, c_fill, c_size = st.columns([1.6, 0.9, 0.9, 1.1])

with c_tool:
    herramienta = st.selectbox(
        "Herramienta activa:",
        ["✏️ Lápiz libre", "📏 Línea recta", "⏹️ Rectángulo", "⭕ Círculo", "🔺 Triángulo / Polígono", "🧹 Borrador"]
    )
with c_color:
    color_trazo = st.color_picker("Tinta:", "#000000")
with c_fill:
    relleno_on = st.checkbox("Relleno", value=False)
with c_size:
    grosor = st.slider("Calibre:", 2, 35, 6)

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
elif "Triángulo" in herramienta:
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
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Introduce tu clave de API de OpenAI en el campo superior.")
    elif canvas_data.image_data is None or not np.any(canvas_data.image_data[:, :, 3] > 0):
        st.warning("El lienzo está en blanco. Traza un dibujo antes de solicitar el análisis.")
    else:
        prog = st.progress(0, text="Codificando matriz visual...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key_val)
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
