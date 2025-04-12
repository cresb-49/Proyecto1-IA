from clases import Curso, Docente, Salon, Asignacion, RelacionDocenteCurso
from typing import List, Dict, Tuple
import random
import copy


class Horario:
    def __init__(self, asignaciones: List[Asignacion]):
        self.asignaciones = asignaciones
        self.aptitud = 0
        self.cantidad_conflictos = 0
        self.cantidad_bonus = 0

    def calcular_aptitud(self):
        conflictos = self.contar_conflictos()
        bonus = self.contar_bonus()
        self.cantidad_conflictos = conflictos
        self.cantidad_bonus = bonus
        self.aptitud = len(self.asignaciones) + (bonus*0.25) - (conflictos*1.5)
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

            # Conflicto de docente duplicado en horario
            if key_d in horarios_docente:
                conflictos += 1
            else:
                horarios_docente[key_d] = True

            # Conflico de salon duplicado en horario
            if key_s in horarios_salon:
                conflictos += 1
            else:
                horarios_salon[key_s] = True

            # Conflictos por cursos obligatorios traslapados
            if asignacion.curso.tipo == "obligatorio":
                if key_c in cursos_semestre:
                    conflictos += 1.5
                else:
                    cursos_semestre[key_c] = True

        return conflictos

    def contar_bonus(self):
        bonus = 0
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

    def copy(self):
        return copy.deepcopy(self)

