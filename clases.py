class Curso:
    def __init__(self, codigo, nombre, carrera, semestre, seccion, tipo):
        self.codigo = codigo
        self.nombre = nombre
        self.carrera = carrera
        self.semestre = int(semestre)
        self.seccion = seccion
        self.tipo = tipo  # obligatorio / optativo
        
    def __repr__(self):
        return f"Curso(codigo={self.codigo}, nombre={self.nombre}, carrera={self.carrera}, semestre={self.semestre}, seccion={self.seccion}, tipo={self.tipo})\n"

class Docente:
    def __init__(self, registro, nombre, hora_entrada, hora_salida):
        self.registro = registro
        self.nombre = nombre
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
    
    def __repr__(self):
        return f"Docente(registro={self.registro}, nombre={self.nombre}, hora_entrada={self.hora_entrada}, hora_salida={self.hora_salida})\n"

class Salon:
    def __init__(self, id_salon, nombre):
        self.id = id_salon
        self.nombre = nombre

    def __repr__(self):
        return f"Salon(id={self.id}, nombre={self.nombre})\n"
class RelacionDocenteCurso:
    def __init__(self):
        self.relaciones = {}  # {registro: [codigos_curso]}

    def agregar(self, registro, codigo):
        self.relaciones.setdefault(registro, []).append(codigo)

    def docentes_para(self, codigo):
        return [r for r, cursos in self.relaciones.items() if codigo in cursos]
    
    def __repr__(self):
        return f"RelacionDocenteCurso(relaciones={self.relaciones})\n"

class Asignacion:
    def __init__(self, curso: Curso, docente: Docente, salon: Salon, horario: str):
        self.curso = curso
        self.docente = docente
        self.salon = salon
        self.horario = horario  # ej: '14:30'
        
    def __repr__(self):
        return f"Asignacion(curso={self.curso}, docente={self.docente}, salon={self.salon}, horario={self.horario})\n"