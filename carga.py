from clases import Curso, Docente, Salon, Asignacion, RelacionDocenteCurso
from typing import List, Dict, Tuple
import csv


class CargadorDatos:
    def cargar_docentes(path: str) -> Tuple[List[Docente], List[str]]:
        docentes = []
        errores = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader: 
                # Validamos que vengan todos los campos y no estén vacíos
                if not all([row['registro'], row['nombre'], row['hora_entrada'], row['hora_salida']]):
                    errores.append(f"Faltan datos en el docente {row['registro']}, se omitirá la carga de este docente, linea {reader.line_num}.")
                    continue
                
                hora_entrada = None
                hora_salida = None
                try:    
                    #Si los datos de entrada y salida son en formato 12 horas, convertir a 24 horas
                    hora_entrada = row['hora_entrada'].split(':')
                    hora_salida = row['hora_salida'].split(':')
                    num_hora_entrada = int(hora_entrada[0])
                    num_hora_salida = int(hora_salida[0])
                    if (num_hora_entrada < 13):
                        num_hora_entrada += 12
                    if (num_hora_salida < 13):
                        num_hora_salida += 12

                    hora_entrada = f"{num_hora_entrada}:{hora_entrada[1]}"
                    hora_salida = f"{num_hora_salida}:{hora_salida[1]}"

                    if hora_entrada is None or hora_salida is None:
                        raise ValueError("Formato de hora inválido")
                except ValueError:
                    errores.append(f"Error en el formato de hora del docente {row['registro']}, se omitirá la carga de este docente, linea {reader.line_num}.")
                    continue

                docente = Docente(
                    registro=row['registro'],
                    nombre=row['nombre'],
                    hora_entrada=hora_entrada,
                    hora_salida=hora_salida
                )
                docentes.append(docente)
        return docentes, errores

    def cargar_cursos(path: str) -> Tuple[List[Curso], List[str]]:
        cursos = []
        cursos_vistos = set()
        errores = []
        # Se permite la carga de cursos con el mismo codigo pero cond diferente seccion

        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['codigo'], row['seccion'])
                if key in cursos_vistos:
                    errores.append(f"El curso {row['codigo']} con seccion {row['seccion']} ya fue cargado, se omitirá la carga de este curso, linea {reader.line_num}.")
                    continue
                cursos_vistos.add(key)

                # Validamos que vengan todos los campos y no estén vacíos
                if not all([row['codigo'], row['nombre'], row['carrera'], row['semestre'], row['seccion'], row['tipo']]):
                    errores.append(f"Faltan datos en el curso {row['codigo']}, se omitirá la carga de este curso, linea {reader.line_num}.")
                    continue

                # Validamos que el semestre sea un número entre 1 y 10
                try:
                    semestre = int(row['semestre'])
                    if semestre < 1 or semestre > 10:
                        errores.append(f"El semestre {row['semestre']} no es válido para el curso {row['codigo']}, se omitirá la carga de este curso, linea {reader.line_num}.")
                        continue
                except ValueError:
                    errores.append(f"El semestre {row['semestre']} no es un número válido para el curso {row['codigo']}, se omitirá la carga de este curso, linea {reader.line_num}.")
                    continue

                # Validamos que el tipo "opcional" o "obligatorio" no es case sensitive
                if row['tipo'].lower() not in ['opcional', 'obligatorio']:
                    errores.append(f"El tipo {row['tipo']} no es válido para el curso {row['codigo']}, se omitirá la carga de este curso, linea {reader.line_num}.")
                    continue

                curso = Curso(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    carrera=row['carrera'],
                    semestre=row['semestre'],
                    seccion=row['seccion'],
                    tipo=row['tipo']
                )
                cursos.append(curso)
        print(f"Se han cargado {len(cursos)} cursos.")
        return cursos, errores

    def cargar_relaciones(path: str) -> Tuple[RelacionDocenteCurso, List[str]]:
        relaciones = RelacionDocenteCurso()
        errores = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validamos que el registro y el codigo del curso no estén vacíos
                if not all([row['registro'], row['codigo_curso']]):
                    errores.append(f"Faltan datos en la relación docente-curso, se omitirá la carga de esta relación, linea {reader.line_num}.")
                    continue
                relaciones.agregar(row['registro'], row['codigo_curso'])
        return relaciones, errores

    def cargar_salones(path: str) -> Tuple[List[Salon], List[str]]:
        salones = []
        counter_id = 101
        errores = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validamos que el nombre del salón no esté vacío
                if not row['salon']:
                    errores.append(f"Faltan datos en el salón, se omitirá la carga de este salón, linea {reader.line_num}.")
                    continue
                salon = Salon(
                    id_salon=counter_id,
                    nombre=row['salon']
                )
                salones.append(salon)
                counter_id += 1
        return salones, errores
