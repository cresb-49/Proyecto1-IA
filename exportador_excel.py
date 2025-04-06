import pandas as pd

class ExportadorExcel:
    @staticmethod
    def exportar_horario(asignaciones, nombre_archivo="horario_generado.xlsx"):
        # Horarios posibles
        horarios = ["13:40", "14:30", "15:20", "16:10", "17:00", "17:50", "18:40", "19:30", "20:20"]
        salones = list({a.salon.nombre for a in asignaciones})

        # Crear DataFrame vacío
        tabla = pd.DataFrame(index=horarios, columns=salones)
        tabla = tabla.fillna("")

        for a in asignaciones:
            texto = f"{a.curso.nombre}\n{a.curso.codigo}\n{a.docente.nombre}\nSem {a.curso.semestre}\n{a.curso.carrera}"
            tabla.loc[a.horario, a.salon.nombre] = texto

        tabla.to_excel(nombre_archivo)
        print(f"Horario exportado exitosamente a '{nombre_archivo}'")
