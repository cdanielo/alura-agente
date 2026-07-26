# Guía de despliegue

El challenge pide que el agente esté accesible públicamente en la nube. Este
proyecto se puede desplegar en **cualquier proveedor** — aquí se documentan
tres opciones. Usa la que te haya funcionado; dentro del README principal deja
solo el link y la evidencia de la que realmente usaste.

---

## Opción A — Streamlit Community Cloud (recomendada)

Gratis, sin tarjeta, y tu app ya está lista para esto porque usa Streamlit.

### 1. Sube tu proyecto a GitHub (si no lo has hecho)

```powershell
git add .
git commit -m "Preparar proyecto para deploy"
git push
```

Asegúrate de que tus PDFs estén en `data/` dentro del repo (o al menos uno de
muestra) para que el índice se pueda generar en la nube.

### 2. Crea la cuenta y conecta el repo

1. Ve a https://streamlit.io/cloud y entra con tu cuenta de GitHub
2. Click en **"Create app"** → **"Deploy a public app from GitHub"**
3. Selecciona tu repositorio `alura-agente`
4. **Main file path:** `src/app.py`
5. Branch: `main`

### 3. Configura tu API key (Secrets)

Antes de darle a Deploy (o después, desde **Settings → Secrets** de la app ya creada):

```toml
GOOGLE_API_KEY = "tu_api_key_real_aqui"
```

Streamlit inyecta esto como variable de entorno automáticamente — tu código
(`os.getenv("GOOGLE_API_KEY")`) lo detecta sin cambios.

### 4. Genera el índice antes del primer deploy (importante)

Streamlit Cloud no ejecuta `ingest.py` por ti. Genera el índice **en tu máquina
local** y súbelo al repo junto con los PDFs:

```powershell
python src\ingest.py
git add faiss_index -f
git commit -m "Agrega índice FAISS pre-generado para el deploy"
git push
```

> Nota: normalmente `faiss_index/` está en `.gitignore`. Usa `-f` para forzar
> que se suba esta vez — es necesario porque Streamlit Cloud no corre scripts
> de preparación antes de levantar la app.

### 5. Deploy

Click en **"Deploy"**. Tarda 2-5 minutos en instalar dependencias. Al terminar,
te da una URL pública tipo:

```
https://alura-agente-tuusuario.streamlit.app
```

Esa es la URL que va en el README como evidencia.

### Si la app se "duerme"

Streamlit Cloud pausa apps sin tráfico. Al abrir el link, tarda ~30 segundos en
despertar — es normal, no es un error. Ábrela tú mismo un rato antes de que el
evaluador la revise, si puedes coordinar el momento.

---

## Opción B — Hugging Face Spaces (alternativa)

También gratis y soporta Streamlit directamente.

1. Crea cuenta en https://huggingface.co
2. Click en tu perfil → **"New Space"**
3. Nombre: `alura-agente` — SDK: **Streamlit** — Visibility: **Public**
4. En **Settings → Repository secrets**, agrega `GOOGLE_API_KEY` con tu clave
5. Sube los archivos del proyecto (puedes conectar el repo de GitHub o subir
   manualmente vía la interfaz web/git):
   ```powershell
   git remote add hf https://huggingface.co/spaces/TU_USUARIO/alura-agente
   git push hf main
   ```
6. Hugging Face detecta `src/app.py` automáticamente si lo defines en la
   configuración del Space (Settings → "App file": `src/app.py`)
7. La URL pública queda como:
   ```
   https://huggingface.co/spaces/TU_USUARIO/alura-agente
   ```

---

## Opción C — Oracle Cloud Infrastructure (OCI)

Si prefieres OCI (o el free tier ya te funcionó tras el upgrade a Pay As You
Go), sigue estos pasos. A diferencia de las opciones A y B, aquí tú controlas
el servidor completo y la app no se "duerme".

### 1. Crear la instancia

- **Compute → Instances → Create Instance**
- Imagen: Canonical Ubuntu 22.04
- Shape: `VM.Standard.E4.Flex` (1 OCPU / 8 GB) si usas Pay As You Go, o
  `VM.Standard.A1.Flex` / `VM.Standard.E2.1.Micro` si el Always Free tiene
  capacidad disponible en tu región
- Networking: usa una VCN con **subred pública**, con el switch de
  **"Automatically assign public IPv4 address"** activado
- Descarga la llave SSH privada cuando el wizard te la ofrezca

### 2. Abrir el puerto 8501

- Ve a la instancia → **Subnet** → **Security List** asociado
- **Add Ingress Rule:** Source `0.0.0.0/0`, protocolo TCP, puerto `8501`

### 3. Conectarte por SSH desde Windows

```powershell
ssh -i C:\ruta\a\tu\llave_privada ubuntu@IP_PUBLICA_DE_TU_INSTANCIA
```

### 4. Preparar el servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git

# Si usaste E2.1.Micro (solo 1 GB RAM), crea swap para que no se cuelgue
# al generar los embeddings:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

sudo iptables -I INPUT -p tcp --dport 8501 -j ACCEPT
```

### 5. Clonar, configurar y correr

```bash
git clone https://github.com/TU_USUARIO/alura-agente.git
cd alura-agente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # pega tu GOOGLE_API_KEY

python src/ingest.py
```

Para dejarlo corriendo de forma permanente, usa `systemd`:

```bash
sudo nano /etc/systemd/system/alura-agente.service
```

```ini
[Unit]
Description=Alura Agente Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/alura-agente
ExecStart=/home/ubuntu/alura-agente/venv/bin/streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
EnvironmentFile=/home/ubuntu/alura-agente/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable alura-agente
sudo systemctl start alura-agente
```

Accede en: `http://IP_PUBLICA_DE_TU_INSTANCIA:8501`

### 6. Cuando ya no lo necesites

Si usaste un shape pagado, no olvides terminar la instancia para evitar
cargos: **Compute → Instances → (selecciona) → Terminate**.

---

## ¿Cuál usar en el README?

Deja documentada solo la opción que realmente desplegaste, con su link y una
captura como evidencia. Si intentaste OCI primero y no funcionó por capacidad,
vale la pena mencionarlo brevemente — muestra que seguiste el proceso
recomendado por el challenge antes de optar por la alternativa.
