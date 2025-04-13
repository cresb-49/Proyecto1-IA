from typing import List
import pandas as pd

from clases import Asignacion, Salon

class ExportadorExcel:
    @staticmethod
    def exportar_horario(asignaciones:List[Asignacion],salones:List[Salon], nombre_archivo="horario_generado.xlsx"):
        # Horarios posibles
        horarios = ["13:40", "14:30", "15:20", "16:10", "17:00", "17:50", "18:40", "19:30", "20:20"]
        salones = sorted({s.nombre for s in salones})

        # Crear DataFrame vacío
        tabla = pd.DataFrame(index=horarios, columns=salones)
        tabla = tabla.fillna("")

        for a in asignaciones:
            texto = f"{a.curso.nombre}\n{a.curso.codigo}\n{a.docente.nombre}\nSem {a.curso.semestre}\n{a.curso.carrera}"
            tabla.loc[a.horario, a.salon.nombre] = texto

        tabla.to_excel(nombre_archivo)
        print(f"Horario exportado exitosamente a '{nombre_archivo}'")