class AlgoritmoGenetico:
    def __init__(self, cursos, docentes, salones, relaciones, generaciones=100, poblacion_inicial=50):
        self.cursos = cursos
        self.keys_cursos = set()
        for curso in cursos:
            key = (curso.codigo, curso.seccion)
            self.keys_cursos.add(key)
        print(f"Hay cargados {len(self.cursos)} cursos")
        print(f"Se han creado {len(self.keys_cursos)} keys de cursos")
        self.docentes = docentes
        self.salones = salones
        self.relaciones = relaciones
        self.generaciones = generaciones
        self.poblacion: List[Horario] = []
        self.mejores_generaciones: List[Horario] = []
        self.aptitudes_mejores_generaciones: List[float] = []
        self.historial_completo: List[Horario] = []
        self.historial_aptitudes: List[float] = []
        self.historial_aptitudes_generaciones: Dict[int, List[float]] = {}
        self.mejor = None
        self.tamano_poblacion = poblacion_inicial
        # Variables de resultado de rendimiento del algoritmo
        self.tiempo_total = 0
        self.cantidad_promedio_conflictos = 0
        self.cantidad_promedio_bonus = 0
        self.cantidad_promedio_aptitud = 0
        self.contador_promedios = 0
        self.uso_ram = 0
        self.pico_ram = 0

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
            # print(f"Se han generado {len(asignaciones)} asignaciones")
            self.poblacion.append(Horario(asignaciones))

    def convertir_a_minutos(self, hora: str) -> int:
        h, m = map(int, hora.split(":"))
        return h * 60 + m

    def generar_horarios_validos(self, docente: Docente) -> list:
        inicio = self.convertir_a_minutos(docente.hora_entrada)
        fin = self.convertir_a_minutos(docente.hora_salida)

        todos_los_slots = ["13:40", "14:30", "15:20", "16:10",
                           "17:00", "17:50", "18:40", "19:30", "20:20"]
        slots_validos = []

        for slot in todos_los_slots:
            slot_min = self.convertir_a_minutos(slot)
            if ((inicio <= slot_min) and ((slot_min + 50) <= fin)):
                slots_validos.append(slot)

        return slots_validos

    def evolucionar(self):
        # calculamos aptitud de la poblacion inicial
        # Ordenamos del mas cer
        for gen in range(self.generaciones):
            # Generamos la clave para el historial de aptitudes
            self.historial_aptitudes_generaciones[f"{gen}"] = []
            for horario in self.poblacion:
                horario.calcular_aptitud()
                # Guardamos el horario en el historial completo para graficar
                # la funcion de aptitud
                self.historial_completo.append(horario)
                self.historial_aptitudes.append(horario.aptitud)
                self.historial_aptitudes_generaciones[f"{gen}"].append(horario.aptitud)
                # Calculos para el reporte de estadisticas
                self.cantidad_promedio_aptitud += horario.aptitud
                self.cantidad_promedio_conflictos += horario.cantidad_conflictos
                self.cantidad_promedio_bonus += horario.cantidad_bonus
                self.contador_promedios += 1
                self.cantidad_promedio_aptitud = self.cantidad_promedio_aptitud / self.contador_promedios
                self.cantidad_promedio_conflictos = self.cantidad_promedio_conflictos / self.contador_promedios
                self.cantidad_promedio_bonus = self.cantidad_promedio_bonus / self.contador_promedios

            self.poblacion.sort(key=lambda h: h.aptitud, reverse=True)
            self.mejor = self.poblacion[0]
            self.mejores_generaciones.append(self.mejor.copy())
            self.aptitudes_mejores_generaciones.append(self.mejor.aptitud)
            print(f"Gen {gen+1}, mejor aptitud: {self.mejor.aptitud}")
            # print(f"Gen {gen+1}, mejor horario: {len(self.mejor.asignaciones)}")
            self.seleccionar_cruzar_mutar()
            
        # De los mejores horarios, seleccionamos el mejor es el que tiene
        # la mejor aptitud de todas las generaciones
        self.mejores_generaciones.sort(key=lambda h: h.aptitud, reverse=True)

        # Tomamos el mejor horario de todas las generaciones
        # A esta eleccion de solucion "optima" se le llama elitismo intergeneracional
        # Ya que tenemos un registro de los mejores horarios de cada generacion
        # y tomamos el mejor de todos en este caso es el que mostrara menos conflictos
        # debido a la funcion de aptitud planteada de conflictos y bonus
        # aptitud = bonus - conflictos
        self.mejor = self.mejores_generaciones[0]

    def cursos_conflicto(self,asignaciones):
        codigos_cursos = []
        # De las asignaciones hay que tomar todas aquellas que tengas algun tipo de conflicto
        map_horario_salon = {}
        map_horario_docente = {}
        map_salon_docente = {}

        self.calcular_mapas(map_horario_salon,map_horario_docente,map_salon_docente,asignaciones)
        for asignacion in asignaciones:
            key_hs = (asignacion.horario, asignacion.salon.nombre)
            key_hd = (asignacion.horario, asignacion.docente.registro)
            key_sd = (asignacion.salon.nombre, asignacion.docente.registro)

            es_conflicto1 = len(map_horario_salon[key_hs]) > 1
            es_conflicto2 = len(map_horario_docente[key_hd]) > 1
            es_conflicto3 = len(map_salon_docente[key_sd]) > 1

            if es_conflicto1 or es_conflicto2 or es_conflicto3:
                codigos_cursos.append(asignacion.curso.codigo)
        
        return codigos_cursos
    
    def eliminar_conflictos(self,codigos_cursos,asignaciones):
        """
        Elimina los conflictos de las asignaciones
        :param codigos_cursos: lista de codigos de cursos con conflictos
        :param asignaciones: lista de asignaciones
        :return: lista de asignaciones sin conflictos
        """
        for asignacion in asignaciones:
            if asignacion.curso.codigo in codigos_cursos:
                # Si el curso tiene conflicto, lo eliminamos
                asignaciones.remove(asignacion)
        return asignaciones
    
    def cruzarFaltante(self,padre1:Horario,padre2:Horario) -> Horario:
        """
        Cruza dos horarios, el hijo es una mezcla de los dos padres
        El resultado es un nuevo horario en este caso se tratan de eliminar conflictos
        mediante el cruce CrossOver el cual se trata en completar los faltantes
        :param padre1: Horario padre 1
        :param padre2: Horario padre 2
        :return: Horario hijo
        """
        # Rrealizamos una copia de padre1 para que sea base del hijo a generar
        hijo = padre1.asignaciones.copy()    
        # Recorremos los codigos de los cursos que tienen conflictos
        codigos_cursos = self.cursos_conflicto(hijo)
        hijo = self.eliminar_conflictos(codigos_cursos,hijo)
        # Recorremos los codigos de los cursos que tienen conflictos
        # Y buscamos en padre2 esos cursos para completar la asignacion
        for asignacion in padre2.asignaciones:
            if asignacion.curso.codigo in codigos_cursos:
                # Realizamos un copia de la asignacion y la agregamos al hijo
                asignacion_copia = Asignacion(asignacion.curso,asignacion.docente,asignacion.salon,asignacion.horario)
                hijo.append(asignacion_copia)
        #Retornamos el hijo con las asignaciones completas
        return Horario(hijo)
            

    def calcular_mapas(self,map_horario_salon,map_horario_docente,map_salon_docente,asignaciones):
        """
        Calcula los mapas de horarios, salones y docentes
        :param asignaciones: lista de asignaciones
        :return: None
        """
        for asignacion in asignaciones:
            key_hs = (asignacion.horario, asignacion.salon.nombre)
            key_hd = (asignacion.horario, asignacion.docente.registro)
            key_sd = (asignacion.salon.nombre, asignacion.docente.registro)
            if key_hs not in map_horario_salon:
                map_horario_salon[key_hs] = []
            map_horario_salon[key_hs].append(asignacion)

            if key_hd not in map_horario_docente:
                map_horario_docente[key_hd] = []
            map_horario_docente[key_hd].append(asignacion)

            if key_sd not in map_salon_docente:
                map_salon_docente[key_sd] = []
            map_salon_docente[key_sd].append(asignacion)

    def cruzarRandom(self, padre1: Horario, padre2: Horario) -> Horario:
        """
        Cruza dos horarios aleatoriamente, el hijo es una mezcla de los dos padres
        El resultado es un nuevo horario pero las asignaciones de cursos se pueden repetir
        Por lo que es muy probable que el hijo tenga conflictos mas dificil de resolver
        :param padre1: Horario padre 1
        :param padre2: Horario padre 2
        :return: Horario hijo
        """
        punto_corte = random.randint(1, len(padre1.asignaciones) - 1)
        hijo_asigs = padre1.asignaciones[:punto_corte] + \
            padre2.asignaciones[punto_corte:]
        return Horario(hijo_asigs)
    
    def cruzarConDosPuntos(self, padre1: Horario, padre2: Horario) -> Horario:
        """
        Cruce con dos puntos de corte que preserva unicidad de cursos.
        Se copia un segmento intermedio del padre1 y se completa desde el padre2.
        """
        total = len(padre1.asignaciones)
        p1, p2 = sorted(random.sample(range(total), 2))  # dos puntos distintos

        hijo_asigs = []
        cursos_usados = set()
        #copiamos el set original de keys de cursos y le quitamos los que ya tenemos
        copias_keys = set(self.keys_cursos)

        # Copiar segmento medio del padre1
        for i in range(p1, p2 + 1):
            asignacion = padre1.asignaciones[i]
            hijo_asigs.append(asignacion)
            # Un curso repetido es el codigo del curso y la seccion
            key = (asignacion.curso.codigo, asignacion.curso.seccion)
            if key in cursos_usados:
                continue
            cursos_usados.add(key)

        # Obtenemos las keys faltantes
        mising_keys = copias_keys - cursos_usados


        # buscamos en base a las keys faltantes
        for key in mising_keys:
            # Buscamos en padre1
            for asignacion in padre2.asignaciones:
                if (asignacion.curso.codigo, asignacion.curso.seccion) == key:
                    hijo_asigs.append(asignacion)
                    cursos_usados.add(key)
                    break
        
        mising_keys = copias_keys - cursos_usados

        # # Completar desde padre2 evitando duplicados
        # for asignacion in padre2.asignaciones:
        #     key = (asignacion.curso.codigo, asignacion.curso.seccion)
        #     if key in cursos_usados:
        #         continue
        #     hijo_asigs.append(asignacion)
        #     cursos_usados.add(asignacion.curso.codigo)

        return Horario(hijo_asigs)

    def seleccionar_cruzar_mutar(self):
        # Aplicamos elitismo, mantenemos los mejores el 20% de la poblacion
        # y cruzamos el resto
        cantidad_elitismo = int(self.tamano_poblacion * 0.2)
        nueva_poblacion = self.poblacion[:cantidad_elitismo]

        while len(nueva_poblacion) < self.tamano_poblacion:
            # seleccionamos 2 padres aleatorios de la poblacion
            # Se toma el 60% de la poblacion ordenada
            # del mejor al peor
            cantidad_padres = int(self.tamano_poblacion * 0.6)
            padres = random.sample(self.poblacion[:cantidad_padres], 2)
            hijo = self.cruzarConDosPuntos(padres[0], padres[1])
            self.mutar(hijo)
            nueva_poblacion.append(hijo)

        self.poblacion = nueva_poblacion

    def mutar(self, individuo: Horario, tasa=0.1):

        # Aplicamos una mutacion del 90%
        if random.random() > tasa:
            return
        # Seleccionamos una asignacion aleatoria y cambiamos su horario
        # Por uno que sea valido para el docente, no verificamos si
        # hay conflictos en general
        asignacion = random.choice(individuo.asignaciones)
        docente = asignacion.docente
        horarios_validos = self.generar_horarios_validos(docente)
        if horarios_validos:
            asignacion.horario = random.choice(horarios_validos)
