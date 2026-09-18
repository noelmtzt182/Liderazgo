import streamlit as st
import json
import os
from datetime import datetime, date

import anthropic

# ----------------------------------------------------------------------------
# Configuración general
# ----------------------------------------------------------------------------
st.set_page_config(page_title="MiCoach de Liderazgo", page_icon="🧭", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DIARY_PATH = os.path.join(DATA_DIR, "diario.json")
ASSESSMENT_PATH = os.path.join(DATA_DIR, "diagnosticos.json")

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------------------------------------------------------
# Sidebar: configuración de la IA
# ----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configuración")

secret_key = ""
try:
    secret_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    secret_key = ""

api_key_input = st.sidebar.text_input(
    "Anthropic API key",
    type="password",
    value="",
    help="Consíguela en console.anthropic.com. También puedes definirla como secret "
         "ANTHROPIC_API_KEY si despliegas en Streamlit Community Cloud.",
)
api_key = api_key_input or secret_key

model = st.sidebar.text_input(
    "Modelo",
    value=DEFAULT_MODEL,
    help="Revisa el id vigente en docs.claude.com/en/docs/about-claude/models",
)

demo_mode = st.sidebar.checkbox(
    "Modo demo (sin API key)",
    value=not bool(api_key),
    help="Muestra respuestas de ejemplo sin llamar a la API. Útil para probar la app.",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Esta app guarda tu diario y tus diagnósticos localmente, en la carpeta `data/` "
    "junto al archivo app.py. No se envían a ningún servidor salvo lo que escribas "
    "en el chat, que va directo a la API de Anthropic."
)

nav = st.sidebar.radio(
    "Ir a",
    [
        "🧭 Diagnóstico de liderazgo",
        "💬 Coach conversacional",
        "🎭 Simulador de conversaciones difíciles",
        "📓 Diario con seguimiento",
    ],
)


def get_client():
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def ask_claude(system, messages, max_tokens=1400):
    """Llama a Claude, o devuelve una respuesta de ejemplo en modo demo."""
    if demo_mode or not api_key:
        return (
            "_(Modo demo — no se llamó a la API real. Aquí verías un análisis "
            "genuino de Claude sobre tu situación, con observaciones específicas "
            "y sugerencias concretas. Agrega tu API key en la barra lateral y "
            "desmarca 'Modo demo' para respuestas reales.)_"
        )
    client = get_client()
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return resp.content[0].text
    except Exception as e:
        return f"⚠️ Error al llamar a la API de Anthropic: {e}"


def latest_assessment():
    history = load_json(ASSESSMENT_PATH, [])
    return history[-1] if history else None


# ----------------------------------------------------------------------------
# MÓDULO 1: Diagnóstico de tipo de liderazgo
# ----------------------------------------------------------------------------
def modulo_diagnostico():
    st.header("🧭 Diagnóstico de tipo de liderazgo")
    st.write(
        "Responde este breve cuestionario con honestidad. La IA identificará tu "
        "estilo de liderazgo predominante, tus fortalezas y tus áreas de "
        "oportunidad, con un plan de crecimiento concreto."
    )

    preguntas = [
        ("decision", "Cuando el equipo enfrenta una decisión importante, yo...",
         ["Decido yo y comunico la instrucción con claridad",
          "Reúno opiniones del equipo pero al final decido yo",
          "Busco que el equipo llegue a un consenso",
          "Delego la decisión a quien tenga más contexto/experiencia"]),
        ("feedback", "Cuando alguien de mi equipo comete un error, mi primera reacción es...",
         ["Corregirlo de inmediato y con firmeza",
          "Preguntar qué pasó antes de opinar",
          "Buscar el aprendizaje conjunto, sin buscar culpables",
          "Evitar el tema si no es grave, para no generar tensión"]),
        ("motivacion", "Motivo a mi equipo principalmente...",
         ["Con metas claras, plazos y consecuencias",
          "Reconociendo el esfuerzo y el progreso individual",
          "Conectando el trabajo con un propósito mayor",
          "Dándoles autonomía para resolver a su manera"]),
        ("conflicto", "Ante un conflicto entre dos personas del equipo...",
         ["Intervengo rápido para resolverlo yo mismo",
          "Facilito una conversación entre ambas partes",
          "Espero a ver si se resuelve solo antes de intervenir",
          "Pido a alguien más senior que medie"]),
        ("delegacion", "Cuando delego una tarea importante...",
         ["Doy instrucciones muy detalladas y reviso cada paso",
          "Explico el objetivo y reviso en hitos clave",
          "Explico el objetivo y dejo que decidan el cómo",
          "Me cuesta soltar el control y termino haciéndolo yo"]),
        ("comunicacion", "Mi estilo de comunicación con el equipo es...",
         ["Directo y enfocado en resultados",
          "Cercano, pregunto cómo están antes de ir al tema",
          "Inspirador, hablo de visión y futuro",
          "Reservado, comunico solo lo esencial"]),
        ("cambio", "Frente a un cambio inesperado (reorganización, nueva prioridad)...",
         ["Actúo rápido y ajusto el plan sin mucho análisis",
          "Consulto al equipo antes de decidir cómo adaptarnos",
          "Busco entender el porqué antes de actuar",
          "Me cuesta adaptarme y prefiero lo conocido"]),
        ("reconocimiento", "Cuando el equipo logra un buen resultado...",
         ["Paso rápido al siguiente objetivo",
          "Reconozco públicamente el logro del equipo",
          "Reconozco a cada persona de forma individual",
          "Asumo que ya lo saben y no digo nada"]),
    ]

    with st.form("form_diagnostico"):
        respuestas = {}
        for key, texto, opciones in preguntas:
            respuestas[key] = st.radio(texto, opciones, key=f"diag_{key}")
        comentario_libre = st.text_area(
            "¿Algo más que quieras contar sobre cómo lideras hoy? (opcional)"
        )
        enviado = st.form_submit_button("Generar diagnóstico")

    if enviado:
        resumen_respuestas = "\n".join(
            f"- {texto}: {respuestas[key]}" for key, texto, _ in preguntas
        )
        system = (
            "Eres un consultor experto en liderazgo organizacional. Analizas "
            "respuestas de un cuestionario y devuelves un diagnóstico honesto, "
            "específico y accionable en español. Usa marcos reconocidos de "
            "liderazgo (situacional, transformacional, servicial, autocrático, "
            "democrático, laissez-faire, coach) para nombrar el estilo "
            "predominante, pero no fuerces una sola etiqueta si la persona es "
            "híbrida. Estructura tu respuesta con estos apartados en texto "
            "corriente (sin usar markdown de tablas): 1) Estilo de liderazgo "
            "predominante y por qué: 2) Fortalezas (2-3): 3) Áreas de "
            "oportunidad (2-3), concretas y sin generalidades: 4) Plan de "
            "crecimiento: para cada área de oportunidad, una acción práctica "
            "que pueda aplicar esta semana. Sé directo pero constructivo."
        )
        user_msg = (
            f"Respuestas al cuestionario de estilo de liderazgo:\n{resumen_respuestas}\n\n"
            f"Comentario adicional de la persona: {comentario_libre or '(sin comentario)'}"
        )
        with st.spinner("Analizando tus respuestas..."):
            resultado = ask_claude(system, [{"role": "user", "content": user_msg}])

        st.subheader("Resultado de tu diagnóstico")
        st.write(resultado)

        history = load_json(ASSESSMENT_PATH, [])
        history.append(
            {
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "respuestas": respuestas,
                "comentario": comentario_libre,
                "resultado": resultado,
            }
        )
        save_json(ASSESSMENT_PATH, history)
        st.success("Diagnóstico guardado. Podrás verlo reflejado en tu historial abajo.")

    st.markdown("---")
    st.subheader("Historial de diagnósticos")
    history = load_json(ASSESSMENT_PATH, [])
    if not history:
        st.caption("Aún no tienes diagnósticos guardados.")
    else:
        for item in reversed(history):
            with st.expander(f"Diagnóstico del {item['fecha'][:16].replace('T', ' ')}"):
                st.write(item["resultado"])


# ----------------------------------------------------------------------------
# MÓDULO 2: Coach conversacional
# ----------------------------------------------------------------------------
def modulo_coach():
    st.header("💬 Coach conversacional de liderazgo")
    st.write(
        "Cuéntale a tu coach de IA una situación, duda o decisión de liderazgo. "
        "Te hará preguntas y te dará perspectiva, como lo haría un buen mentor."
    )

    if "coach_history" not in st.session_state:
        st.session_state.coach_history = []

    contexto_extra = ""
    ultimo = latest_assessment()
    if ultimo:
        contexto_extra = (
            "\n\nContexto: la persona ya hizo un diagnóstico de liderazgo previo. "
            "Resultado resumido:\n" + ultimo["resultado"][:1500]
        )

    system = (
        "Eres un coach ejecutivo de liderazgo, cálido pero directo. Respondes en "
        "español. No das discursos largos: haces preguntas que ayuden a la persona "
        "a pensar por sí misma, ofreces marcos simples cuando ayudan, y das "
        "sugerencias concretas solo cuando la persona ya exploró el problema. "
        "Evita la condescendencia y el relleno motivacional vacío." + contexto_extra
    )

    for msg in st.session_state.coach_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Escribe tu situación o pregunta de liderazgo...")
    if prompt:
        st.session_state.coach_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = ask_claude(system, st.session_state.coach_history)
            st.write(respuesta)
        st.session_state.coach_history.append({"role": "assistant", "content": respuesta})

    if st.session_state.coach_history:
        if st.button("🗑️ Reiniciar conversación"):
            st.session_state.coach_history = []
            st.rerun()


# ----------------------------------------------------------------------------
# MÓDULO 3: Simulador de conversaciones difíciles
# ----------------------------------------------------------------------------
def modulo_simulador():
    st.header("🎭 Simulador de conversaciones difíciles")
    st.write(
        "Describe la situación y el simulador jugará el papel de la otra persona "
        "para que practiques antes de tener la conversación real."
    )

    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []
        st.session_state.sim_activa = False

    with st.expander("Configurar la simulación", expanded=not st.session_state.sim_activa):
        situacion = st.text_area(
            "Situación / motivo de la conversación",
            placeholder="Ej: Necesito decirle a Ana que su desempeño ha bajado en los últimos 2 meses.",
        )
        rol = st.text_input(
            "¿Quién es la otra persona?",
            placeholder="Ej: Ana, colaboradora senior con 3 años en el equipo",
        )
        personalidad = st.selectbox(
            "Actitud esperada de la otra persona",
            [
                "Defensiva / se justifica mucho",
                "Pasivo-agresiva / evita el conflicto directo",
                "Muy emocional / puede llorar o enojarse",
                "Racional y abierta a feedback",
                "Confrontativa / cuestiona tu autoridad",
            ],
        )
        objetivo = st.text_input(
            "Tu objetivo en esta conversación",
            placeholder="Ej: Que entienda el impacto y acordemos un plan de mejora",
        )
        if st.button("🎬 Iniciar simulación"):
            st.session_state.sim_history = []
            st.session_state.sim_activa = True
            st.session_state.sim_system = (
                "Vas a interpretar un personaje en un roleplay de práctica de "
                "liderazgo, en español. No eres un asistente, eres el personaje. "
                f"Personaje: {rol or 'un colaborador'}. Actitud: {personalidad}. "
                f"Contexto de la conversación: {situacion}. "
                "Responde siempre en primera persona, como el personaje, con "
                "reacciones creíbles y humanas (no exageradas). No rompas el "
                "personaje ni des consejos de liderazgo: solo actúa el papel. "
                "Mantén las respuestas breves, como en una conversación real."
            )
            st.session_state.sim_objetivo = objetivo
            st.rerun()

    if st.session_state.sim_activa:
        st.info(f"🎯 Tu objetivo: {st.session_state.get('sim_objetivo', '')}")

        for msg in st.session_state.sim_history:
            role_label = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role_label):
                st.write(msg["content"])

        prompt = st.chat_input("Escribe lo que le dirías...")
        if prompt:
            st.session_state.sim_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    respuesta = ask_claude(st.session_state.sim_system, st.session_state.sim_history)
                st.write(respuesta)
            st.session_state.sim_history.append({"role": "assistant", "content": respuesta})

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Dame retroalimentación de cómo lo manejé"):
                transcript = "\n".join(
                    f"{'Tú' if m['role']=='user' else 'Otra persona'}: {m['content']}"
                    for m in st.session_state.sim_history
                )
                system_fb = (
                    "Eres un coach de liderazgo evaluando una simulación de "
                    "conversación difícil. Responde en español, en texto corrido: "
                    "qué hizo bien la persona (rol 'Tú'), qué podría mejorar, y "
                    "1-2 frases alternativas concretas que pudo usar en momentos "
                    "clave. Sé específico, cita fragmentos del diálogo."
                )
                with st.spinner("Analizando la conversación..."):
                    feedback = ask_claude(
                        system_fb,
                        [{"role": "user", "content": f"Objetivo: {st.session_state.get('sim_objetivo','')}\n\nTranscripción:\n{transcript}"}],
                    )
                st.subheader("Retroalimentación")
                st.write(feedback)
        with col2:
            if st.button("🔄 Terminar y reiniciar"):
                st.session_state.sim_activa = False
                st.session_state.sim_history = []
                st.rerun()


