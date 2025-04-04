from typing import List, Dict, Tuple
import random
import csv
from clases import Curso, Docente, Salon, Asignacion, RelacionDocenteCurso


class CargadorDatos:
    def cargar_docentes(path: str) -> List[Docente]:
        docentes = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                docente = Docente(
                    registro=row['registro'],
                    nombre=row['nombre'],
                    hora_entrada=row['hora_entrada'],
                    hora_salida=row['hora_salida']
                )
                docentes.append(docente)
        return docentes

    def cargar_cursos(path: str) -> List[Curso]:
        cursos = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                curso = Curso(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    carrera=row['carrera'],
                    semestre=row['semestre'],
                    seccion=row['seccion'],
                    tipo=row['tipo']
                )
                cursos.append(curso)
        return cursos
    
    def cargar_relaciones(path: str) -> RelacionDocenteCurso:
        relaciones = RelacionDocenteCurso()
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                relaciones.agregar(row['registro'], row['codigo_curso'])
        return relaciones
    
    def cargar_salones():
        return [Salon("101", "Salon 1"),
                Salon("102", "Salon 2"),
                Salon("103", "Salon 3"),
                Salon("104", "Salon 4"),
                Salon("105", "Salon 5"),
                Salon("106", "Salon 6"),
                Salon("107", "Salon 7"),
                Salon("108", "Salon 8"),
                Salon("109", "Salon 9"),
                Salon("110", "Salon 10"),
                Salon("111", "Salon 11")
                ]




class Horario:
    def __init__(self, asignaciones: List[Asignacion]):
        self.asignaciones = asignaciones
        self.aptitud = 0

    def calcular_aptitud(self):
        conflictos = self.contar_conflictos()
        bonus = self.contar_bonus()
        self.aptitud = bonus - (10 * conflictos)  # peso 10 por conflicto
        return self.aptitud

    def contar_conflictos(self):
        conflictos = 0
        horarios_docente = {}
        horarios_salon = {}
        cursos_semestre = {}

        for asignacion in self.asignaciones:
            key_d = (asignacion.docente.registro, asignacion.horario)
            key_s = (asignacion.salon.id, asignacion.horario)
            key_c = (asignacion.curso.carrera,
                     asignacion.curso.semestre, asignacion.horario)

            if key_d in horarios_docente:
                conflictos += 1  # docente duplicado
            else:
                horarios_docente[key_d] = True

            if key_s in horarios_salon:
                conflictos += 1  # salón duplicado
            else:
                horarios_salon[key_s] = True

            if asignacion.curso.tipo == "obligatorio":
                if key_c in cursos_semestre:
                    conflictos += 1  # cursos obligatorios del mismo semestre traslapados
                else:
                    cursos_semestre[key_c] = True

        return conflictos

    def contar_bonus(self):
        bonus = 0
        # BONUS: cursos consecutivos del mismo semestre
        # Agrupar por carrera+semestre y ordenar horarios
        grupos = {}
        for asignacion in self.asignaciones:
            key = (asignacion.curso.carrera, asignacion.curso.semestre)
            grupos.setdefault(key, []).append(asignacion.horario)

        for horarios in grupos.values():
            horarios_int = sorted([self.hora_a_min(h) for h in horarios])
            consecutivos = sum(1 for i in range(1, len(horarios_int))
                               if horarios_int[i] - horarios_int[i-1] == 50)
            bonus += consecutivos

        return bonus

    def hora_a_min(self, hora):
        h, m = map(int, hora.split(":"))
        return h * 60 + m


class AlgoritmoGenetico:
    def __init__(self, cursos, docentes, salones, relaciones, generaciones=100, poblacion_inicial=50):
        self.cursos = cursos
        self.docentes = docentes
        self.salones = salones
        self.relaciones = relaciones
        self.generaciones = generaciones
        self.poblacion = []
        self.mejor = None
        self.tamano_poblacion = poblacion_inicial

    def generar_poblacion_inicial(self):
        for _ in range(self.tamano_poblacion):
            asignaciones = []
            for curso in self.cursos:
                posibles_docentes = self.relaciones.docentes_para(curso.codigo)
                if not posibles_docentes:
                    continue
                docente = random.choice(
                    [d for d in self.docentes if d.registro in posibles_docentes])
                salon = random.choice(self.salones)
                horario = self.generar_horario_aleatorio()
                asignaciones.append(Asignacion(curso, docente, salon, horario))
            self.poblacion.append(Horario(asignaciones))

    def generar_horario_aleatorio(self):
        # Horarios entre 13:40 y 21:10
        horarios = ["13:40", "14:30", "15:20", "16:10",
                    "17:00", "17:50", "18:40", "19:30", "20:20"]
        return random.choice(horarios)

    def evolucionar(self):
        for gen in range(self.generaciones):
            for horario in self.poblacion:
                horario.calcular_aptitud()
            self.poblacion.sort(key=lambda h: h.aptitud, reverse=True)
            self.mejor = self.poblacion[0]
            self.seleccionar_cruzar_mutar()
            print(f"Gen {gen+1}, mejor aptitud: {self.mejor.aptitud}")

    def cruzar(self, padre1: Horario, padre2: Horario) -> Horario:
        punto_corte = random.randint(1, len(padre1.asignaciones) - 1)
        hijo_asigs = padre1.asignaciones[:punto_corte] + \
            padre2.asignaciones[punto_corte:]
        return Horario(hijo_asigs)

    def seleccionar_cruzar_mutar(self):
        # elitismo: mantener los 10 mejores
        nueva_poblacion = self.poblacion[:10]

        while len(nueva_poblacion) < self.tamano_poblacion:
            # torneo entre top 30
            padres = random.sample(self.poblacion[:30], 2)
            hijo = self.cruzar(padres[0], padres[1])
            self.mutar(hijo)
            nueva_poblacion.append(hijo)

        self.poblacion = nueva_poblacion

    def mutar(self, individuo: Horario, tasa=0.1):
        if random.random() > tasa:
            return
        asignacion = random.choice(individuo.asignaciones)
        # mutar horario o salón o docente
        asignacion.horario = self.generar_horario_aleatorio()
