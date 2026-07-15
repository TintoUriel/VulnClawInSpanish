# Seguridad de API
English: API Security
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Vulnerabilidad de seguridad de JWT
- ID: jwt-security
- Difficulty: intermediate
- Subcategory: JWT
- Tags: jwt, token, authentication
- Original Extracted Source: original extracted web-security-wiki source/jwt-security.md
Description:
Explotación de vulnerabilidades de seguridad de JSON Web Token
Prerequisites:
- Se usa JWT para la autenticación
- Existe un problema en la configuración o validación de JWT
Execution Outline:
1. 1. Decodificar el JWT
2. 2. Ataque de algoritmo None
3. 3. Descifrado de clave débil
4. 4. Ataque de confusión de clave
## Ataque de inyección en GraphQL
- ID: graphql-injection
- Difficulty: intermediate
- Subcategory: GraphQL
- Tags: graphql, api, injection, introspection
- Original Extracted Source: original extracted web-security-wiki source/graphql-injection.md
Description:
Ataque de inyección y fuga de información en API GraphQL
Prerequisites:
- El objetivo usa API GraphQL
- Existe acceso no autorizado o un punto de inyección
Execution Outline:
1. 1. Sondear el endpoint de GraphQL
2. 2. Consulta de introspección
3. 3. Ataque de consultas por lotes
4. 4. Inyección SQL
## Ataque de introspección de GraphQL
- ID: graphql-introspection
- Difficulty: beginner
- Subcategory: Introspección de GraphQL
- Tags: graphql, introspection, enumeration, api
- Original Extracted Source: original extracted web-security-wiki source/graphql-introspection.md
Description:
Explota la funcionalidad de introspección de GraphQL para obtener la estructura de la API
Prerequisites:
- El objetivo usa GraphQL
- La funcionalidad de introspección no está deshabilitada
Execution Outline:
1. 1. Introspección básica
2. 2. Introspección completa
3. 3. Análisis con herramientas
## Ataque de consultas por lotes en GraphQL
- ID: graphql-batching
- Difficulty: intermediate
- Subcategory: Consultas por lotes de GraphQL
- Tags: graphql, batching, rate-limit, bypass
- Original Extracted Source: original extracted web-security-wiki source/graphql-batching.md
Description:
Explota las consultas por lotes de GraphQL para eludir el límite de tasa
Prerequisites:
- El objetivo usa GraphQL
- Existe límite de tasa
Execution Outline:
1. 1. Consulta por lotes mediante alias
2. 2. Consulta por lotes mediante array
3. 3. Fuerza bruta
## Pruebas de seguridad de REST API
- ID: rest-api-security
- Difficulty: intermediate
- Subcategory: REST API
- Tags: rest, api, security, testing
- Original Extracted Source: original extracted web-security-wiki source/rest-api-security.md
Description:
Pruebas de seguridad y explotación de vulnerabilidades en REST API
Prerequisites:
- El objetivo usa REST API
- Se conocen los endpoints de la API
Execution Outline:
1. 1. Descubrimiento de endpoints de la API
2. 2. Pruebas de autenticación
3. 3. Pruebas de métodos HTTP
4. 4. Contaminación de parámetros
## Ataque de algoritmo None en JWT
- ID: jwt-none-alg
- Difficulty: beginner
- Subcategory: Seguridad de JWT
- Tags: jwt, none, algorithm, bypass
- Original Extracted Source: original extracted web-security-wiki source/jwt-none-alg.md
Description:
Explota el algoritmo None de JWT para eludir la verificación de firma
Prerequisites:
- El objetivo usa autenticación JWT
- El servidor no valida correctamente el algoritmo
Execution Outline:
1. 1. Decodificar el JWT
2. 2. Construir un Token con algoritmo None
3. 3. Modificar los permisos del usuario
4. 4. Enviar el Token malicioso
## Ataque de confusión de clave en JWT
- ID: jwt-key-confusion
- Difficulty: intermediate
- Subcategory: Seguridad de JWT
- Tags: jwt, algorithm, confusion, rs256
- Original Extracted Source: original extracted web-security-wiki source/jwt-key-confusion.md
Description:
Explota la confusión de algoritmo de JWT para lograr el bypass de la firma
Prerequisites:
- El objetivo usa el algoritmo RS256
- Es posible obtener la clave pública
Execution Outline:
1. 1. Obtener la clave pública
2. 2. Ataque de confusión de algoritmo
3. 3. Enviar el Token malicioso
## IDOR referencia directa a objetos insegura
- ID: api-idor
- Difficulty: beginner
- Subcategory: IDOR
- Tags: idor, api, authorization, bypass
- Original Extracted Source: original extracted web-security-wiki source/api-idor.md
Description:
Explota la vulnerabilidad IDOR para acceder a recursos no autorizados
Prerequisites:
- El objetivo usa un ID para referenciar recursos
- Existe un defecto en la verificación de autorización
Execution Outline:
1. 1. Identificar el parámetro ID
2. 2. Enumerar el ID
3. 3. Detección masiva
4. 4. Acceso entre usuarios
## Bypass del límite de tasa de la API
- ID: api-rate-limit
- Difficulty: intermediate
- Subcategory: Límite de tasa
- Tags: api, rate-limit, bypass, brute-force
- Original Extracted Source: original extracted web-security-wiki source/api-rate-limit.md
Description:
Elude el límite de tasa de la API para realizar un ataque de fuerza bruta
Prerequisites:
- El objetivo tiene límite de tasa
- La implementación del límite tiene defectos
Execution Outline:
1. 1. Detectar el límite de tasa
2. 2. Bypass por IP
3. 3. Bypass distribuido
4. 4. Otras técnicas de bypass
## Vulnerabilidad de asignación masiva
- ID: api-mass-assignment
- Difficulty: beginner
- Subcategory: Asignación masiva
- Tags: api, mass-assignment, privilege-escalation
- Original Extracted Source: original extracted web-security-wiki source/api-mass-assignment.md
Description:
Explota la vulnerabilidad de asignación masiva para modificar campos sensibles
Prerequisites:
- La API acepta entrada JSON
- Existen campos sin filtrar
Execution Outline:
1. 1. Identificar los campos de entrada
2. 2. Agregar campos sensibles
3. 3. Operación de actualización
4. 4. Objetos anidados
## BOLA quebrantamiento de la autorización a nivel de objeto
- ID: api-bola
- Difficulty: intermediate
- Subcategory: BOLA
- Tags: api, bola, authorization, idor
- Original Extracted Source: original extracted web-security-wiki source/api-bola.md
Description:
Explota la vulnerabilidad BOLA para acceder a objetos no autorizados
Prerequisites:
- La API usa un ID de objeto
- Existe un defecto en la verificación de autorización
Execution Outline:
1. 1. Identificar el acceso a objetos
2. 2. Probar la autorización
3. 3. Acceso horizontal
4. 4. Operaciones de modificación/eliminación
## Ataque de inyección en API
- ID: api-injection
- Difficulty: intermediate
- Subcategory: Inyección en API
- Tags: api, injection, sqli, nosqli
- Original Extracted Source: original extracted web-security-wiki source/api-injection.md
Description:
Diversos tipos de ataques de inyección en endpoints de API
Prerequisites:
- La API acepta entrada del usuario
- La entrada no se filtra correctamente
Execution Outline:
1. 1. Inyección SQL
2. 2. Inyección NoSQL
3. 3. Inyección LDAP
4. 4. Inyección de comandos
</content>
