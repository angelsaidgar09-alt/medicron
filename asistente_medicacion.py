import base64
import html
from pathlib import Path

import streamlit as st


# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="MediCrón | Asistente de Medicación Crónica", page_icon="🏥", layout="centered")

# Logo incrustado como data URI: no depende de servir archivos estáticos,
# así funciona igual en local y en la nube, y no puede dar error 404.
# Se busca en varias ubicaciones porque al subir a GitHub es fácil que la imagen
# quede suelta en la raíz del repositorio en vez de dentro de static/.
# Si no aparece en ninguna, la app sigue funcionando y muestra el nombre como texto.
NOMBRES_LOGO = ("static/logo_medicron.png", "logo_medicron.png")


def _buscar_logo() -> Path | None:
    for carpeta in (Path(__file__).parent, Path.cwd()):
        for nombre in NOMBRES_LOGO:
            ruta = carpeta / nombre
            if ruta.is_file():
                return ruta
    return None


RUTA_LOGO = _buscar_logo()
HAY_LOGO = RUTA_LOGO is not None
if HAY_LOGO:
    try:
        LOGO_URL = "data:image/png;base64," + base64.b64encode(RUTA_LOGO.read_bytes()).decode("ascii")
    except OSError:
        HAY_LOGO = False
        LOGO_URL = ""
else:
    LOGO_URL = ""

# 2. ESTILOS CSS PARA COLORES INTERACTIVOS Y DISEÑO AMIGABLE
# El fondo y los colores base se configuran en .streamlit/config.toml.
# Aquí solo se estiliza el botón (con su key) y la tarjeta de resultados.
st.html("""
    <style>
    /* Estilo del botón principal (key="btn_generar") */
    .st-key-btn_generar button {
        background-color: #0077b6;
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
    }
    .st-key-btn_generar button:hover {
        background-color: #023e8a;
        color: #ffffff;
        transform: scale(1.02);
    }
    .st-key-btn_generar button:focus-visible {
        outline: 3px solid #90e0ef;
        outline-offset: 2px;
    }
    /* Tarjeta de resultados dinámica */
    .tarjeta-resultado {
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    /* Encabezado adaptable al tema claro/oscuro sin re-ejecutar el script.
       light-dark() usa el color-scheme que Streamlit aplica al contenedor. */
    .medi-eslogan {
        color: inherit;
        color: light-dark(#4a5568, #cbd5e1);
    }
    /* Logo: en modo oscuro se superpone una capa blanca con la silueta del logo,
       así el logo cambia a blanco sin fondo y sin re-ejecutar el script. */
    .logo-medi {
        position: relative;
        display: block;
        width: 220px;
        margin: 0 auto;
    }
    .logo-medi img {
        display: block;
        width: 100%;
        height: auto;
    }
    .logo-blanco {
        position: absolute;
        inset: 0;
        pointer-events: none;
        background-color: transparent;
        background-color: light-dark(transparent, #ffffff);
        -webkit-mask: url("__LOGO__") center / contain no-repeat;
        mask: url("__LOGO__") center / contain no-repeat;
    }
    /* Transición de carga al abrir la web (solo la primera vez) */
    .splash {
        position: fixed;
        inset: 0;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 18px;
        background: light-dark(#f4f8fb, #0e1726);
        animation: splash-salir 1.7s ease forwards;
        pointer-events: none;
    }
    .splash-logo {
        position: relative;
        width: 170px;
        aspect-ratio: 421 / 261;
        animation: splash-latido 1.1s ease-in-out infinite alternate;
    }
    .splash-logo img {
        display: block;
        width: 100%;
        height: auto;
    }
    .splash-texto {
        margin: 0;
        font-size: 16px;
        letter-spacing: 0.3px;
        color: light-dark(#4a5568, #cbd5e1);
    }
    .splash-barra {
        width: 170px;
        height: 4px;
        border-radius: 999px;
        overflow: hidden;
        background: light-dark(#dbe9f4, #1c2a44);
    }
    .splash-barra span {
        display: block;
        height: 100%;
        width: 45%;
        border-radius: inherit;
        background: light-dark(#0077b6, #00b4d8);
        animation: splash-cargar 1s ease-in-out infinite;
    }
    @keyframes splash-salir {
        0%, 68% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    @keyframes splash-latido {
        from { transform: scale(0.96); }
        to { transform: scale(1.02); }
    }
    @keyframes splash-cargar {
        0% { transform: translateX(-110%); }
        100% { transform: translateX(260%); }
    }
    </style>
""".replace("__LOGO__", LOGO_URL or "none"))

