"""VulnClaw Crypto Toolkit — encoding/decoding, encryption/decryption utilities.

Provides a unified interface for common crypto operations encountered
during penetration testing and CTF challenges.

All functions return a dict with:
  - "success": bool
  - "result": str (the output)
  - "error": str (if failed)
"""

from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import urllib.parse
from typing import Any, Optional

# ── Morse Code Tables ────────────────────────────────────────────────

MORSE_ENCODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "'": ".----.",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "$": "...-..-",
    "@": ".--.-.",
}

MORSE_DECODE = {v: k for k, v in MORSE_ENCODE.items()}

# ── Base58 Alphabet ──────────────────────────────────────────────────

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# ── Operation Registry ──────────────────────────────────────────────

OPERATIONS: dict[str, dict[str, Any]] = {}


def _register(
    name: str,
    category: str,
    description: str,
    required_params: list[str],
    optional_params: dict[str, str] | None = None,
):
    """Decorator to register a crypto operation."""

    def decorator(func):
        OPERATIONS[name] = {
            "function": func,
            "category": category,
            "description": description,
            "required_params": required_params,
            "optional_params": optional_params or {},
        }
        return func

    return decorator


# ── Encoding / Decoding Operations ───────────────────────────────────


@_register("base64_encode", "encode", "Codificación Base64", ["input"])
def _base64_encode(input_str: str, **_) -> dict:
    encoded = base64.b64encode(input_str.encode("utf-8")).decode("ascii")
    return {"success": True, "result": encoded}


@_register("base64_decode", "decode", "Decodificación Base64", ["input"])
def _base64_decode(input_str: str, **_) -> dict:
    cleaned = input_str.strip()
    missing_padding = len(cleaned) % 4
    padded = cleaned + ("=" * (4 - missing_padding) if missing_padding else "")
    decoder_kwargs = {"altchars": b"-_"} if any(char in cleaned for char in "-_") else {}
    try:
        decoded = base64.b64decode(padded, validate=True, **decoder_kwargs).decode(
            "utf-8", errors="replace"
        )
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Base64: {e}"}


@_register("base32_encode", "encode", "Codificación Base32", ["input"])
def _base32_encode(input_str: str, **_) -> dict:
    encoded = base64.b32encode(input_str.encode("utf-8")).decode("ascii")
    return {"success": True, "result": encoded}


@_register("base32_decode", "decode", "Decodificación Base32", ["input"])
def _base32_decode(input_str: str, **_) -> dict:
    try:
        cleaned = input_str.strip().upper()
        missing_padding = len(cleaned) % 8
        if missing_padding:
            cleaned += "=" * (8 - missing_padding)
        decoded = base64.b32decode(cleaned).decode("utf-8", errors="replace")
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Base32: {e}"}


@_register("base58_encode", "encode", "Codificación Base58 (Bitcoin)", ["input"])
def _base58_encode(input_str: str, **_) -> dict:
    try:
        num = int.from_bytes(input_str.encode("utf-8"), "big")
        result = ""
        while num > 0:
            num, rem = divmod(num, 58)
            result = BASE58_ALPHABET[rem] + result
        # Handle leading zero bytes
        for byte in input_str.encode("utf-8"):
            if byte == 0:
                result = "1" + result
            else:
                break
        return {"success": True, "result": result or "1"}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al codificar Base58: {e}"}


