import os
from carga import CargadorDatos
from exportador_excel import ExportadorExcel
from exportador_pdf import ExportadorPDF
from genetico import AlgoritmoGenetico

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
