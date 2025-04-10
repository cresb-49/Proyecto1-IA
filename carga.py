from clases import Curso, Docente, Salon, Asignacion, RelacionDocenteCurso
from typing import List, Dict, Tuple
import csv


class CargadorDatos:
    def cargar_docentes(path: str) -> List[Docente]:
        docentes = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader: 
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

                docente = Docente(
                    registro=row['registro'],
                    nombre=row['nombre'],
                    hora_entrada=hora_entrada,
                    hora_salida=hora_salida
                )
                docentes.append(docente)
        return docentes

    def cargar_cursos(path: str) -> List[Curso]:
        cursos = []
        cursos_vistos = set()
        # Se permite la carga de cursos con el mismo codigo pero cond diferente seccion

        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['codigo'], row['seccion'])
                if key in cursos_vistos:
                    print(f"El curso {row['codigo']} ya fue cargado, se omitirá la carga de este curso.")
                    continue
                cursos_vistos.add(key)
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
        return cursos

    def cargar_relaciones(path: str) -> RelacionDocenteCurso:
        relaciones = RelacionDocenteCurso()
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                relaciones.agregar(row['registro'], row['codigo_curso'])
        return relaciones

    def cargar_salones(path: str) -> List[Salon]:
        salones = []
        counter_id = 101
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                salon = Salon(
                    id_salon=counter_id,
                    nombre=row['salon']
                )
                salones.append(salon)
                counter_id += 1
        return salones
