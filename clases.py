class Curso:
    def __init__(self, codigo, nombre, carrera, semestre, seccion, tipo):
        self.codigo = codigo
        self.nombre = nombre
        self.carrera = carrera
        self.semestre = int(semestre)
        self.seccion = seccion
        self.tipo = tipo  # obligatorio / optativo

class Docente:
    def __init__(self, registro, nombre, hora_entrada, hora_salida):
        self.registro = registro
        self.nombre = nombre
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida

class Salon:
    def __init__(self, id_salon, nombre):
        self.id = id_salon
        self.nombre = nombre

class RelacionDocenteCurso:
    def __init__(self):
        self.relaciones = {}  # {registro: [codigos_curso]}

    def agregar(self, registro, codigo):
        self.relaciones.setdefault(registro, []).append(codigo)

    def docentes_para(self, codigo):
        return [r for r, cursos in self.relaciones.items() if codigo in cursos]

class Asignacion:
    def __init__(self, curso: Curso, docente: Docente, salon: Salon, horario: str):
        self.curso = curso
        self.docente = docente
        self.salon = salon
        self.horario = horario  # ej: '14:30'