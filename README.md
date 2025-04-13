# Proyecto: Generador de Horarios con Algoritmos Genéticos

Este proyecto consiste en un sistema desarrollado en Python para generar horarios académicos optimizados, utilizando algoritmos genéticos como técnica de resolución. El sistema considera restricciones reales como disponibilidad de docentes, cantidad de salones y la distribución por semestres, generando propuestas automáticas de asignaciones que pueden ser evaluadas, editadas y exportadas por el usuario.

---

## 🎓 Objetivo del Proyecto
Demostrar la aplicación práctica de los algoritmos genéticos en la resolución de un problema complejo como la generación de horarios académicos, con una interfaz gráfica amigable y personalizable.

---

## 🤖 Tecnologías Utilizadas
- **Python 3.11** (recomendado Python 3.10 o superior)
- Interfaz gráfica con **Tkinter** y **tkhtmlview**
- Análisis de datos: **pandas**
- Exportación de reportes:
  - **openpyxl** (Excel)
  - **pdfkit** + **jinja2** (PDF)
- Visualización gráfica: **matplotlib**
- Análisis de rendimiento: **time**, **tracemalloc**

---

## 📊 Funcionamiento General
1. **Carga de datos**: desde archivos CSV ubicados en `/data`.
2. **Selección de cursos**: el usuario selecciona qué cursos incluir en el horario.
3. **Parámetros genéticos**: se define el número de generaciones y el tamaño poblacional.
4. **Ejecución del algoritmo genético**: se generan horarios que evolucionan con cada generación.
5. **Visualización**:
   - Horario generado y sus conflictos
   - Estadísticas de rendimiento y aptitud
   - Gráficas de evolución
6. **Edición manual y exportación**: el usuario puede realizar ajustes y exportar el resultado a PDF/Excel.

---

## 🔨 Requisitos Técnicos

### ✅ Versión mínima de Python
- Python 3.10+

### ⚡ Dependencias
Instalables con:
```bash
pip install -r requirements.txt
```
Dependencias:
- tkhtmlview
- pandas
- jinja2
- pdfkit *(requiere instalar wkhtmltopdf)*
- openpyxl
- matplotlib

### ▶️ Ejecución
```bash
python app.py
```

---

## 📂 Estructura del Proyecto
```
proyecto/
├── data/                        # Archivos de entrada CSV
│   ├── cursos.csv
│   ├── docente_curso.csv
│   ├── docentes.csv
│   └── salones.csv
├── app.py                      # Archivo principal (GUI)
├── clases.py                   # Entidades principales (Curso, Docente, etc.)
├── carga.py                    # Carga y validación de CSV
├── genetico.py                 # Lógica del algoritmo genético
├── exportador_excel.py         # Exporta a Excel
├── exportador_pdf.py           # Exporta a PDF
├── horario_generado.html       # Plantilla HTML intermedia
├── horario_generado.pdf        # Reporte generado (PDF)
├── horario_generado.xlsx       # Reporte generado (Excel)
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

---

## 📖 Manual Técnico y de Usuario
Puedes encontrar la documentación completa, explicaciones detalladas y capturas de interfaz en el **Manual Técnico** adjunto al proyecto.

Incluye:
- Introducción a algoritmos genéticos
- Metodología implementada: selección, cruce, mutación
- Arquitectura modular del sistema
- Ejemplo de datos y validaciones
- Manual de uso paso a paso

---

## 📑 Configuración de archivos CSV

Todos los archivos CSV deben estar ubicados en la carpeta `data/`.

### 1. cursos.csv

Contiene la información de los cursos disponibles.

| codigo | nombre        | carrera               | semestre | seccion | tipo        |
|--------|---------------|------------------------|----------|---------|-------------|
| INF101 | Algoritmos    | Ingeniería en Sistemas | 1        | A       | obligatorio |
| CIV102 | Topografía   | Ingeniería Civil      | 2        | B       | opcional    |

**Validaciones**:
- `semestre`: debe ser un número entre 1 y 10.
- `tipo`: debe ser `obligatorio` u `opcional` (no sensible a mayúsculas/minúsculas).
- No debe haber duplicados con misma combinación de `codigo` y `seccion`.

---

### 2. docentes.csv

Contiene la lista de docentes disponibles con su horario de disponibilidad.

| registro | nombre          | hora_entrada | hora_salida |
|----------|------------------|--------------|-------------|
| D001     | Ana López         | 13:40        | 19:30       |
| D002     | Carlos Martínez  | 14:30        | 20:20       |

**Validaciones**:
- Las horas deben tener el formato HH:MM (24h).
- El campo `registro` debe ser único.

---

### 3. docente_curso.csv

Define la relación entre docentes y los cursos que pueden impartir.

| registro | codigo_curso |
|------------------|--------------|
| D001             | INF101       |
| D002             | CIV102       |

**Validaciones**:
- Ambos campos deben coincidir con claves primarias en `docentes.csv` y `cursos.csv`.

---

### 4. salones.csv

Lista de salones disponibles para asignación.

| nombre   |
|----------|
| Salon 1  |
| Salon 2  |
| Salon 3  |

**Nota**: Los identificadores de salones son asignados automáticamente.

---

## Errores de carga

Si algún archivo contiene errores en su estructura o datos, se mostrará un cuadro de diálogo con todos los errores detectados al iniciar la aplicación.

---

## 🚀 Autor
**Carlos Benjamin Pac Flores**  
Carné: 201931012  
Ingeniería en Ciencias y Sistemas, CUNOC  
Fecha: Abril 2025

