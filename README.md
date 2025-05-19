# Analizador de Gramáticas LL(1) y SLR(1)
Student Information
--
Paulina Velásquez Londoño

Mariamny Del Valle Ramírez Telles

Class Number: 7309

System and Tools Used
--
Operating System: Any system supporting Python 3

Programming Language: Python 3.x

Development Environment: PyCharm, VS Code, or any Python-compatible IDE


Este proyecto implementa un analizador sintáctico para gramáticas LL(1) y SLR(1) en Python. El programa permite:
- Definir gramáticas libres de contexto
- Calcular conjuntos FIRST y FOLLOW
- Construir tablas de parsing para LL(1) y SLR(1)
- Analizar cadenas de entrada según la gramática proporcionada

## Características principales

- **Cálculo de FIRST y FOLLOW**: Implementación completa de los algoritmos para calcular estos conjuntos fundamentales
- **Análisis LL(1)**:
  - Construcción de tabla de parsing
  - Detección de conflictos LL(1)
  - Visualización de la tabla
- **Análisis SLR(1)**:
  - Construcción de la colección canónica de items LR(0)
  - Generación de tablas ACTION y GOTO
  - Detección de conflictos SLR(1)
- **Interfaz interactiva**: Menú para ingresar gramáticas y probar cadenas

## Requisitos

- Python 3.x
- No se requieren librerías externas

## Instrucciones de uso

1. Ejecutar el programa: `python analizador.py`
2. Seguir las instrucciones para ingresar la gramática:
   - Especificar número de producciones
   - Ingresar cada producción en formato `S -> A B | C` (usar 'e' para épsilon)
3. El programa analizará la gramática y mostrará:
   - Los conjuntos FIRST y FOLLOW
   - Si la gramática es LL(1) y/o SLR(1)
4. Seleccionar opción para usar el parser LL(1) o SLR(1) (si aplica)
5. Ingresar cadenas para analizar sintácticamente

## Ejemplo de gramática válida

```
S -> A B C
A -> a A | e
B -> b B | e
C -> c
```

## Limitaciones

- Los símbolos terminales deben ser caracteres individuales
- La gramática debe estar en forma adecuada para los parsers (sin recursión izquierda para LL(1), etc.)
- La interfaz es por consola con capacidades básicas



