# Liderazgo con IA (Streamlit)

App para desarrollar tu liderazgo apoyado en Claude (Anthropic), con 4 módulos:

1. **Diagnóstico de liderazgo** — cuestionario corto que identifica tu estilo
   predominante, fortalezas y áreas de oportunidad, con un plan de crecimiento.
   Guarda un historial para ver tu evolución.
2. **Coach conversacional** — chat libre con un coach de liderazgo que conoce
   tu último diagnóstico.
3. **Simulador de conversaciones difíciles** — practica una conversación
   incómoda (dar feedback negativo, manejar un conflicto, etc.) con la IA
   jugando el papel de la otra persona, y pide retroalimentación al final.
4. **Diario con seguimiento** — registra situaciones semana a semana y pide un
   análisis de patrones a lo largo del tiempo.

Tus datos (diario y diagnósticos) se guardan localmente en `data/*.json`, junto
al archivo `app.py`. Nada se sube a ningún servidor salvo lo que envíes al chat,
que va directo a la API de Anthropic con tu propia API key.

## Cómo correrla en tu computadora

1. Instala Python 3.9+ si no lo tienes.
2. En una terminal, dentro de esta carpeta:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. Se abrirá en tu navegador en `http://localhost:8501`.
4. En la barra lateral, pega tu **API key de Anthropic** (la consigues gratis
   registrándote en https://console.anthropic.com, sección "API Keys"). Mientras
   no tengas una, puedes dejar activado el **modo demo** para explorar la
   interfaz con respuestas de ejemplo.

## Desplegarla gratis en la nube (para acceder desde cualquier lugar)

1. Sube esta carpeta a un repositorio de GitHub.
2. Entra a https://share.streamlit.io (Streamlit Community Cloud), conecta tu
   cuenta de GitHub y selecciona el repo, con `app.py` como archivo principal.
3. En "Advanced settings → Secrets", agrega:

   ```toml
   ANTHROPIC_API_KEY = "tu-api-key-aquí"
   ```

   Así no tendrás que pegar la key cada vez que entres.
4. Ojo: en Streamlit Cloud el sistema de archivos no es permanente entre
   redeploys, así que el diario/diagnósticos guardados en `data/` pueden
   perderse si el servicio reinicia el contenedor. Para uso personal diario
   corriéndola en tu propia máquina esto no es un problema.

## Modelo de IA usado

Por defecto usa `claude-sonnet-4-5-20250929`. Puedes cambiarlo en la barra
lateral por cualquier otro id vigente — revisa la lista actualizada en
https://docs.claude.com/en/docs/about-claude/models

## Costos

Esta app no tiene costo propio; pagas únicamente el uso de la API de Anthropic
según tu consumo (normalmente centavos de dólar por conversación). Puedes ver
tu consumo en tu cuenta de console.anthropic.com.