# 3. LOGO DE LA APLICACIÓN (imagen en static/, servida por Streamlit)
# En modo oscuro, .logo-blanco superpone una silueta blanca del mismo logo.

# Transición de carga al abrir la web (solo la primera vez por sesión)
if not st.session_state.get("intro_mostrada"):
    if HAY_LOGO:
        marca_splash = (
            "<img src='" + LOGO_URL + "' alt=''>"
            "<span class='logo-blanco'></span>"
        )
    else:
        marca_splash = (
            "<span style='font-size: 34px; font-weight: 700; letter-spacing: 1px;'>"
            "MediCrón</span>"
        )
    st.html(
        "<div class='splash' aria-hidden='true'>"
        "<div class='splash-logo'>" + marca_splash + "</div>"
        "<p class='splash-texto'>Preparando tu guía…</p>"
        "<div class='splash-barra'><span></span></div>"
        "</div>"
    )
    st.session_state["intro_mostrada"] = True

# Encabezado apilado y centrado: logo (incluye el nombre) y eslogan
with st.container(horizontal_alignment="center"):
    if HAY_LOGO:
        st.html(
            "<div class='logo-medi'>"
            "<img src='" + LOGO_URL + "' alt='Logo MediCrón'>"
            "<span class='logo-blanco' aria-hidden='true'></span>"
            "</div>"
        )
    else:
        st.html(
            "<h1 style='margin: 0; font-size: 42px; letter-spacing: 1px;'>MediCrón</h1>"
        )
    st.html(
        "<p class='medi-eslogan' style='font-size: 16px; margin-top: 4px; text-align: center;'>"
        "Asistente Comunitario para Pacientes Crónicos</p>"
    )

st.divider()

# 4. BASE DE CONOCIMIENTO CON IDENTIDAD DE COLOR POR CONDICIÓN
BASE_MEDICAMENTOS = {
    "Hipertensión Arterial": {
        "nombre": "Losartán",
        "presentacion": "Tabletas",
        "efectos_adversos": "Al principio podrías sentir mareos ligeros o fatiga mientras tu cuerpo se adapta. No te asustes, es parte del proceso.",
        "horario": "Generalmente una vez al día, preferiblemente por la mañana según lo indique tu médico.",
        "color_fondo": "#ffe5ec",   # Rosa suave (asociado al corazón/presión)
        "color_borde": "#ff4d6d"
    },
    "Diabetes Tipo 2": {
        "nombre": "Metformina",
        "presentacion": "Tabletas",
        "efectos_adversos": "Suele causar molestias estomacales leves o náuseas los primeros días. Esto mejora con el tiempo.",
        "horario": "Debe tomarse junto con las comidas principales para proteger tu estómago.",
        "color_fondo": "#e0fbfc",   # Azul celeste (color mundial de la diabetes)
        "color_borde": "#00b4d8"
    },
    "Asma Crónica": {
        "nombre": "Salbutamol (Albuterol)",
        "presentacion": "Inhalador de suspensión aerosol",
        "efectos_adversos": "Es normal sentir temblores leves en las manos o el corazón acelerado justo después de usarlo. Pasará en unos minutos.",
        "horario": "Se utiliza únicamente ante crisis o dificultad respiratoria según tu plan médico.",
        "color_fondo": "#e8f8f5",   # Verde menta (asociado al aire y respiración)
        "color_borde": "#2ec4b6"
    }
}

# 5. INTERFAZ DE USUARIO (Formulario de Entrada)
st.write("👋 *Hola.* Completa los datos del paciente para generar su guía visual:")

nombre = st.text_input("Nombre del paciente:", placeholder="Ej.: María González")

