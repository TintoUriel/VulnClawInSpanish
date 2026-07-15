# Plantilla de reporte de HackerOne y referencia de análisis de scope

Esta referencia es para uso del Skill `hackerone`: a la derecha está la forma objetivo del **análisis de scope**, a la izquierda
la plantilla de reporte en **formato de envío de HackerOne**. Los términos técnicos se mantienen en su idioma original (inglés).

## 1. Referencia de análisis de scope

### 1.1 asset type (human label ↔ API enum)

| Human label            | API enum                                   | Procesable directamente por pentest-flow |
| ---------------------- | ------------------------------------------ | ----------------------- |
| Domain / URL           | `URL`                                      | ✅                      |
| Wildcard `*.x.com`     | `WILDCARD`                                 | ✅                      |
| IP range / CIDR        | `CIDR`                                     | ⚠️ Requiere confirmación (puede estar restringido)   |
| Source code            | `SOURCE_CODE`                              | ❌ Manual                 |
| Android app            | `GOOGLE_PLAY_APP_ID` / `OTHER_APK`         | ❌ Requiere flujo dedicado           |
| iOS app                | `APPLE_STORE_APP_ID` / `TESTFLIGHT` / `OTHER_IPA` | ❌ Requiere flujo dedicado    |
| Hardware               | `HARDWARE`                                 | ❌ Manual                 |
| AI Model               | `AI_MODEL`                                 | ❌ Manual                 |
| Smart Contract         | `SMART_CONTRACT`                           | ❌ Manual                 |
| Other / ASN            | `OTHER`                                    | ⚠️ Requiere confirmación               |

### 1.2 Triple estado de eligibility (submission × bounty, dos booleanos independientes)

| submission | bounty | Significado                                    | Comportamiento             |
| ---------- | ------ | --------------------------------------- | ---------------- |
| true       | true   | in scope, se puede probar, con recompensa                  | Prueba normal         |
| true       | false  | in scope, se puede probar, **sin recompensa**              | Prueba normal (no omitir)|
| false      | —      | **out of scope**                        | **Nunca tocar**     |

### 1.3 Forma objetivo de la tabla de scope pegada (lenient parse)

```
In scope:
https://api.example.com        | URL       | Eligible for bounty
*.example.com                  | WILDCARD  | Eligible for bounty
app.example.com                | URL       | In scope, NOT bounty-eligible
com.example.android            | GOOGLE_PLAY_APP_ID | Eligible for bounty

Out of scope:
blog.example.com               | URL
*.corp.example.com             | WILDCARD
```

Puntos clave del análisis:
- De cada línea, extraer al menos el **identificador del asset** y la **pertenencia in/out**; identificar type y eligibility en la medida de lo posible.
- El orden de las columnas y los separadores (`|`, tab, espacios múltiples) pueden variar — hacer coincidencia flexible por token.
- Para cualquier línea cuya pertenencia no pueda determinarse, **confirmar con el usuario, nunca asumir por defecto in-scope**.

## 2. Checklist obligatoria de reglas del programa

Verificar cada punto antes de probar cualquier asset:

- **sin DoS / sin impacto en la disponibilidad** —— prohibidas las pruebas de estrés, el agotamiento de recursos, la concurrencia masiva.
- **rate limit / límite de automatización** —— baja velocidad y en serie; respetar la cláusula "no automated scanning".
- **sin ingeniería social** —— no dirigirse a personas, no phishing.
- **impacto mínimo / sin exfiltración de PII** —— detenerse en cuanto se verifique, no exportar datos reales de usuarios.
- Se superpone a los `BLOCKED_PATTERNS` / `RESERVED_IP_RANGES` ya existentes de VulnClaw.

## 3. Plantilla de reporte en formato de envío de HackerOne

Cada finding debe usar la siguiente estructura:

```markdown
### [Title] <tipo de vulnerabilidad> on <asset>

**Asset:** <asset in-scope afectado (URL / identificador)>

**Severity (CVSS):** <Critical | High | Medium | Low> —
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N` (score: X.X)

**Steps to Reproduce:**
1. <paso, incluyendo solicitud / respuesta / payload>
2. ...

**Impact:**
<explotabilidad e impacto en el negocio>

**Remediation:**
<recomendaciones de corrección>

**Proof of Concept:**
(adjuntar PoC en Python parametrizable, librería requests; solo para verificación, sin carácter destructivo)
```

Recordatorio: el reporte es solo para que el usuario lo **envíe manualmente** en HackerOne, el Skill no lo envía automáticamente.
