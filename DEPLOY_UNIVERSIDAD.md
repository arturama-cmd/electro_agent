# Guia de Despliegue Universitario - ElectroAI

Esta guia detalla como desplegar ElectroAI en infraestructura local de la universidad usando modelos open source.

## Requisitos de Hardware

### Minimos (Llama 3.1 8B)
- GPU: 1x NVIDIA con 10+ GB VRAM (RTX 3080, A10)
- RAM: 32 GB
- CPU: 8 cores
- Almacenamiento: 50 GB SSD

### Recomendados (Llama 3.1 70B)
- GPU: 2x NVIDIA A100 80GB o 4x RTX 4090
- RAM: 128 GB
- CPU: 32 cores
- Almacenamiento: 200 GB NVMe SSD

### Optimo (Qwen 2.5 72B / DeepSeek)
- GPU: 4x NVIDIA A100 80GB o 8x RTX 4090
- RAM: 256 GB
- CPU: 64 cores
- Almacenamiento: 500 GB NVMe SSD

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     SERVIDOR GPU                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │    Servidor de Inferencia (elegir uno):             │    │
│  │    • Ollama (mas facil)                             │    │
│  │    • vLLM (mejor rendimiento)                       │    │
│  │    • text-generation-inference (HuggingFace)        │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           │ REST API (puerto 11434/8000)    │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ElectroAI Application                   │    │
│  │  • Streamlit (frontend)                             │    │
│  │  • RAG System (backend)                             │    │
│  │  • ChromaDB (vector store)                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           │ HTTPS (puerto 443)              │
└───────────────────────────┼─────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │    Reverse Proxy          │
              │    (nginx + SSL)          │
              │    + Auth Universidad     │
              └─────────────┬─────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   Estudiante          Estudiante          Estudiante
```

## Instalacion Paso a Paso

### 1. Instalar Servidor de Inferencia

#### Opcion A: Ollama (Recomendado para empezar)

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo (elegir segun VRAM disponible)
ollama pull llama3.1:8b      # 8GB VRAM - Basico
ollama pull llama3.1:70b     # 40GB VRAM - Recomendado
ollama pull qwen2.5:72b      # 45GB VRAM - Mejor calidad

# Iniciar servidor (se inicia automaticamente como servicio)
ollama serve
```

#### Opcion B: vLLM (Mejor rendimiento en produccion)

```bash
# Instalar vLLM
pip install vllm

# Iniciar servidor
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-70B-Instruct \
    --tensor-parallel-size 2 \
    --port 8000
```

### 2. Configurar ElectroAI

```bash
# Clonar repositorio
git clone <repo-url> /opt/electroai
cd /opt/electroai

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install ollama  # Solo si usas Ollama

# Configurar variables de entorno
cp .env.local.example .env
nano .env  # Editar segun tu configuracion
```

### 3. Reemplazar RAG System

```bash
# Usar version con soporte local
cp rag_system_local.py rag_system.py
```

### 4. Configurar Reverse Proxy (nginx)

```nginx
# /etc/nginx/sites-available/electroai
server {
    listen 443 ssl;
    server_name electroai.universidad.edu;

    ssl_certificate /etc/ssl/certs/universidad.crt;
    ssl_certificate_key /etc/ssl/private/universidad.key;

    # Autenticacion LDAP (opcional)
    auth_ldap "Universidad Login";
    auth_ldap_servers ldap_server;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Configuracion LDAP
ldap_server ldap_server {
    url ldap://ldap.universidad.edu/dc=universidad,dc=edu?uid?sub?(objectClass=person);
    binddn "cn=readonly,dc=universidad,dc=edu";
    binddn_passwd "password";
    group_attribute member;
    group_attribute_is_dn on;
    require valid_user;
}
```

### 5. Crear Servicio Systemd

```ini
# /etc/systemd/system/electroai.service
[Unit]
Description=ElectroAI Streamlit Application
After=network.target ollama.service

[Service]
Type=simple
User=electroai
WorkingDirectory=/opt/electroai
Environment="PATH=/opt/electroai/venv/bin"
ExecStart=/opt/electroai/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
sudo systemctl daemon-reload
sudo systemctl enable electroai
sudo systemctl start electroai
```

## Comparativa de Costos (Anual)

### Escenario: 500 estudiantes, 50 consultas/mes c/u = 300,000 consultas/ano

| Concepto | API Anthropic | Hardware Local |
|----------|---------------|----------------|
| Costo por consulta | $0.02 | ~$0.001 |
| Costo anual consultas | $6,000 | $300 (electricidad) |
| Hardware inicial | $0 | $0 (ya disponible) |
| Mantenimiento | $0 | $600 |
| **TOTAL ANUAL** | **$6,000** | **$900** |
| **Ahorro** | - | **$5,100/ano** |

### Costos de Electricidad Estimados

| Configuracion | Consumo | Costo/mes (Chile ~$0.15/kWh) |
|---------------|---------|------------------------------|
| 2x RTX 4090 (idle) | 100W | $11 |
| 2x RTX 4090 (carga) | 900W | $100 |
| 4x A100 (idle) | 200W | $22 |
| 4x A100 (carga) | 1600W | $175 |

*Asumiendo uso promedio 8 horas/dia en carga*

## Rendimiento Esperado

| Modelo | Tokens/segundo | Tiempo respuesta tipica |
|--------|----------------|-------------------------|
| Llama 3.1 8B (1x RTX 4090) | ~80 tok/s | 3-5 segundos |
| Llama 3.1 70B (2x A100) | ~40 tok/s | 8-15 segundos |
| Qwen 2.5 72B (4x A100) | ~35 tok/s | 10-20 segundos |

## Usuarios Concurrentes

| Configuracion | Usuarios simultaneos | Latencia p95 |
|---------------|----------------------|--------------|
| Ollama + 1 GPU | 3-5 | 15s |
| vLLM + 2 GPU | 10-15 | 12s |
| vLLM + 4 GPU | 25-40 | 10s |

## Monitoreo

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Metricas a monitorear
- GPU utilization (nvidia-smi)
- Tokens/segundo
- Latencia de respuesta
- Usuarios activos
- Errores de inferencia

## Seguridad

### Checklist
- [ ] SSL/TLS habilitado
- [ ] Autenticacion LDAP/SSO configurada
- [ ] Firewall: solo puerto 443 expuesto
- [ ] Rate limiting configurado
- [ ] Logs de acceso habilitados
- [ ] Backups automaticos del corpus

### Rate Limiting (nginx)

```nginx
# Limitar a 10 requests/minuto por usuario
limit_req_zone $binary_remote_addr zone=electroai:10m rate=10r/m;

location / {
    limit_req zone=electroai burst=20 nodelay;
    proxy_pass http://localhost:8501;
}
```

## Troubleshooting

### GPU no detectada
```bash
nvidia-smi  # Verificar drivers
ollama list  # Verificar modelos disponibles
```

### Modelo muy lento
- Reducir tamano del modelo (70B → 8B)
- Aumentar tensor parallelism
- Verificar que no hay otros procesos usando GPU

### Errores de memoria
```bash
# Limpiar cache de modelos
ollama rm llama3.1:70b
ollama pull llama3.1:70b

# Reiniciar servicio
sudo systemctl restart ollama
```

## Contacto Soporte

Para soporte tecnico contactar:
- Email: soporte-ti@universidad.edu
- Documentacion: https://docs.universidad.edu/electroai
