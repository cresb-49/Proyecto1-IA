import tkinter as tk
from tkhtmlview import HTMLLabel
from tkinter import Toplevel, ttk, messagebox
from clases import Curso
from carga import CargadorDatos
import os

from exportador_excel import ExportadorExcel
from exportador_pdf import ExportadorPDF
from genetico import AlgoritmoGenetico


class AppHorario:
    def __init__(self, root):
        self.root = root
        self.root.title("Seleccionar Cursos")
        self.root.geometry("1000x600")

        self.cursos = CargadorDatos.cargar_cursos("data/cursos.csv")
        self.check_vars = []

        self.build_ui()

    def build_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        btn_pares = tk.Button(
            frame_top, text="Seleccionar pares", command=self.seleccionar_pares)
        btn_impares = tk.Button(
            frame_top, text="Seleccionar impares", command=self.seleccionar_impares)
        btn_todos = tk.Button(frame_top, text="Seleccionar todos",
                              command=lambda: self.seleccionar_todos(True))
        btn_nada = tk.Button(frame_top, text="Quitar selección",
                             command=lambda: self.seleccionar_todos(False))
        btn_generar = tk.Button(
            frame_top, text="Generar Horario", command=self.generar_horario)

        btn_pares.pack(side=tk.LEFT, padx=5)
        btn_impares.pack(side=tk.LEFT, padx=5)
        btn_todos.pack(side=tk.LEFT, padx=5)
        btn_nada.pack(side=tk.LEFT, padx=5)
        btn_generar.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.root)
        self.scroll_y = ttk.Scrollbar(
            self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # Expandir columnas automáticamente
        for col in range(7):
            self.scroll_frame.grid_columnconfigure(col, weight=1)

        # Tabla de cursos
        encabezados = ["", "Código", "Nombre",
                       "Carrera", "Semestre", "Sección", "Tipo"]
        for col, texto in enumerate(encabezados):
            lbl = tk.Label(self.scroll_frame, text=texto, font=(
                "Arial", 10, "bold"), borderwidth=1, relief="solid", padx=4)
            lbl.grid(row=0, column=col, sticky="nsew")

        for i, curso in enumerate(self.cursos):
            var = tk.BooleanVar()
            self.check_vars.append((var, curso))
            tk.Checkbutton(self.scroll_frame, variable=var).grid(
                row=i+1, column=0, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.codigo).grid(
                row=i+1, column=1, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.nombre).grid(
                row=i+1, column=2, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.carrera).grid(
                row=i+1, column=3, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.semestre).grid(
                row=i+1, column=4, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.seccion).grid(
                row=i+1, column=5, sticky="nsew")
            tk.Label(self.scroll_frame, text=curso.tipo).grid(
                row=i+1, column=6, sticky="nsew")

    def seleccionar_todos(self, estado):
        for var, _ in self.check_vars:
            var.set(estado)

    def seleccionar_pares(self):
        for var, curso in self.check_vars:
            var.set(curso.semestre % 2 == 0)

    def seleccionar_impares(self):
        for var, curso in self.check_vars:
            var.set(curso.semestre % 2 != 0)

    def generar_horario(self):
        seleccionados = [curso for var, curso in self.check_vars if var.get()]
        if not seleccionados:
            messagebox.showwarning(
                "Aviso", "Selecciona al menos un curso para continuar.")
            return

        # Aquí puedes invocar el algoritmo genético con seleccionados
        self.ejecutar_algoritmo_genetico(seleccionados)
        messagebox.showinfo(
            "Éxito", "Horario generado y exportado exitosamente.")
        self.mostrar_html_desde_archivo()

    def ejecutar_algoritmo_genetico(self, cursos_seleccionados):
        # Carga de archivos CSV
        base_path = "data"
        path_docentes = os.path.join(base_path, "docentes.csv")
        path_relaciones = os.path.join(base_path, "docente_curso.csv")
        path_salones = os.path.join(base_path, "salones.csv")

        docentes = CargadorDatos.cargar_docentes(path_docentes)
        relaciones = CargadorDatos.cargar_relaciones(path_relaciones)
        salones = CargadorDatos.cargar_salones(path_salones)

        ag = AlgoritmoGenetico(
            cursos=cursos_seleccionados,
            docentes=docentes,
            salones=salones,
            relaciones=relaciones,
            generaciones=50,
            poblacion_inicial=100
        )

        ag.generar_poblacion_inicial()
        ag.evolucionar()

        # Exportar el horario generado
        ExportadorExcel.exportar_horario(ag.mejor.asignaciones)
        ExportadorPDF.exportar_horario(ag.mejor.asignaciones)
        print("Asignaciones generadas:")
        for asignacion in ag.mejor.asignaciones:
            print(asignacion)
        return ag.mejor.asignaciones

    def mostrar_html_desde_archivo(self,ruta="horario_generado.html"):
        ventana = Toplevel()
        ventana.title("Vista HTML del Horario")
        ventana.geometry("800x600")

        with open(ruta, encoding="utf-8") as f:
            contenido = f.read()

        label = HTMLLabel(ventana, html=contenido)
        label.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppHorario(root)
    root.mainloop()
