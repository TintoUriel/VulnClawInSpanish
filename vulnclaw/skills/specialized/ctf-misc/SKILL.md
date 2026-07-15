---
name: ctf-misc
description: Base de conocimiento de misceláneos CTF — escape de Jail en Python, escape de Jail en Bash, identificación y decodificación de cadenas de codificación, esteganografía QR/audio/imagen, reversing de VM de juegos, navegación de la API de CTFd, escalada de privilegios en Linux
---

# Base de conocimiento de misceláneos CTF

Base de conocimiento práctica para retos de CTF Misc, que cubre categorías variadas como **escape de sandbox, identificación de cadenas de codificación, esteganografía y reversing de juegos**.

## Enrutamiento de escenarios

| Escenario | Documento de referencia | Contenido principal |
|------|---------|---------|
| Escape de sandbox en Python | `python-jail-escape.md` | `__import__`/func\_globals/cadenas de eval |
| Escape de sandbox en Bash | `bash-jail-escape.md` | HISTFILE/ctypes.sh/escape del editor vi |
| Identificación y decodificación de cadenas de codificación | `encoding-chain-reference.md` | Base64→Hex→ROT13 anidamiento multicapa |
| Reversing de VM de juegos/personalizadas | `game-and-vm-reverse.md` | WASM/Brainfuck/resolución de restricciones con Z3 |
| Operaciones en la plataforma CTFd | `ctfd-platform-guide.md` | Descarga de adjuntos vía API/envío de flag |
| Escalada de privilegios en Linux | `linux-privesc-quick.md` | SUID/sudo/cron/vulnerabilidades de kernel |

## Identificación rápida

| Característica del reto | Posible tema | Referencia recomendada |
|---------|---------|---------|
| Campo de entrada con exec/eval de Python | Escape de PyJail | python-jail-escape.md |
| Línea de comandos con bash restringido | Escape de BashJail | bash-jail-escape.md |
| Cadena con codificación extraña | Decodificación de cadenas de codificación | encoding-chain-reference.md |
| Código QR/archivo de audio | Esteganografía | encoding-chain-reference.md |
| Binario de juego/WASM | Reversing de VM personalizada | game-and-vm-reverse.md |
| Plataforma CTFtime / CTFd | API de la plataforma | ctfd-platform-guide.md |
| Se proporciona una shell | Escalada de privilegios en Linux | linux-privesc-quick.md |
