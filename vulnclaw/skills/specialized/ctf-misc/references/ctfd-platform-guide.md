# Guía de operación de la plataforma CTFd

## Fundamentos de la API de CTFd

```python
import requests

CTFD_URL = "https://ctf.example.com"
session = requests.Session()

def login(username, password):
    """Iniciar sesión en CTFd"""
    r = session.post(f"{CTFD_URL}/login", data={
        "name": username,
        "password": password,
    })
    return r

def get_challenges():
    """Obtener todos los retos"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges")
    return r.json()

def get_challenge_detail(chal_id):
    """Obtener el detalle de un reto individual"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}")
    return r.json()

def get_challenge_files(chal_id):
    """Obtener los archivos adjuntos del reto"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}/files")
    return r.json()

def download_file(file_id):
    """Descargar un archivo del reto"""
    r = session.get(f"{CTFD_URL}/api/v1/files/{file_id}")
    return r.content

def submit_flag(flag):
    """Enviar la flag"""
    r = session.post(f"{CTFD_URL}/api/v1/challenges/attempt", json={
        "challenge_id": chal_id,
        "submission": flag,
    })
    return r.json()

def get_scoreboard():
    """Obtener la tabla de clasificación"""
    r = session.get(f"{CTFD_URL}/api/v1/scoreboard")
    return r.json()

def get_user_info():
    """Obtener la información del usuario actual"""
    r = session.get(f"{CTFD_URL}/api/v1/users/me")
    return r.json()
```

## Detección del tipo de plataforma

```python
def detect_platform(url):
    """Detectar el tipo de plataforma CTF"""
    # CTFd
    r = requests.get(f"{url}/login")
    if 'ctfd' in r.text.lower() or 'csrf_token' in r.text:
        return "CTFd"

    # RBCG / CTFdLight
    if '/static/core' in r.text:
        return "RBCG"

    # HCTF / otras
    return "Unknown"
```

## API común de CTFd

```
GET  /api/v1/challenges          # Todos los retos
GET  /api/v1/challenges/{id}     # Detalle del reto
GET  /api/v1/challenges/{id}/files # Archivos del reto
POST /api/v1/challenges/attempt  # Enviar flag
GET  /api/v1/scoreboard          # Tabla de clasificación
GET  /api/v1/users/me            # Usuario actual
GET  /api/v1/notifications       # Anuncios
```

## Descarga masiva de archivos adjuntos

```python
def download_all_files(url, output_dir):
    """Descargar en bloque todos los archivos adjuntos de los retos"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        try:
            files = get_challenge_files(chal_id)['data']
            for f in files:
                filename = f['filename']
                content = download_file(f['id'])
                with open(os.path.join(output_dir, filename), 'wb') as out:
                    out.write(content)
                print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download challenge {chal_id}: {e}")
```

## Plantilla de resolución automática

```python
def auto_solve(url, username, password, solve_func):
    """Plantilla de resolución automática

    solve_func(challenge_data) -> flag
    """
    session = requests.Session()
    login(username, password)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        detail = get_challenge_detail(chal_id)['data']
        files = get_challenge_files(chal_id)['data']

        print(f"Solving: {detail['name']}")
        flag = solve_func(detail, files)

        if flag:
            result = submit_flag(flag)
            if result.get('data', {}).get('status') == 'correct':
                print(f"[✓] {detail['name']}: {flag}")
            else:
                print(f"[✗] {detail['name']}: Wrong flag")
        else:
            print(f"[-] {detail['name']}: No solve function")
```
