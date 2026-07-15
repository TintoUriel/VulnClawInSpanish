# Ingeniería inversa de juegos y VM personalizadas

## Brainfuck

```python
# Intérprete de Brainfuck
import sys

def brainfuck(code, input_data=''):
    code = ''.join(c for c in code if c in '><+-.,[]')
    tape = [0] * 30000
    ptr = 0
    iptr = 0
    input_ptr = 0
    output = []

    while iptr < len(code):
        op = code[iptr]
        if op == '>':
            ptr += 1
        elif op == '<':
            ptr -= 1
        elif op == '+':
            tape[ptr] = (tape[ptr] + 1) % 256
        elif op == '-':
            tape[ptr] = (tape[ptr] - 1) % 256
        elif op == '.':
            output.append(chr(tape[ptr]))
        elif op == ',':
            if input_ptr < len(input_data):
                tape[ptr] = ord(input_data[input_ptr])
                input_ptr += 1
            else:
                tape[ptr] = 0
        elif op == '[':
            if tape[ptr] == 0:
                depth = 1
                while depth > 0:
                    iptr += 1
                    if code[iptr] == '[':
                        depth += 1
                    elif code[iptr] == ']':
                        depth -= 1
        elif op == ']':
            if tape[ptr] != 0:
                depth = 1
                while depth > 0:
                    iptr -= 1
                    if code[iptr] == '[':
                        depth -= 1
                    elif code[iptr] == ']':
                        depth += 1
        iptr += 1

    return ''.join(output)
```

## Ook!

```python
# Conversión de Ook! a Brainfuck
ook_to_bf = {
    'Ook. Ook?': '>',
    'Ook? Ook.': '<',
    'Ook. Ook.': '+',
    'Ook! Ook!': '-',
    'Ook! Ook.': '.',
    'Ook. Ook!': ',',
    'Ook! Ook?': '[',
    'Ook? Ook!': ']',
}
```

## Flujo de ingeniería inversa de una VM personalizada

```python
# Pasos para analizar una VM personalizada:
# 1. Localizar la tabla de definición de opcodes
# 2. Localizar el código de inicialización de la VM (registros, inicialización de memoria)
# 3. Rastrear el bucle principal (main loop) para encontrar el despacho de instrucciones
# 4. Analizar la función de cada opcode
# 5. Extraer el archivo de bytecode
# 6. Escribir un desensamblador o simular la ejecución directamente

"""
Patrones de opcode comunes:
0x00 = NOP
0x01 = LOAD  (cargar datos)
0x02 = STORE (almacenar datos)
0x03 = ADD
0x04 = SUB
0x05 = JMP
0x06 = JZ    (salto condicional)
0x07 = HALT
"""

class SimpleVM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.regs = [0] * 8
        self.memory = bytecode[256:]  # se asume que los datos van después del código
        self.pc = 0
        self.running = True

    def step(self):
        op = self.bytecode[self.pc]
        if op == 0x01:  # LOAD
            self.pc += 1
            reg = self.bytecode[self.pc]
            self.pc += 1
            addr = self.bytecode[self.pc]
            self.regs[reg] = self.memory[addr]
        elif op == 0x05:  # JMP
            self.pc += 1
            self.pc = self.bytecode[self.pc]
        elif op == 0x07:  # HALT
            self.running = False
        self.pc += 1

    def run(self):
        while self.running and self.pc < len(self.bytecode):
            self.step()
```

## Resolución de restricciones con Z3

```python
from z3 import *

def solve_with_z3(constraints, variables):
    """Resolver restricciones usando Z3"""
    s = Solver()
    for constraint in constraints:
        s.add(constraint)
    if s.check() == sat:
        model = s.model()
        return {v: model[v] for v in variables}
    return None
```

## Análisis de WASM

```python
# Comandos comunes de análisis de wasm
"""
# Extraer cadenas del wasm
strings game.wasm | grep -i flag

# Ver funciones exportadas
wasm-objdump -h game.wasm

# Descompilar al formato de texto wasm
wasm2wat game.wasm -o game.wat

# Ver funciones
wasm-objdump -d game.wasm

# Ejecutar con wasmer o wasmtime
wasmer game.wasm
"""
```
