# Seguridad de la base de IA - Metodología práctica de escape de contenedores y sandbox

> Fuente: Comunidad de Seguridad de Grandes Modelos AISS NSFOCUS | Extraído de ai-baseline-security.md
> Tema: Metodología práctica de escape de contenedores / persistencia / movimiento lateral

## 20. Metodología de pruebas prácticas de escape de contenedores y sandbox

> Pruebas sistemáticas de escape y aislamiento para entornos de despliegue de aplicaciones de IA (Docker/Sysbox/Daytona/Kubernetes)
> **Seguridad general de despliegue en contenedores**: Verificación de seguridad de despliegue de aplicaciones web en contenedores → [web-deployment-security.md §2](web-deployment-security.md)

### 1. Resumen general del flujo de pruebas

```
Recopilación de información → Identificación del entorno → Evaluación de aislamiento → Intento de escape → Verificación de persistencia → Movimiento lateral → Informe
```

### 2. Fase de recopilación de información

#### 2.1 Identificación del runtime del contenedor

| Ítem de verificación | Comando | Criterio de evaluación |
|--------|------|----------|
| Si está en un contenedor | `cat /proc/1/cgroup` | Contiene `docker`/`kubepods`/`containerd` |
| Archivo indicador de Docker | `ls /.dockerenv` | Si el archivo existe, es un contenedor Docker |
| Tipo de runtime del contenedor | `cat /proc/1/cgroup \| head` | `sysbox-fs`→Sysbox, `docker`→Docker |
| Versión del kernel | `uname -r` | Coincide con el alcance de impacto de la CVE |
| User Namespace | `cat /proc/self/uid_map` | `0 0 4294967295`→sin aislamiento (peligroso) |
| Capabilities | `cat /proc/self/status \| grep Cap` | Tras decodificar, verificar Caps peligrosas |
| Seccomp | `cat /proc/self/status \| grep Seccomp` | 0=deshabilitado, 2=filtro |
| AppArmor | `cat /proc/self/attr/current` | `unconfined`→sin protección |
| Puntos de montaje | `mount \| grep -v overlay` | Detectar montajes de rutas sensibles del host |

#### 2.2 Detección específica de Sysbox

| Ítem de verificación | Método | Impacto de seguridad |
|--------|------|----------|
| Versión CE vs EE | `sysbox-runc --version` o verificar el rango de mapeo UID | El mapeo compartido de CE tiene riesgo entre inquilinos (tenants) |
| Exclusividad del mapeo UID | `cat /proc/self/uid_map`, CE normalmente `0 165536 65536` (compartido) | Mapeo compartido→posible escalamiento de privilegios entre contenedores |
| Virtualización de /proc | `ls /proc/sys/net/` | Grado de virtualización de Sysbox |
| Docker-in-Docker | `docker ps 2>/dev/null` | El Docker interno puede no tener restricciones de seguridad |
| /dev/kvm | `ls /dev/kvm` | KVM disponible→escape mediante virtualización anidada |

### 3. Fase de evaluación de aislamiento

#### 3.1 Aislamiento de procesos

```bash
# Verificación de PID Namespace
ps aux   # Comprobar si se pueden ver procesos de otros contenedores/del host
ls /proc/*/cmdline   # Enumerar procesos visibles

# Si el PID 1 no es el init del contenedor sino systemd/dockerd → falla de aislamiento
cat /proc/1/cmdline | tr '\0' ' '
```

#### 3.2 Aislamiento de red

```bash
# Interfaces de red
ip addr   # Verificar interfaces de red y segmento IP
ip route  # Tabla de rutas, si se puede alcanzar otros segmentos de red

# Escaneo del mismo segmento de red (descubrir contenedores vecinos)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i alive") &
done; wait

# Sondeo de DNS interno
cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local 2>/dev/null
```

#### 3.3 Aislamiento del sistema de archivos

```bash
# Verificar montajes del sistema de archivos del host
mount | grep -E "ext4|xfs|btrfs" | grep -v overlay
findmnt

# Prueba de path traversal
ls -la /var/lib/sysbox/ 2>/dev/null
ls -la /var/lib/docker/ 2>/dev/null
ls -la /run/containerd/ 2>/dev/null

# Escape mediante enlace simbólico
ln -s /proc/1/root/etc/shadow /tmp/test_escape
cat /tmp/test_escape 2>&1  # Si tiene éxito→falla de aislamiento
```

### 4. Matriz de pruebas de escape

