from typing import List, Dict, Tuple
import random
import os
from clases import Curso, Docente, Salon, Asignacion, RelacionDocenteCurso
from carga import CargadorDatos
from exportador_excel import ExportadorExcel
from exportador_pdf import ExportadorPDF


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
                horarios_validos = self.generar_horarios_validos(docente)
                if not horarios_validos:
                    continue
                horario = random.choice(horarios_validos)
                asignaciones.append(Asignacion(curso, docente, salon, horario))
            self.poblacion.append(Horario(asignaciones))

    def convertir_a_minutos(self, hora: str) -> int:
        h, m = map(int, hora.split(":"))
        return h * 60 + m

    def generar_horarios_validos(self, docente: Docente) -> list:
        inicio = self.convertir_a_minutos(docente.hora_entrada)
        fin = self.convertir_a_minutos(docente.hora_salida)

        # Slots posibles en el sistema
        todos_los_slots = ["13:40", "14:30", "15:20", "16:10",
                           "17:00", "17:50", "18:40", "19:30", "20:20"]
        slots_validos = []

        for slot in todos_los_slots:
            slot_min = self.convertir_a_minutos(slot)
            if ((inicio <= slot_min) and ((slot_min + 50) <= fin)):
                slots_validos.append(slot)

        return slots_validos

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
        docente = asignacion.docente
        horarios_validos = self.generar_horarios_validos(docente)
        if horarios_validos:
            asignacion.horario = random.choice(horarios_validos)


def main():
    # Carga de archivos CSV
    base_path = "data"
    path_docentes = os.path.join(base_path, "docentes.csv")
    path_cursos = os.path.join(base_path, "cursos.csv")
    path_relaciones = os.path.join(base_path, "docente_curso.csv")
    path_salones = os.path.join(base_path, "salones.csv")

    docentes = CargadorDatos.cargar_docentes(path_docentes)
    cursos = CargadorDatos.cargar_cursos(path_cursos)
    relaciones = CargadorDatos.cargar_relaciones(path_relaciones)
    salones = CargadorDatos.cargar_salones(path_salones)

    # Preguntamos al usuario si quiere los de semestre pare o impar
    while True:
        semestre = input(
            "¿Quieres los cursos de semestre par o impar? (p/i): ").strip().lower()
        if semestre in ['p', 'i']:
            break
        else:
            print("Opción inválida. Por favor, elige 'p' para par o 'i' para impar.")

    cursos_filtrados = []
    for curso in cursos:
        if semestre == 'p' and curso.semestre % 2 == 0:
            cursos_filtrados.append(curso)
        elif semestre == 'i' and curso.semestre % 2 != 0:
            cursos_filtrados.append(curso)

    # --- Iniciar algoritmo genético ---
    ag = AlgoritmoGenetico(
        cursos=cursos_filtrados,
        docentes=docentes,
        salones=salones,
        relaciones=relaciones,
        generaciones=50,
        poblacion_inicial=100
    )

    ag.generar_poblacion_inicial()
    ag.evolucionar()

    print("\n--- Mejor horario encontrado ---")
    ExportadorExcel.exportar_horario(ag.mejor.asignaciones)
    ExportadorPDF.exportar_horario(ag.mejor.asignaciones)
    print(f"Aptitud final: {ag.mejor.aptitud}")


if __name__ == "__main__":
    main()
