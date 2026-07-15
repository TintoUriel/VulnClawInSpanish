# 🦞 War Stories — Biblioteca de experiencias reales de VulnClaw

Aquí se guardan los reportes reales de pentesting/resolución de retos CTF de VulnClaw.

Cada reporte documenta la cadena de ataque completa: desde la recopilación de información hasta la flag final, incluyendo los caminos equivocados que se tomaron y dónde estuvo el punto de quiebre clave.

## Reglas de nomenclatura de archivos

```
YYYY-MM-DD_tipo-de-reto_palabras-clave.md
```

Por ejemplo: `2026-04-19_php-deserialization_regex-bypass.md`

## Plantilla de reporte

Cada reporte debe incluir:

| Sección | Contenido |
|------|------|
| **Metainformación** | Fecha, objetivo, tipo, palabras clave, número de rondas, cadena de herramientas |
| **Cadena de ataque** | Qué se hizo en cada paso y qué se descubrió |
| **Quiebre clave** | Qué paso fue decisivo y por qué |
| **Caminos equivocados** | Qué intentos fallaron y por qué |
| **Payload** | Código de explotación final reproducible |
| **Resumen de la experiencia** | Metodología transferible a retos similares |

## Índice de reportes

| Fecha | Reto | Tipo | Rondas | Enlace |
|------|------|------|------|------|
| 2026-04-19 | NSSCTF PHP bypass de expresión regular | Web / PHP / bypass de regex | 14 | [→](./2026-04-19_php-deserialization_regex-bypass.md) |
