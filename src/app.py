
import streamlit as st
import os
from ambiguity_engine import AmbiguityEngine

# --- Configuración de la página --- #
st.set_page_config(
    page_title="LyricScope AI: Detector de Ambigüedad",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Título y Descripción --- #
st.title("🎵 LyricScope AI: Detector de Ambigüedad")
st.markdown("Bienvenido a LyricScope AI, tu herramienta para analizar la ambigüedad en las letras de canciones. Introduce las letras a continuación y descubre sus múltiples interpretaciones.")

# --- Obtener API Key de OpenAI --- #
# Es crucial que la API Key se configure como una variable de entorno
# para despliegues seguros. Para desarrollo local, puedes ponerla aquí
# o en un archivo .env y cargarla con `dotenv`.
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.warning("¡Atención! La clave de la API de OpenAI no está configurada. Por favor, establece la variable de entorno `OPENAI_API_KEY` o introduce tu clave a continuación para probar la aplicación.")
    openai_api_key = st.text_input("Introduce tu clave de la API de OpenAI aquí:", type="password")

# --- Inicializar AmbiguityEngine --- #
@st.cache_resource
def get_ambiguity_engine(api_key):
    if api_key:
        return AmbiguityEngine(api_key)
    return None

engine = get_ambiguity_engine(openai_api_key)

# --- Área de Entrada de Letras --- #
lyrics_input = st.text_area(
    "Pega aquí las letras de la canción para analizar:",
    height=300,
    placeholder="Ejemplo:\nIs this the real life?\nIs this just fantasy?\nCaught in a landslide, no escape from reality."
)

# --- Botón de Análisis --- #
if st.button("Analizar Ambigüedad", use_container_width=True):
    if not openai_api_key:
        st.error("Por favor, introduce tu clave de la API de OpenAI para continuar.")
    elif not lyrics_input.strip():
        st.error("Por favor, introduce algunas letras para analizar.")
    elif engine:
        with st.spinner("Analizando la letra... Esto puede tardar unos segundos."):
            try:
                result = engine.detect_ambiguity("Canción sin título", "Artista Desconocido", lyrics_input)
                
                st.subheader("Resultados del Análisis de Ambigüedad")
                
                if "error" in result:
                    st.error(f"Ocurrió un error durante el análisis: {result["error"]}")
                else:
                    score = result.get("ambiguity_score", 0.0)
                    is_ambiguous = result.get("is_ambiguous", False)
                    reasoning = result.get("reasoning", "No se proporcionó justificación.")
                    interpretations = result.get("multiple_interpretations", [])
                    artistic_intentional = result.get("artistic_intentional_ambiguity", False)
                    notes = result.get("notes", "No hay notas adicionales.")

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric(label="Puntuación de Ambigüedad", value=f"{score:.2f}/1.0")
                        if is_ambiguous:
                            st.success("**La canción es ambigua** ✅")
                        else:
                            st.info("**La canción no es ambigua** ❌")
                        
                        if artistic_intentional:
                            st.info("Ambigüedad artística intencional detectada.")

                    with col2:
                        st.write("**Justificación:**")
                        st.write(reasoning)

                    if interpretations:
                        st.write("**Múltiples Interpretaciones:**")
                        for i, interp in enumerate(interpretations):
                            st.write(f"- {interp}")
                    
                    if notes:
                        st.write("**Notas Adicionales:**")
                        st.write(notes)

                    with st.expander("Ver JSON Completo del Resultado"):
                        st.json(result)

            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")
                st.exception(e)
    else:
        st.error("El motor de ambigüedad no pudo ser inicializado. Por favor, verifica tu clave de la API de OpenAI.")

