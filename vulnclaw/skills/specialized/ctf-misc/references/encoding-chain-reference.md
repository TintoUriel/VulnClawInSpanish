# Identificación y decodificación de cadenas de codificación

## Características de identificación de codificación

| Codificación | Características | Ejemplo |
|------|------|------|
| Base64 | `A-Za-z0-9+/=`, longitud % 4 | `TnNTY1RmLnBocA==` |
| Base32 | `A-Z2-7=`, longitud % 8 | `OBZHK5DFN2A====` |
| Base16 | `0-9A-F`, longitud par | `4E535354662E706870` |
| Codificación URL | `%XX` | `%2F%61%64%6D%69%6E` |
| Entidad HTML | `&#xNNN;` o `&#NNN;` | `&#x3C;script&#x3E;` |
| Unicode | `\uXXXX` o `\UXXXXXXXX` | `\u003c\u0073\u0063` |
| Hex (Python) | `\xNN` | `\x4e\x53\x53\x54` |
| ROT13 | Sustitución de letras, Caesar | `axzc` → `nmp` |
| Morse | Combinación de `.` `-` `/` | `.-/-.../-.-.` |
| Binary | Secuencia de `01` | `01001101` |

## Cadenas de codificación comunes

### 1. Cadena simple
```
Hex → Base64 → Codificación URL
```

### 2. Familia binaria
```
Binary → ASCII
Octal → ASCII
Hex → ASCII
```

### 3. Familia de navegador
```
Entidad HTML → Codificación URL → Base64
```

### 4. Codificaciones especiales
```
Brainfuck (`><+-.,[]`)
Ook! (`Ook. Ook?`)
Hex → Ook! → Brainfuck
```

## Script de decodificación automática

```python
import base64, binascii, urllib.parse, html

def auto_decode(data, max_iter=10):
    """Intentar automáticamente múltiples capas de decodificación"""
    result = data
    for _ in range(max_iter):
        changed = False
        original = result

        # Decodificación URL
        try:
            result = urllib.parse.unquote(result)
            if result != original:
                changed = True
        except:
            pass

        # Decodificación de entidades HTML
        try:
            result = html.unescape(result)
            if result != original:
                changed = True
        except:
            pass

        # Decodificación Base64
        try:
            result = base64.b64decode(result).decode('utf-8')
            if result != original:
                changed = True
        except:
            try:
                result = base64.b64decode(result + '==').decode('utf-8')
                if result != original:
                    changed = True
            except:
                pass

        # Decodificación hexadecimal
        try:
            if all(c in '0123456789abcdefABCDEF' for c in result.replace('%', '')):
                result = bytes.fromhex(result.replace('%', '')).decode('utf-8')
                if result != original:
                    changed = True
        except:
            pass

        # ROT13
        try:
            result = original.encode().translate(bytes.maketrans(
                b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                b'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
            )).decode()
            if result != original:
                changed = True
        except:
            pass

        if not changed:
            break

    return result
```

## Decodificación de códigos QR

```python
from PIL import Image
import zbarlight

def decode_qr(image_path):
    """Decodificar código QR"""
    image = Image.open(image_path)
    codes = zbarlight.scan_codes(['qrcode'], image)
    return codes
```

## Esteganografía de audio (bit menos significativo)

```python
def extract_lsb_wav(wav_path):
    """Extraer datos ocultos mediante LSB de un archivo WAV"""
    import wave, struct
    with wave.open(wav_path, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
        binary = ''
        for byte in frames:
            binary += str(byte & 1)
    # Cada 8 bits forman un carácter
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result
```

## Esteganografía en imágenes

```python
from PIL import Image

def extract_lsb_png(image_path):
    """Extraer esteganografía LSB de un archivo PNG"""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    binary = ''
    for pixel in pixels:
        if isinstance(pixel, tuple):
            for channel in pixel[:3]:
                binary += str(channel & 1)
        else:
            binary += str(pixel & 1)
    # Cada 8 bits forman un carácter
    result = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            result += chr(int(byte, 2))
    return result
```