# ----------------------------------------------------------------------------
# MÓDULO 4: Diario de liderazgo con seguimiento
# ----------------------------------------------------------------------------
def modulo_diario():
    st.header("📓 Diario de liderazgo con seguimiento")
    st.write(
        "Registra situaciones de liderazgo semana a semana. Con el tiempo, la IA "
        "te ayudará a detectar patrones que no se ven en una sola entrada."
    )

    with st.form("form_diario", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=date.today())
        situacion = st.text_area("¿Qué situación de liderazgo viviste?")
        bien = st.text_area("¿Qué hiciste bien?")
        diferente = st.text_area("¿Qué harías diferente?")
        aprendizaje = st.text_area("¿Qué aprendizaje te llevas?")
        guardar = st.form_submit_button("Guardar entrada")

    if guardar:
        if not situacion.strip():
            st.warning("Describe al menos la situación antes de guardar.")
        else:
            entradas = load_json(DIARY_PATH, [])
            entradas.append(
                {
                    "fecha": fecha.isoformat(),
                    "situacion": situacion,
                    "bien": bien,
                    "diferente": diferente,
                    "aprendizaje": aprendizaje,
                }
            )
            save_json(DIARY_PATH, entradas)
            st.success("Entrada guardada en tu diario.")

    st.markdown("---")
    entradas = load_json(DIARY_PATH, [])
    st.subheader(f"Tus entradas ({len(entradas)})")

    if not entradas:
        st.caption("Aún no tienes entradas. Registra tu primera situación arriba.")
        return

    for e in reversed(entradas[-20:]):
        with st.expander(f"{e['fecha']} — {e['situacion'][:60]}"):
            st.markdown(f"**Situación:** {e['situacion']}")
            if e.get("bien"):
                st.markdown(f"**Qué hizo bien:** {e['bien']}")
            if e.get("diferente"):
                st.markdown(f"**Qué haría diferente:** {e['diferente']}")
            if e.get("aprendizaje"):
                st.markdown(f"**Aprendizaje:** {e['aprendizaje']}")

    st.markdown("---")
    if st.button("🔍 Analizar patrones de mis últimas entradas"):
        recientes = entradas[-15:]
        texto_entradas = "\n\n".join(
            f"[{e['fecha']}] Situación: {e['situacion']}\n"
            f"Qué hizo bien: {e.get('bien','')}\n"
            f"Qué haría diferente: {e.get('diferente','')}\n"
            f"Aprendizaje: {e.get('aprendizaje','')}"
            for e in recientes
        )
        ultimo_diag = latest_assessment()
        contexto_diag = (
            f"\n\nSu diagnóstico de liderazgo más reciente concluyó:\n{ultimo_diag['resultado'][:1200]}"
            if ultimo_diag else ""
        )
        system = (
            "Eres un coach de liderazgo que analiza un diario de entradas a lo "
            "largo del tiempo para encontrar patrones que la persona no ve por sí "
            "misma. Responde en español, en texto corrido, con estos apartados: "
            "1) Patrones recurrentes que detectas (temas, situaciones que se "
            "repiten): 2) Un posible punto ciego: 3) Progreso que sí notas frente "
            "a entradas anteriores, si lo hay: 4) Una sola prioridad de foco para "
            "las próximas dos semanas, con una acción concreta. Sé específico y "
            "cita ejemplos de las entradas." + contexto_diag
        )
        with st.spinner("Buscando patrones en tu diario..."):
            analisis = ask_claude(system, [{"role": "user", "content": texto_entradas}])
        st.subheader("Análisis de patrones")
        st.write(analisis)


# ----------------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------------
st.title("🧭 MiCoach de Liderazgo")
st.caption(
    "Diagnostica tu estilo, practica conversaciones difíciles, lleva un diario "
    "con seguimiento y conversa con un coach — todo apoyado en Claude."
)

if nav == "🧭 Diagnóstico de liderazgo":
    modulo_diagnostico()
elif nav == "💬 Coach conversacional":
    modulo_coach()
elif nav == "🎭 Simulador de conversaciones difíciles":
    modulo_simulador()
elif nav == "📓 Diario con seguimiento":
    modulo_diario()
