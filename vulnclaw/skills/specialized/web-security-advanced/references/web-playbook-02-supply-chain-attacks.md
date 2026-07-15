# Ataques a la cadena de suministro
English: Supply Chain Attacks
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Suplantación de nombres de paquetes NPM (Typosquatting)
- ID: supply-typosquat
- Difficulty: intermediate
- Subcategory: Envenenamiento de gestores de paquetes
- Tags: cadena de suministro, NPM, Typosquatting, envenenamiento de paquetes, postinstall
- Original Extracted Source: original extracted web-security-wiki source/supply-typosquat.md
Description:
Registrar un paquete malicioso con un nombre muy similar a un paquete NPM popular (por ejemplo, lodash→1odash, colors→co1ors) para inducir al desarrollador a instalarlo por error. El paquete malicioso ejecuta una reverse shell, roba variables de entorno o instala una puerta trasera en los hooks install/postinstall.
Prerequisites:
- Cuenta NPM
- Conocimiento de las dependencias del proyecto objetivo
- Infraestructura para el paquete malicioso
Execution Outline:
1. 1. Reconocimiento de las dependencias objetivo
2. 2. Generación de nombres de paquete suplantados
3. 3. Construcción del paquete malicioso
4. 4. Detección y análisis forense
## Envenenamiento de pipelines de CI/CD
- ID: supply-ci-poison
- Difficulty: advanced
- Subcategory: Ataques a CI/CD
- Tags: cadena de suministro, CI/CD, GitHub Actions, Jenkins, Pipeline
- Original Extracted Source: original extracted web-security-wiki source/supply-ci-poison.md
Description:
Atacar el pipeline de CI/CD mediante pull requests maliciosos, inyección en Actions o manipulación de scripts de build. El atacante puede robar claves de compilación, envenenar los artefactos de build o insertar código de puerta trasera en el proceso de despliegue.
Prerequisites:
- El objetivo usa CI/CD público
- Es posible enviar un PR o hacer fork
Execution Outline:
1. 1. Identificar la configuración de CI/CD
2. 2. Inyección en workflows disparados por PR
3. 3. Inyección de expresiones en Actions
4. 4. Envenenamiento de artefactos de build
## Ataque de confusión de dependencias
- ID: supply-dependency-confusion
- Difficulty: intermediate
- Subcategory: Confusión de dependencias
- Tags: cadena de suministro, confusión de dependencias, NPM, PyPI, Dependency Confusion
- Original Extracted Source: original extracted web-security-wiki source/supply-dependency-confusion.md
Description:
Explotar la vulnerabilidad de prioridad de resolución de los gestores de paquetes entre el registro público y el privado. Cuando una empresa usa nombres de paquetes internos, el atacante registra un paquete con el mismo nombre y un número de versión más alto en el registro público NPM/PyPI; el gestor de paquetes priorizará la instalación del paquete público de versión más alta, ejecutando así código malicioso.
Prerequisites:
- Se conoce el nombre del paquete interno del objetivo
- Cuenta en el registro público
Execution Outline:
1. 1. Descubrir nombres de paquetes internos
2. 2. Registrar un paquete con el mismo nombre en el registro público
3. 3. Monitorear callbacks DNS para confirmar el impacto
4. 4. Evaluación de impacto y elaboración del informe
</content>