col1, col2 = st.columns(2)

with col1:
    enfermedad = st.selectbox(
        "Seleccione la enfermedad crónica:",
        ["Seleccione una opción", "Hipertensión Arterial", "Diabetes Tipo 2", "Asma Crónica"]
    )
    edad = st.number_input("Edad del paciente (años):", min_value=1, max_value=120, value=45, step=1)

with col2:
    peso = st.number_input("Peso del paciente (kg):", min_value=3.0, max_value=250.0, value=70.0, step=0.1)
    altura = st.number_input("Altura del paciente (cm):", min_value=50.0, max_value=250.0, value=170.0, step=0.5)

st.write("")
procesar = st.button("🤖 Generar Orientación Personalizada", key="btn_generar", width="stretch")

# 6. MOTOR DE INFERENCIA (Lógica de IA basada en Reglas)
if procesar:
    if enfermedad == "Seleccione una opción":
        st.error("⚠️ Por favor, seleccione una enfermedad crónica válida para continuar.")
    elif not nombre.strip():
        st.error("⚠️ Por favor, ingrese el nombre del paciente para continuar.")
    else:
        med = BASE_MEDICAMENTOS[enfermedad]
        nombre_paciente = html.escape(nombre.strip())

        orientacion_calculada = ""
        observacion_ia = ""

        if enfermedad == "Hipertensión Arterial":
            if edad >= 65:
                orientacion_calculada = "Requiere evaluación geriátrica para definir esquema inicial."
                observacion_ia = "Al ser un adulto mayor, tus arterias son más sensibles. Tu médico debe iniciar con dosis suaves."
            else:
                orientacion_calculada = "Esquema estándar para adultos según criterio médico."
                observacion_ia = "Aunque te sientas muy bien, recuerda no suspender tu tratamiento diario."

        elif enfermedad == "Diabetes Tipo 2":
            if peso < 60.0:
                orientacion_calculada = "Requiere ajuste pautado por el especialista debido al bajo peso."
                observacion_ia = "Al tener un peso ligero (< 60 kg), se sugiere supervisión estrecha para cuidar tu digestión."
            else:
                orientacion_calculada = "Esquema estándar para control glucémico."
                observacion_ia = "Acompaña tu medicamento con caminatas suaves y buena hidratación."

        elif enfermedad == "Asma Crónica":
            if edad < 12:
                orientacion_calculada = "Esquema pediátrico supervisado."
                observacion_ia = "En niños es vital usar una cámara espaciadora bajo la supervisión amorosa de un adulto."
            else:
                orientacion_calculada = "Esquema estándar para adolescentes y adultos."
                observacion_ia = "Lleva siempre tu inhalador contigo para mantener la tranquilidad."

        # 7. DESPLIEGUE DE RESULTADOS CON COLOR INTERACTIVO
        st.html(f"""
            <div class="tarjeta-resultado" style="background-color: {med['color_fondo']}; border-left: 8px solid {med['color_borde']};">
                <h3 style="color: #1d3557; margin-top: 0;">📋 Plan de Orientación para {nombre_paciente}</h3>
                <p style="color: #2b2d42;"><b>🩺 Condición:</b> {enfermedad}</p>
                <p style="font-size: 20px; color: #1d3557;"><b>💊 Medicamento de Referencia:</b> {med['nombre']}</p>
                <p style="color: #2b2d42;"><b>📦 Presentación:</b> {med['presentacion']}</p>
                <p style="color: #2b2d42;"><b>⚖️ Orientación Biométrica:</b> {orientacion_calculada}</p>
                <p style="color: #2b2d42;"><b>⏰ Horario Sugerido:</b> {med['horario']}</p>
            </div>
        """)

        st.write("")
        st.warning(f"*⚠️ Lo que debes vigilar (Efectos Adversos):* {med['efectos_adversos']}")
        st.info(f"*💡 Consejo Humano de la IA:* {observacion_ia}")
        st.caption("🔴 *Nota Legal:* Esta aplicación es un asistente educativo comunitario. Nunca cambies tu dosis ni suspendas tu tratamiento sin consultar a tu médico.")