@_register("base58_decode", "decode", "Decodificación Base58 (Bitcoin)", ["input"])
def _base58_decode(input_str: str, **_) -> dict:
    try:
        num = 0
        for char in input_str.strip():
            num = num * 58 + BASE58_ALPHABET.index(char)
        # Count leading '1's
        leading_zeros = 0
        for char in input_str.strip():
            if char == "1":
                leading_zeros += 1
            else:
                break
        result_bytes = num.to_bytes((num.bit_length() + 7) // 8, "big") if num else b""
        result_bytes = b"\x00" * leading_zeros + result_bytes
        return {"success": True, "result": result_bytes.decode("utf-8", errors="replace")}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Base58: {e}"}


@_register("hex_encode", "encode", "Codificación Hex", ["input"])
def _hex_encode(input_str: str, **_) -> dict:
    encoded = input_str.encode("utf-8").hex()
    return {"success": True, "result": encoded}


@_register("hex_decode", "decode", "Decodificación Hex", ["input"])
def _hex_decode(input_str: str, **_) -> dict:
    try:
        cleaned = input_str.strip()
        # Remove common prefixes
        if cleaned.lower().startswith("0x"):
            cleaned = cleaned[2:]
        # Remove spaces
        cleaned = cleaned.replace(" ", "")
        decoded = bytes.fromhex(cleaned).decode("utf-8", errors="replace")
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Hex: {e}"}


@_register("url_encode", "encode", "Codificación URL", ["input"])
def _url_encode(input_str: str, **_) -> dict:
    encoded = urllib.parse.quote(input_str, safe="")
    return {"success": True, "result": encoded}


@_register("url_decode", "decode", "Decodificación URL", ["input"])
def _url_decode(input_str: str, **_) -> dict:
    try:
        decoded = urllib.parse.unquote(input_str.strip())
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar URL: {e}"}


@_register("html_encode", "encode", "Codificación de entidades HTML", ["input"])
def _html_encode(input_str: str, **_) -> dict:
    encoded = html.escape(input_str, quote=True)
    return {"success": True, "result": encoded}


@_register("html_decode", "decode", "Decodificación de entidades HTML", ["input"])
def _html_decode(input_str: str, **_) -> dict:
    try:
        decoded = html.unescape(input_str.strip())
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar HTML: {e}"}


@_register("unicode_encode", "encode", "Codificación de escape Unicode (\\uXXXX)", ["input"])
def _unicode_encode(input_str: str, **_) -> dict:
    encoded = input_str.encode("unicode_escape").decode("ascii")
    return {"success": True, "result": encoded}


@_register("unicode_decode", "decode", "Decodificación de escape Unicode (\\uXXXX)", ["input"])
def _unicode_decode(input_str: str, **_) -> dict:
    try:
        decoded = input_str.strip().encode("ascii", errors="ignore").decode("unicode_escape")
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Unicode: {e}"}


@_register("rot13_encode", "encode", "Codificación ROT13 (autoinversa, codificar equivale a decodificar)", ["input"])
def _rot13(input_str: str, **_) -> dict:
    import codecs

    result = codecs.encode(input_str, "rot_13")
    return {"success": True, "result": result}


# Alias: rot13_decode is the same as rot13_encode
_register("rot13_decode", "decode", "Decodificación ROT13 (autoinversa)", ["input"])(_rot13)


@_register(
    "caesar_encode",
    "encode",
    "Codificación con cifrado César (cifrado por desplazamiento)",
    ["input"],
    {"shift": "Cantidad de desplazamiento, por defecto 3"},
)
def _caesar_encode(input_str: str, shift: int = 3, **_) -> dict:
    result = []
    for char in input_str:
        if char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return {"success": True, "result": "".join(result)}


@_register(
    "caesar_decode",
    "decode",
    "Decodificación con cifrado César (fuerza bruta con todos los desplazamientos)",
    ["input"],
    {"shift": "Cantidad de desplazamiento; si no se proporciona, devuelve las 25 posibilidades"},
)
def _caesar_decode(input_str: str, shift: Optional[int] = None, **_) -> dict:
    if shift is not None:
        result = []
        for char in input_str:
            if char.isalpha():
                base = ord("A") if char.isupper() else ord("a")
                result.append(chr((ord(char) - base - shift) % 26 + base))
            else:
                result.append(char)
        return {"success": True, "result": "".join(result)}

    # Brute force all 25 shifts
    results = []
    for s in range(1, 26):
        decoded = []
        for char in input_str:
            if char.isalpha():
                base = ord("A") if char.isupper() else ord("a")
                decoded.append(chr((ord(char) - base - s) % 26 + base))
            else:
                decoded.append(char)
        results.append(f"shift={s}: {''.join(decoded)}")
    return {"success": True, "result": "\n".join(results)}


@_register("morse_encode", "encode", "Codificación en código Morse", ["input"])
def _morse_encode(input_str: str, **_) -> dict:
    result = []
    for char in input_str.upper():
        if char == " ":
            result.append("/")
        elif char in MORSE_ENCODE:
            result.append(MORSE_ENCODE[char])
        else:
            result.append("?")
    return {"success": True, "result": " ".join(result)}


@_register("morse_decode", "decode", "Decodificación de código Morse", ["input"])
def _morse_decode(input_str: str, **_) -> dict:
    try:
        words = input_str.strip().split("/")
        result = []
        for word in words:
            letters = word.strip().split()
            for letter in letters:
                if letter in MORSE_DECODE:
                    result.append(MORSE_DECODE[letter])
                else:
                    result.append("?")
            result.append(" ")
        return {"success": True, "result": "".join(result).strip()}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar Morse: {e}"}


# ── Hash Operations ──────────────────────────────────────────────────


@_register("md5_hash", "hash", "Hash MD5", ["input"])
def _md5_hash(input_str: str, **_) -> dict:
    result = hashlib.md5(input_str.encode("utf-8")).hexdigest()
    return {"success": True, "result": result}


@_register("sha1_hash", "hash", "Hash SHA1", ["input"])
def _sha1_hash(input_str: str, **_) -> dict:
    result = hashlib.sha1(input_str.encode("utf-8")).hexdigest()
    return {"success": True, "result": result}


@_register("sha256_hash", "hash", "Hash SHA256", ["input"])
def _sha256_hash(input_str: str, **_) -> dict:
    result = hashlib.sha256(input_str.encode("utf-8")).hexdigest()
    return {"success": True, "result": result}


@_register("sha512_hash", "hash", "Hash SHA512", ["input"])
def _sha512_hash(input_str: str, **_) -> dict:
    result = hashlib.sha512(input_str.encode("utf-8")).hexdigest()
    return {"success": True, "result": result}


# ── JWT Operations ───────────────────────────────────────────────────


@_register("jwt_decode", "decode", "Decodificación de JWT (Header + Payload)", ["input"])
def _jwt_decode(input_str: str, **_) -> dict:
    try:
        parts = input_str.strip().split(".")
        if len(parts) != 3:
            return {
                "success": False,
                "result": "",
                "error": "El JWT debe contener 3 partes (header.payload.signature)",
            }

        # Decode header (base64url)
        header_b64 = parts[0]
        missing = len(header_b64) % 4
        if missing:
            header_b64 += "=" * (4 - missing)
        header = json.loads(base64.urlsafe_b64decode(header_b64))

        # Decode payload (base64url)
        payload_b64 = parts[1]
        missing = len(payload_b64) % 4
        if missing:
            payload_b64 += "=" * (4 - missing)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        result = json.dumps({"header": header, "payload": payload}, ensure_ascii=False, indent=2)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al decodificar JWT: {e}"}


@_register(
    "jwt_encode",
    "encode",
    "Codificación de JWT (requiere header, payload, secret)",
    ["input"],
    {"header": "JWT header JSON", "secret": "Clave de firma", "algorithm": "Algoritmo de firma, por defecto HS256"},
)
def _jwt_encode(
    input_str: str,
    header: str = '{"alg":"HS256","typ":"JWT"}',
    secret: str = "",
    algorithm: str = "HS256",
    **_,
) -> dict:
    try:
        import hmac

        header_data = json.loads(header)
        payload_data = json.loads(input_str)

        header_b64 = (
            base64.urlsafe_b64encode(json.dumps(header_data, separators=(",", ":")).encode())
            .rstrip(b"=")
            .decode()
        )

        payload_b64 = (
            base64.urlsafe_b64encode(json.dumps(payload_data, separators=(",", ":")).encode())
            .rstrip(b"=")
            .decode()
        )

        signing_input = f"{header_b64}.{payload_b64}"

        if algorithm == "HS256" and secret:
            sig = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
            sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        elif algorithm == "none":
            sig_b64 = ""
        else:
            return {"success": False, "result": "", "error": f"Algoritmo aún no compatible: {algorithm}"}

        return {"success": True, "result": f"{signing_input}.{sig_b64}"}
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al codificar JWT: {e}"}


# ── AES Operations ───────────────────────────────────────────────────


@_register(
    "aes_encrypt",
    "encrypt",
    "Cifrado AES (modo CBC, relleno PKCS7)",
    ["input"],
    {"key": "Clave (16/24/32 bytes)", "iv": "Vector de inicialización (16 bytes, por defecto igual a la clave)"},
)
def _aes_encrypt(input_str: str, key: str = "", iv: str = "", **_) -> dict:
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad

        key_bytes = key.encode("utf-8") if key else b"0123456789abcdef"
        iv_bytes = (iv.encode("utf-8") if iv else key_bytes)[:16]

        if len(key_bytes) not in (16, 24, 32):
            return {"success": False, "result": "", "error": "La clave AES debe tener 16/24/32 bytes"}

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        padded = pad(input_str.encode("utf-8"), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return {"success": True, "result": base64.b64encode(encrypted).decode()}
    except ImportError:
        return {
            "success": False,
            "result": "",
            "error": "Se requiere instalar pycryptodome: pip install pycryptodome",
        }
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al cifrar con AES: {e}"}


@_register(
    "aes_decrypt",
    "decrypt",
    "Descifrado AES (modo CBC, relleno PKCS7)",
    ["input"],
    {"key": "Clave (16/24/32 bytes)", "iv": "Vector de inicialización (16 bytes, por defecto igual a la clave)"},
)
def _aes_decrypt(input_str: str, key: str = "", iv: str = "", **_) -> dict:
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad

        key_bytes = key.encode("utf-8") if key else b"0123456789abcdef"
        iv_bytes = (iv.encode("utf-8") if iv else key_bytes)[:16]

        if len(key_bytes) not in (16, 24, 32):
            return {"success": False, "result": "", "error": "La clave AES debe tener 16/24/32 bytes"}

        encrypted = base64.b64decode(input_str.strip())
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return {"success": True, "result": decrypted.decode("utf-8", errors="replace")}
    except ImportError:
        return {
            "success": False,
            "result": "",
            "error": "Se requiere instalar pycryptodome: pip install pycryptodome",
        }
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al descifrar con AES: {e}"}


# ── Auto-detect decode ───────────────────────────────────────────────


@_register("auto_decode", "decode", "Detecta automáticamente el tipo de codificación y decodifica (prueba todas las codificaciones comunes)", ["input"])
def _auto_decode(input_str: str, **_) -> dict:
    """Try to auto-detect the encoding and decode the input."""
    results = []
    s = input_str.strip()

    # 1. URL decode
    if "%" in s:
        try:
            decoded = urllib.parse.unquote(s)
            if decoded != s:
                results.append(f"[Decodificación URL] {decoded}")
        except Exception:
            pass

    # 2. HTML entity decode
    if "&" in s and ("#" in s or s.count(";") > 0):
        try:
            decoded = html.unescape(s)
            if decoded != s:
                results.append(f"[Decodificación HTML] {decoded}")
        except Exception:
            pass

    # 3. Unicode escape decode
    if "\\u" in s:
        try:
            decoded = s.encode("ascii", errors="ignore").decode("unicode_escape")
            results.append(f"[Decodificación Unicode] {decoded}")
        except Exception:
            pass

    # 4. Base64 decode
    if re.match(r"^[A-Za-z0-9+/]+=*$", s) and len(s) >= 4:
        try:
            cleaned = s
            missing = len(cleaned) % 4
            if missing:
                cleaned += "=" * (4 - missing)
            decoded = base64.b64decode(cleaned).decode("utf-8", errors="strict")
            if decoded and any(c.isprintable() for c in decoded):
                results.append(f"[Decodificación Base64] {decoded}")
        except Exception:
            pass

    # 5. Base64url decode (for JWT-like)
    if re.match(r"^[A-Za-z0-9_-]+$", s) and len(s) >= 4:
        try:
            cleaned = s
            missing = len(cleaned) % 4
            if missing:
                cleaned += "=" * (4 - missing)
            decoded = base64.urlsafe_b64decode(cleaned).decode("utf-8", errors="strict")
            if decoded and any(c.isprintable() for c in decoded):
                results.append(f"[Decodificación Base64URL] {decoded}")
        except Exception:
            pass

    # 6. Base32 decode
    if re.match(r"^[A-Z2-7]+=*$", s.upper()) and len(s) >= 8:
        try:
            cleaned = s.upper()
            missing = len(cleaned) % 8
            if missing:
                cleaned += "=" * (8 - missing)
            decoded = base64.b32decode(cleaned).decode("utf-8", errors="strict")
            if decoded:
                results.append(f"[Decodificación Base32] {decoded}")
        except Exception:
            pass

    # 7. Hex decode
    if re.match(r"^[0-9a-fA-F]+$", s) and len(s) % 2 == 0 and len(s) >= 2:
        try:
            decoded = bytes.fromhex(s).decode("utf-8", errors="strict")
            if decoded and any(c.isprintable() for c in decoded):
                results.append(f"[Decodificación Hex] {decoded}")
        except Exception:
            pass

    # 8. Morse decode
    if set(s) <= {".", "-", " ", "/"} and ("." in s or "-" in s):
        try:
            decoded = _morse_decode(s)
            if decoded["success"]:
                results.append(f"[Decodificación Morse] {decoded['result']}")
        except Exception:
            pass

    # 9. ROT13
    if s.isalpha():
        import codecs

        try:
            decoded = codecs.encode(s, "rot_13")
            if decoded != s:
                results.append(f"[Decodificación ROT13] {decoded}")
        except Exception:
            pass

    if not results:
        return {"success": False, "result": "", "error": "No se pudo identificar automáticamente el tipo de codificación"}

    return {"success": True, "result": "\n".join(results)}


# ── Public API ───────────────────────────────────────────────────────


def execute(operation: str, input_str: str, **kwargs) -> dict:
    """Execute a crypto operation by name.

    Args:
        operation: The operation name (e.g., "base64_decode", "md5_hash")
        input_str: The input string to process
        **kwargs: Additional parameters (e.g., key, iv, shift)

    Returns:
        Dict with success, result, and optional error.
    """
    if operation not in OPERATIONS:
        available = ", ".join(sorted(OPERATIONS.keys()))
        return {
            "success": False,
            "result": "",
            "error": f"Operación desconocida: {operation}. Operaciones disponibles: {available}",
        }

    func = OPERATIONS[operation]["function"]
    try:
        return func(input_str=input_str, **kwargs)
    except Exception as e:
        return {"success": False, "result": "", "error": f"Error al ejecutar {operation}: {e}"}


def list_operations() -> dict[str, dict[str, str]]:
    """List all available operations with their descriptions."""
    return {
        name: {
            "category": info["category"],
            "description": info["description"],
            "required_params": ", ".join(info["required_params"]),
            "optional_params": ", ".join(f"{k}({v})" for k, v in info["optional_params"].items()),
        }
        for name, info in sorted(OPERATIONS.items())
    }
