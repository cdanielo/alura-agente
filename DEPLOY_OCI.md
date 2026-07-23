# Despliegue en Oracle Cloud Infrastructure (OCI) — Always Free

Guía paso a paso para poner tu agente accesible públicamente cumpliendo el
requisito de deploy del challenge.

## 1. Crear la instancia (VM)

1. Entra a https://cloud.oracle.com y crea/inicia sesión en tu cuenta **Always Free**.
2. Ve a **Compute → Instances → Create Instance**.
3. Configuración recomendada:
   - **Imagen:** Canonical Ubuntu 22.04
   - **Shape:** `VM.Standard.E2.1.Micro` (AMD, siempre gratis) o `VM.Standard.A1.Flex` (ARM, más RAM gratis, recomendado si vas a correr sentence-transformers)
   - **Add SSH keys:** genera un par de llaves o sube tu llave pública (en Windows puedes generarla con `ssh-keygen` desde PowerShell)
4. Crea la instancia y anota la **IP pública**.

## 2. Abrir el puerto 8501 (Streamlit)

1. Ve a la instancia → pestaña **Subnet** → click en el nombre de la subred.
2. Entra al **Security List** (o crea una NSG) asociado.
3. **Add Ingress Rule:**
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: TCP
   - Destination Port Range: `8501`
4. Guarda.

## 3. Conectarte por SSH desde Windows (PowerShell)

```powershell
ssh -i C:\ruta\a\tu\llave_privada ubuntu@IP_PUBLICA_DE_TU_INSTANCIA
```

## 4. Preparar el servidor

Dentro de la instancia (ya conectado por SSH):

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git

# El firewall interno de Ubuntu también bloquea el puerto por defecto:
sudo iptables -I INPUT -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save   # si no existe, usa: sudo apt install -y iptables-persistent
```

## 5. Clonar el repo y configurar

```bash
git clone https://github.com/TU_USUARIO/alura-agente.git
cd alura-agente

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
nano .env   # pega tu GOOGLE_API_KEY, Ctrl+O para guardar, Ctrl+X para salir
```

Sube tus PDFs a `data/` (puedes usar `scp` desde tu PC Windows):

```powershell
scp -i C:\ruta\a\tu\llave_privada "C:\ruta\a\tus\pdfs\*.pdf" ubuntu@IP_PUBLICA:~/alura-agente/data/
```

Genera el índice en el servidor:

```bash
python src/ingest.py
```

## 6. Correr la app de forma permanente

Para que siga corriendo aunque cierres la sesión SSH, usa `systemd`:

```bash
sudo nano /etc/systemd/system/alura-agente.service
```

Pega esto (ajusta rutas si tu usuario no es `ubuntu`):

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

Actívalo:

```bash
sudo systemctl daemon-reload
sudo systemctl enable alura-agente
sudo systemctl start alura-agente
sudo systemctl status alura-agente   # debe decir "active (running)"
```

## 7. Verificar

Abre en tu navegador:

```
http://IP_PUBLICA_DE_TU_INSTANCIA:8501
```

Toma una captura de pantalla de la app funcionando y pégala en el README
principal como evidencia del deploy exitoso.

## Comandos útiles

```bash
sudo systemctl restart alura-agente   # reiniciar tras cambios
journalctl -u alura-agente -f         # ver logs en vivo
```
