# 🤖 Alura Agente — Santos Pegasus Soluciones

Agente de inteligencia artificial (RAG — *Retrieval-Augmented Generation*) capaz
de responder preguntas en lenguaje natural sobre la documentación interna de
**Santos Pegasus Soluciones**, empresa de tecnología especializada en
microservicios y soluciones de IA.

Proyecto final del **Challenge Alura Agente** (curso de Cloud Computing – Alura).

---

## 📚 Base de conocimiento

El agente responde preguntas basándose en los siguientes documentos internos
(colocados en `/data`):

- `Manual de Onboarding para Nuevos Desarrolladores.pdf`
- `Guía Oficial de Ingeniería Back-end.pdf`
- `Guía Oficial de Ingeniería Front-end.pdf`
- `Protocolo de Respuesta a Incidentes y Post-Mortems.pdf`
- `Arquitectura de Microservicios y Mapa de Dominios.pdf`

---

## 🏗️ Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌───────────────────┐
│  Documentos  │ ---> │   Ingesta    │ ---> │   Índice vectorial │
│  PDF (data/) │      │ (ingest.py)  │      │  FAISS (local)     │
└─────────────┘      └──────────────┘      └────────┬───────────┘
                                                       │
                                                       ▼
┌──────────────┐     ┌────────────────────┐   ┌────────────────┐
│   Usuario     │---> │  Interfaz Streamlit │-->│  Retriever      │
│ (pregunta)    │     │      (app.py)       │   │  (busca chunks  │
└──────────────┘     └────────┬────────────┘   │  relevantes)    │
                               │                └────────┬────────┘
                               ▼                          ▼
                     ┌────────────────────────────────────────┐
                     │   LLM Gemini (2.5 Flash) — agent.py   │
                     │   Genera la respuesta usando solo el     │
                     │   contexto recuperado                    │
                     └────────────────────────────────────────┘
```

**Componentes:**

| Capa | Tecnología | Motivo |
|---|---|---|
| Lectura de documentos | `PyPDFLoader` (LangChain) | Extrae texto de los PDF |
| Fragmentación | `RecursiveCharacterTextSplitter` | Divide en chunks de 1000 caracteres con solapamiento |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace, local) | 100% gratis, corre en CPU, sin API key |
| Base vectorial | FAISS | Búsqueda por similitud, corre en local, gratis |
| LLM (generación de respuesta) | Google Gemini — `gemini-2.5-flash` | Gratis, sin tarjeta de crédito, buen contexto (1M tokens) |
| Orquestación | LangChain (`create_retrieval_chain`) | Une retriever + LLM |
| Interfaz | Streamlit | Simple de correr y de exponer en un servidor |
| Hosting | Streamlit Community Cloud (ver [`DEPLOY.md`](./DEPLOY.md) para alternativas: Hugging Face Spaces, OCI) | Accesibilidad pública requerida por el challenge |

**Flujo (pipeline RAG):**
1. `ingest.py` lee los PDF, los trocea y genera un embedding (vector numérico) por
   fragmento, guardando todo en un índice FAISS local.
2. Cuando el usuario pregunta algo, `agent.py` convierte la pregunta en un vector,
   busca los 4 fragmentos más parecidos en el índice (`retriever`) y se los pasa
   al LLM de Gemini junto con la pregunta.
3. El LLM responde **solo** con base en esos fragmentos (no inventa información
   que no esté en los documentos).

---

## 💬 Ejemplos de preguntas y respuestas

> Reemplaza estos ejemplos con capturas reales una vez que pruebes tu agente
> con tus documentos.

**Pregunta:** ¿Qué debe hacer un nuevo desarrollador en su primera semana según el manual de onboarding?
**Respuesta:** *(pega aquí la respuesta real del agente)*

**Pregunta:** ¿Qué pasos sigue el protocolo de respuesta a incidentes tras detectar un post-mortem?
**Respuesta:** *(pega aquí la respuesta real del agente)*

**Pregunta:** ¿Qué estándares técnicos exige la guía de ingeniería back-end?
**Respuesta:** *(pega aquí la respuesta real del agente)*

---

## ⚙️ Instrucciones para ejecutar el proyecto (local)

### Requisitos
- Python 3.10+
- Una API key gratuita de Google AI Studio: https://aistudio.google.com/apikey

### Pasos (Windows / PowerShell)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/alura-agente.git
cd alura-agente

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar la API key
copy .env.example .env
# Abre .env y pega tu GOOGLE_API_KEY

# 5. Colocar tus documentos PDF/CSV dentro de la carpeta data/

# 6. Generar el índice vectorial (solo una vez, o cuando cambien los documentos)
python src/ingest.py

# 7a. Probar en consola
python src/agent.py

# 7b. O correr la interfaz web local
streamlit run src/app.py
```

---

## ☁️ Deploy

**🔗 Aplicación funcionando:** `<pega aquí tu URL real, por ejemplo https://alura-agente-tuusuario.streamlit.app>`

*(agrega aquí una captura de pantalla de la app funcionando en el navegador)*

Se desplegó en **[Streamlit Community Cloud / Hugging Face Spaces / OCI — deja solo la que usaste]**.
Pasos completos de despliegue (incluye las tres opciones) en [`DEPLOY.md`](./DEPLOY.md).

---

## 📂 Estructura del repositorio

```
alura-agente/
├── data/                 # Documentos PDF/CSV (base de conocimiento)
├── src/
│   ├── ingest.py         # Construye el índice vectorial
│   ├── agent.py          # Lógica del agente RAG (consola)
│   └── app.py            # Interfaz web (Streamlit)
├── faiss_index/          # Índice generado (no se sube a git)
├── requirements.txt
├── .env.example
├── .gitignore
├── DEPLOY.md             # Guía de despliegue (Streamlit Cloud / HF Spaces / OCI)
└── README.md
```

---

## 🧠 Decisiones técnicas

- **Embeddings locales en vez de API paga:** se usa un modelo open-source de
  HuggingFace que corre en CPU, evitando costos y límites de cuota solo para
  generar los vectores del índice.
- **Gemini como LLM:** Google AI Studio ofrece un tier gratuito sin tarjeta de
  crédito, con una ventana de contexto de hasta 1 millón de tokens, suficiente
  para una demo funcional del challenge.
- **FAISS local:** no requiere una base de datos vectorial externa ni
  credenciales adicionales, lo que simplifica el despliegue en cualquier
  proveedor de nube — el índice se genera una vez y se sube junto con el
  código.
- **Hosting flexible:** el proyecto corre igual en Streamlit Community Cloud,
  Hugging Face Spaces u OCI, ya que no depende de ningún servicio propietario
  de un proveedor específico. Ver [`DEPLOY.md`](./DEPLOY.md) para el paso a
  paso de cada opción.