| Ruta de escape | Condición previa | Nivel de peligro | Método de prueba |
|----------|----------|----------|----------|
| cgroup release_agent | CAP_SYS_ADMIN + cgroup v1 | Crítico | Escribir en release_agent para ejecutar comandos en el host |
| Docker Socket | /var/run/docker.sock expuesto | Crítico | Crear un contenedor privilegiado mediante la API |
| /proc/1/root | PID Namespace sin aislar | Crítico | Leer y escribir directamente archivos del host |
| Contenedor privilegiado | Modo --privileged | Crítico | Montar el disco del host |
| Fuga de fd de runc | CVE-2024-21626 | Alto | Aprovechar /proc/self/fd para acceder al host |
| Dirty Pipe | CVE-2022-0847, 5.8≤kernel≤5.16.11 | Alto | Sobrescribir archivos de solo lectura para escalar privilegios |
| OverlayFS | CVE-2023-0386, 5.11≤kernel≤6.2 | Alto | Escalamiento de privilegios mediante archivo SUID |
| Montaje sensible | Ruta del host montada dentro del contenedor | Alto | Escribir en archivos del host |
| CAP_DAC_READ_SEARCH | Capability sin limitar | Medio | open_by_handle_at para leer archivos |
| CAP_SYS_PTRACE | Capability sin limitar | Medio | Inyectar en procesos del host |
| Docker-in-Docker | Docker interno sin restricciones | Medio | Crear un contenedor privilegiado en la capa interna |

### 5. Pruebas de persistencia

> Verificar la viabilidad de ataques de persistencia entre sesiones del sandbox (especialmente aplicable a sandboxes persistentes como Daytona)

| Ítem de prueba | Operación en sesión 1 | Verificación en sesión 2 | Resultado de seguridad esperado |
|--------|-----------|-----------|-------------|
| Puerta trasera en .bashrc | `echo 'malicious_cmd' >> ~/.bashrc` | Abrir un shell nuevo y verificar si se ejecuta | La nueva sesión no hereda/se restablece |
| Crontab | `echo "* * * * * cmd" \| crontab -` | `crontab -l` | El crontab se limpia o no está disponible |
| Clave SSH | Escribir en ~/.ssh/authorized_keys | Prueba de conexión SSH | El servicio SSH no está disponible o la clave se limpia |
| Proceso en segundo plano | `nohup cmd &` | `ps aux \| grep cmd` | El proceso termina al cerrar la sesión |
| Envenenamiento de archivos | Escribir un archivo malicioso en el área de trabajo | Si la IA lo lee y ejecuta | La IA no ejecuta automáticamente instrucciones dentro de archivos |
| Residuo de historial | Introducir un comando sensible en el shell | `cat ~/.bash_history` | El historial de comandos se limpia entre sesiones |
| Variable de entorno | `export SECRET=leaked` | `echo $SECRET` | La variable de entorno no persiste entre sesiones |

### 6. Pruebas de movimiento lateral

```
Dentro del contenedor → Descubrimiento de servicios de la red interna → Conexión directa a base de datos/caché/API → Sandbox de otros inquilinos
         ↓
         Servicio de metadatos en la nube (169.254.169.254) → Robo de credenciales IAM → Acceso a recursos en la nube
         ↓
         API de K8s (kubernetes.default.svc) → Obtención de lista de Pods/Secrets
```

| Objetivo | Comando de detección | Método de explotación |
|------|----------|----------|
| Metadatos en la nube | `curl 169.254.169.254` | Obtener credenciales temporales de IAM |
| API de K8s | `curl -k https://kubernetes.default.svc` | Listar Pods/obtener Secrets |
| ServiceAccount de K8s | `cat /var/run/secrets/kubernetes.io/serviceaccount/token` | Autenticarse ante la API de K8s |
| Base de datos de la red interna | `echo \| nc DB_HOST 5432` | Conexión directa a la base de datos |
| Redis | `redis-cli -h REDIS_HOST ping` | Acceso no autorizado |
| Docker Registry | `curl http://REGISTRY:5000/v2/_catalog` | Extraer imágenes sensibles |

### 7. Checklist de verificación de defensa

```
[ ] El contenedor se ejecuta con un usuario no root (o el User Namespace está aislado correctamente)
[ ] Sin Capabilities excedentes (principio mínimo: solo elementos necesarios como NET_BIND_SERVICE)
[ ] El perfil de Seccomp está habilitado (no deshabilitado)
[ ] AppArmor/SELinux no está en modo unconfined
[ ] /var/run/docker.sock no está expuesto
[ ] No se ejecuta en modo --privileged
[ ] No hay montajes de rutas sensibles del host (/, /etc, /var/run)
[ ] La versión del kernel no está afectada por CVE de escape conocidas
[ ] cgroup v2 o release_agent no es escribible
[ ] El aislamiento del PID Namespace es efectivo (solo se ven los propios procesos)
[ ] Network Policy/firewall limita la comunicación entre contenedores
[ ] El servicio de metadatos 169.254.169.254 está bloqueado
[ ] Los datos sensibles entre sesiones (historial/credenciales) se limpian
[ ] Al destruir el sandbox se eliminan por completo todos los datos del usuario
[ ] Sysbox usa la versión EE o mapeo UID exclusivo
```

---
