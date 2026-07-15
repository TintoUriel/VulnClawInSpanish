# Contrabando de solicitudes
English: Request Smuggling
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Contrabando CL-TE
- ID: smuggling-cl-te
- Difficulty: advanced
- Subcategory: CL-TE
- Tags: smuggling, request, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-cl-te.md
Description:
Contrabando mediante Content-Length y Transfer-Encoding
Prerequisites:
- El objetivo usa múltiples capas de proxy
- Existe diferencia de procesamiento entre frontend y backend
Execution Outline:
1. CL-TE básico
2. TE-CL básico
3. TE-TE
## Contrabando CL-CL
- ID: smuggling-cl-cl
- Difficulty: advanced
- Subcategory: CL-CL
- Tags: smuggling, cl-cl, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-cl-cl.md
Description:
Explota que el proxy frontend y el servidor backend procesan simultáneamente la cabecera Content-Length pero difieren en el tratamiento de múltiples cabeceras CL, para lograr contrabando de solicitudes HTTP
Prerequisites:
- Existe una arquitectura de proxy frontend (como HAProxy/Nginx) + servidor backend
- Hay diferencias en el análisis de la cabecera Content-Length entre ambos extremos
- Comprensión de los principios del contrabando de solicitudes HTTP
Execution Outline:
1. Detectar las condiciones para el contrabando CL-CL
2. POC de contrabando de solicitudes CL-CL
3. Explotar el contrabando CL-CL para eludir el control de acceso del frontend
## Contrabando TE-CL
- ID: smuggling-te-cl
- Difficulty: expert
- Subcategory: TE-CL
- Tags: smuggling, te-cl, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-te-cl.md
Description:
Explota la diferencia en que el frontend usa Transfer-Encoding mientras el backend usa Content-Length, para lograr contrabando de solicitudes HTTP
Prerequisites:
- El proxy frontend prioriza el procesamiento de Transfer-Encoding
- El servidor backend prioriza el procesamiento de Content-Length
- Comprensión del formato de codificación chunked
Execution Outline:
1. Detectar la diferencia TE-CL
2. POC de contrabando TE-CL
3. Secuestro de solicitudes mediante contrabando TE-CL
## Contrabando TE-TE
- ID: smuggling-te-te
- Difficulty: expert
- Subcategory: TE-TE
- Tags: smuggling, te-te, http
- Original Extracted Source: original extracted web-security-wiki source/smuggling-te-te.md
Description:
Explota las diferencias en el manejo de distintas variantes de ofuscación de la cabecera Transfer-Encoding entre el frontend y el backend, para lograr contrabando de solicitudes
Prerequisites:
- Tanto el frontend como el backend soportan Transfer-Encoding
- Es posible, mediante ofuscación de la cabecera TE, hacer que uno de los extremos la ignore
- Comprensión de la codificación chunked y los principios del contrabando HTTP
Execution Outline:
1. Sondeo de variantes de ofuscación de TE
2. Explotación de contrabando TE-TE (el frontend ignora el TE ofuscado)
3. Ataque de envenenamiento de caché mediante TE-TE
</content>
