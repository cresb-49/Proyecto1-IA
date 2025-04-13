import time
import tracemalloc
import tkinter as tk
from tkhtmlview import HTMLLabel
from tkinter import Toplevel, ttk, messagebox
from clases import Curso
from carga import CargadorDatos
import os
from clases import Asignacion,RelacionDocenteCurso, Docente, Salon
from typing import List

from exportador_excel import ExportadorExcel
from exportador_pdf import ExportadorPDF
from genetico import AlgoritmoGenetico


class AppHorario:
    def __init__(self, root):
        self.root = root
        self.root.title("Seleccionar Cursos")
        self.root.geometry("1000x600")

        self.cursos: List[Curso] = []
        self.errores: List[str] = []
        self.relaciones:RelacionDocenteCurso = None
        self.docentes: List[Docente] = []
        self.salones: List[Salon] = []
        self.check_vars = []
        self.cargar_info()
        self.build_ui()

    def cargar_info(self):
        base_path = "data"
        path_cursos = os.path.join(base_path, "cursos.csv")
        path_docentes = os.path.join(base_path, "docentes.csv")
        path_relaciones = os.path.join(base_path, "docente_curso.csv")
        path_salones = os.path.join(base_path, "salones.csv")

        self.cursos, errores0 = CargadorDatos.cargar_cursos(path_cursos)
        self.docentes,errores1 = CargadorDatos.cargar_docentes(path_docentes)
        self.relaciones,errores2 = CargadorDatos.cargar_relaciones(path_relaciones)
        self.salones,errores3 = CargadorDatos.cargar_salones(path_salones)

        self.errores = errores0 + errores1 + errores2 + errores3

    def build_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        btn_pares = tk.Button(
            frame_top, text="Semestre Par", command=self.seleccionar_pares)
        btn_impares = tk.Button(
            frame_top, text="Semestre Impar", command=self.seleccionar_impares)
        btn_nada = tk.Button(frame_top, text="Quitar selección",
                             command=lambda: self.seleccionar_todos(False))
        btn_generar = tk.Button(
            frame_top, text="Generar Horario", command=self.generar_horario)
        
        btn_mostrar_errores = tk.Button(
            frame_top, text="Mostrar Errores", command=self.mostrar_errores_carga)

        btn_pares.pack(side=tk.LEFT, padx=5)
        btn_impares.pack(side=tk.LEFT, padx=5)
        btn_nada.pack(side=tk.LEFT, padx=5)
        btn_generar.pack(side=tk.LEFT, padx=5)
        btn_mostrar_errores.pack(side=tk.LEFT, padx=5)

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
        self.mostrar_errores_carga()
    
    def hora_a_min(self,hora):
        h, m = map(int, hora.split(":"))
        return h * 60 + m

    def mostrar_errores_carga(self):
        # Mostrar errores
        # Si hay algun error, se muestra en un popup con scrollbar
        if len(self.errores) > 0:
            popup = Toplevel(self.root)
            popup.title("Errores")
            popup.geometry("400x300")

            scrollbar = ttk.Scrollbar(popup)
            scrollbar.pack(side="right", fill="y")

            text_area = tk.Text(popup, wrap="word", yscrollcommand=scrollbar.set)
            text_area.pack(expand=True, fill="both")
            scrollbar.config(command=text_area.yview)

            for error in self.errores:
                text_area.insert(tk.END, error + "\n")
        else:
            popup = Toplevel(self.root)
            popup.title("Carga exitosa")
            popup.geometry("300x100")
            messagebox.showinfo("Carga exitosa", "No se encontraron errores en la carga de datos.")

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
            messagebox.showwarning("Aviso", "Selecciona al menos un curso para continuar.")
            return

        def continuar():
            try:
                generaciones = int(entry_generaciones.get())
                poblacion = int(entry_poblacion.get())
                top.destroy()
                print(f"Se han seleccionado {len(seleccionados)} cursos.")
                self.ejecutar_algoritmo_genetico(seleccionados, generaciones, poblacion)
            except ValueError:
                messagebox.showerror("Error", "Los valores deben ser números enteros.")

        top = Toplevel(self.root)
        top.title("Parámetros del Algoritmo Genético")
        top.geometry("300x200")
        top.resizable(False, False)

        tk.Label(top, text="Cantidad de generaciones:").pack(pady=5)
        entry_generaciones = tk.Entry(top)
        entry_generaciones.insert(0, "50")  # valor por defecto
        entry_generaciones.pack()

        tk.Label(top, text="Tamaño de la población inicial:").pack(pady=5)
        entry_poblacion = tk.Entry(top)
        entry_poblacion.insert(0, "100")  # valor por defecto
        entry_poblacion.pack()

        tk.Button(top, text="Generar", command=continuar).pack(pady=10)

    def ejecutar_algoritmo_genetico(self, cursos_seleccionados,generaciones=50,poblacion=100):
        cursos_validos_seleccionados = []
        cursos_no_validos_seleccionados = []

        for curso in cursos_seleccionados:
            posibles_docentes = self.relaciones.docentes_para(curso.codigo)
            if posibles_docentes:
                cursos_validos_seleccionados.append(curso)
            else:
                cursos_no_validos_seleccionados.append(curso)
        print(f"Se han seleccionado {len(cursos_validos_seleccionados)} cursos validos.")
        print(f"Se han seleccionado {len(cursos_no_validos_seleccionados)} cursos no validos.")

        ag = AlgoritmoGenetico(
            cursos=cursos_validos_seleccionados,
            docentes=self.docentes,
            salones=self.salones,
            relaciones=self.relaciones,
            generaciones=generaciones,
            poblacion_inicial=poblacion
        )

        inicio = time.time()
        tracemalloc.start()
        ag.generar_poblacion_inicial()
        ag.evolucionar()
        fin = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        ag.tiempo_total = fin - inicio
        ag.uso_ram = f"{current / 1024:.2f} KB"
        ag.pico_ram = f"{peak / 1024:.2f} KB"

        # Exportar el horario generado
        ExportadorExcel.exportar_horario(ag.mejor.asignaciones,self.salones)
        ExportadorPDF.exportar_horario(ag.mejor.asignaciones,self.salones)
        messagebox.showinfo(
            "Éxito", "Horario generado y exportado exitosamente, con una funcion de aptitud de: " + str(ag.mejor.aptitud))
        self.mostrar_vista_edicion(self.salones,ag)

    def calcular_mapas(self, map_horario_salon, map_horario_docente, map_salon_docente, map_curso_semestre, asignaciones:List[Asignacion]):
        for asignacion in asignaciones:
            key_hs = (asignacion.horario, asignacion.salon.nombre)
            key_hd = (asignacion.horario, asignacion.docente.registro)
            key_sd = (asignacion.salon.nombre, asignacion.docente.registro,asignacion.horario)
            key_traspale_csh= (asignacion.curso.carrera,asignacion.curso.semestre,asignacion.horario)

            if key_hs not in map_horario_salon:
                map_horario_salon[key_hs] = []
            map_horario_salon[key_hs].append(asignacion)

            if key_hd not in map_horario_docente:
                map_horario_docente[key_hd] = []
            map_horario_docente[key_hd].append(asignacion)

            if key_sd not in map_salon_docente:
                map_salon_docente[key_sd] = []
            map_salon_docente[key_sd].append(asignacion)

            if asignacion.curso.tipo == "obligatorio":
                if key_traspale_csh not in map_curso_semestre:
                    map_curso_semestre[key_traspale_csh] = []
                map_curso_semestre[key_traspale_csh].append(asignacion)

    def mostrar_vista_edicion(self, salones,algoritmo_genetico:AlgoritmoGenetico):
        ventana = Toplevel()
        ventana.title("Editar Asignaciones")
        ventana.geometry("1000x500")

        tree = ttk.Treeview(ventana, columns=(
            "curso", "docente", "horario", "salon"), show="headings")
        tree.heading("curso", text="Curso")
        tree.heading("docente", text="Docente")
        tree.heading("horario", text="Horario")
        tree.heading("salon", text="Salón")


        asignaciones:List[Asignacion] = algoritmo_genetico.mejor.asignaciones
        # Creamos una lista donde el contenido son la hora de la asignacion en minutos
        comodin_ordenar = []
        for asignacion in asignaciones:
            comodin_ordenar.append((self.hora_a_min(asignacion.horario),asignacion))
        # Ordenamos las asignaciones por horario
        comodin_ordenar.sort(key=lambda x: x[0])
        # Desempacamos la lista de asignaciones
        asignaciones = [asignacion for _,asignacion in comodin_ordenar]

        # Como la asignacion resultante puede tener coliciones de 3 formas:
        # 1. Horario y salon ocupados por otra asignacion
        # 2. Hora y Catedratico ocupados por otra asignacion
        # 3. Salon y Catedratico ocupados por otra asignacion
        # Se generan 3 mapas para cada una de las coliciones

        map_horario_salon = {}
        map_horario_docente = {}
        map_salon_docente = {}
        map_curso_semestre = {}

        # Tag para marcar la filas con errores
        # Diferentes colores para cada tipo de conflicto
        # 1. Horario y salon color: red -> El horario y salon ocupados por otra asignacion
        # 2. Horario y docente color: orange -> El horario y docente ocupados por otra asignacion
        # 3. Salon y docente color: green -> El salon y docente ocupados por otra asignacion
        # 4. Curso obligatorio traslapado color: purple -> El curso obligatorio traslapado por otro curso obligatorio
        tree.tag_configure('horario_salon', background='orange')
        tree.tag_configure('horario_docente', background='green')
        tree.tag_configure('salon_docente', background='red')
        tree.tag_configure('curso_obligatorio_traspale', background='purple')

        # Calcular los mapas de asignaciones
        self.calcular_mapas(
            map_horario_salon, map_horario_docente, map_salon_docente,map_curso_semestre, asignaciones)
        for asignacion in asignaciones:
            key_hs = (asignacion.horario, asignacion.salon.nombre)
            key_hd = (asignacion.horario, asignacion.docente.registro)
            key_sd = (asignacion.salon.nombre, asignacion.docente.registro,asignacion.horario)
            key_traspale_csh= (asignacion.curso.carrera,asignacion.curso.semestre,asignacion.horario)

            es_conflicto1 = len(map_horario_salon[key_hs]) > 1
            es_conflicto2 = len(map_horario_docente[key_hd]) > 1
            es_conflicto3 = len(map_salon_docente[key_sd]) > 1
            es_conflicto4 = len(map_curso_semestre.get(key_traspale_csh, [])) > 1

            tag_asociado = None
            if es_conflicto1:
                tag_asociado = 'horario_salon'
            elif es_conflicto2:
                tag_asociado = 'horario_docente'
            elif es_conflicto3:
                tag_asociado = 'salon_docente'
            elif es_conflicto4:
                tag_asociado = 'curso_obligatorio_traspale'

            tree.insert(
                "", "end",
                values=(
                    asignacion.curso.nombre,
                    (asignacion.docente.nombre + " - " + asignacion.docente.registro),
                    asignacion.horario,
                    asignacion.salon.nombre
                ),
                tags=(tag_asociado,) if tag_asociado else ()
            )

        tree.pack(expand=True, fill="both")

        leyenda_frame = tk.Frame(ventana)
        leyenda_frame.pack(pady=5, anchor="center")

        tk.Label(leyenda_frame, text="Leyenda:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 5)
        )

        # Primera fila de etiquetas
        tk.Label(leyenda_frame, text="Horario y docente en conflicto",
                bg="green", fg="white", width=30).grid(row=1, column=0, padx=10, pady=2)
        tk.Label(leyenda_frame, text="Horario y salón en conflicto",
                bg="orange", fg="white", width=30).grid(row=1, column=1, padx=10, pady=2)

        # Segunda fila de etiquetas
        tk.Label(leyenda_frame, text="Salón y docente en conflicto",
                bg="red", fg="black", width=30).grid(row=2, column=0, padx=10, pady=2)
        tk.Label(leyenda_frame, text="Curso obligatorio traslapado",
                bg="purple", fg="white", width=30).grid(row=2, column=1, padx=10, pady=2)
        
        # Información del algoritmo
        resultados_frame = tk.Frame(ventana)
        resultados_frame.pack(pady=10)

        tk.Label(resultados_frame, text=f"Generaciones: {algoritmo_genetico.generaciones}").grid(row=0, column=0, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Tiempo: {algoritmo_genetico.tiempo_total} s").grid(row=0, column=1, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"RAM usada: {algoritmo_genetico.uso_ram}").grid(row=0, column=2, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Pico RAM: {algoritmo_genetico.pico_ram}").grid(row=0, column=3, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Cantidad PC: {algoritmo_genetico.cantidad_promedio_conflictos}").grid(row=1, column=0, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Cantidad PB: {algoritmo_genetico.cantidad_promedio_bonus}").grid(row=1, column=1, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Cantidad PA: {algoritmo_genetico.cantidad_promedio_aptitud}").grid(row=1, column=2, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Iteraciones Realizadas: {len(algoritmo_genetico.historial_aptitudes)}").grid(row=2, column=0, padx=10, sticky="w")
        tk.Label(resultados_frame, text=f"Aptitud del Actual Horario: {algoritmo_genetico.mejor.aptitud}").grid(row=2, column=1, padx=10, sticky="w")
        

        def aplicar_cambio():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Selecciona", "Selecciona una fila.")
                return
            index = tree.index(selected[0])
            asignacion = asignaciones[index]

            current_key_hs = (asignacion.horario, asignacion.salon.nombre)
            current_key_hd = (asignacion.horario, asignacion.docente.registro)
            current_key_sd = (asignacion.salon.nombre, asignacion.docente.registro,asignacion.horario)

            popup = Toplevel(ventana)
            popup.title("Editar Asignación")

            horarios_disponibles = [
                "13:40", "14:30", "15:20", "16:10", "17:00", "17:50", "18:40", "19:30", "20:20"]

            def hora_str_to_dt(hora_str):
                composicion = hora_str.split(":")
                horas = int(composicion[0])
                minutos = int(composicion[1])
                return horas * 60 + minutos

            inicio = hora_str_to_dt(asignacion.docente.hora_entrada)
            fin = hora_str_to_dt(asignacion.docente.hora_salida)

            horarios = [
                h for h in horarios_disponibles
                if (inicio <= hora_str_to_dt(h)) and ((hora_str_to_dt(h) + 50) <= fin)
            ]

            tk.Label(popup, text="Nuevo Horario:").grid(row=0, column=0)
            combo_horario = ttk.Combobox(popup, state="readonly")
            combo_horario['values'] = horarios
            combo_horario.set(asignacion.horario)
            combo_horario.grid(row=0, column=1)

            tk.Label(popup, text="Nuevo Salón:").grid(row=1, column=0)
            combo_salon = ttk.Combobox(popup, state="readonly")
            nombres_salones = [s.nombre for s in salones]
            combo_salon['values'] = nombres_salones
            combo_salon.set(asignacion.salon.nombre)
            combo_salon.grid(row=1, column=1)

            def validar_y_aplicar():
                nuevo_horario = combo_horario.get()
                nuevo_salon = combo_salon.get()
                conflictos_despues_cambio = None
                try:
                    new_key = (nuevo_horario, nuevo_salon)
                    # Verificar si el nuevo horario y salón ya están ocupados
                    if new_key in map_horario_salon:
                        raise ValueError(
                            "El horario y salón ya están ocupados por otra asignación")
                    # Verificar si el nuevo horario y docente ya están ocupados
                    new_key_hd = (nuevo_horario, asignacion.docente.registro)
                    print(f"new_key_hd: {new_key_hd}")
                    print(f"current_key_hd: {current_key_hd}")
                    if new_key_hd in map_horario_docente and new_key_hd != current_key_hd:
                        raise ValueError(
                            "El horario y docente ya están ocupados por otra asignación")
                    # Verificar si el nuevo salón y docente ya están ocupados
                    new_key_sd = (nuevo_salon, asignacion.docente.registro)
                    print(f"new_key_sd: {new_key_sd}")
                    print(f"current_key_sd: {current_key_sd}")
                    if new_key_sd in map_salon_docente and new_key_sd != current_key_sd:
                        raise ValueError(
                            "El salón y docente ya están ocupados por otra asignación")
                    # Aplicar cambios
                    # buscamos el salon en la lista de salones
                    salon_encontrado = next(
                        (s for s in salones if s.nombre == nuevo_salon), None)
                    if salon_encontrado is None:
                        raise ValueError("El salón no existe")
                    asignacion.horario = nuevo_horario
                    asignacion.salon = salon_encontrado

                    # Recalcular mapas
                    map_horario_salon.clear()
                    map_horario_docente.clear()
                    map_salon_docente.clear()
                    map_curso_semestre.clear()

                    self.calcular_mapas(
                        map_horario_salon, map_horario_docente, map_salon_docente,map_curso_semestre, asignaciones)

                    for item in tree.get_children():
                        tree.delete(item)
                    conflictos_despues_cambio = 0

                    for a in asignaciones:
                        key_hs = (a.horario, a.salon.nombre)
                        key_hd = (a.horario, a.docente.registro)
                        key_sd = (a.salon.nombre, a.docente.registro,a.horario)
                        key_traspale_csh= (asignacion.curso.carrera,asignacion.curso.semestre,asignacion.horario)

                        es_conflicto1 = len(map_horario_salon[key_hs]) > 1
                        es_conflicto2 = len(map_horario_docente[key_hd]) > 1
                        es_conflicto3 = len(map_salon_docente[key_sd]) > 1
                        es_conflicto4 = len(map_curso_semestre.get(key_traspale_csh, [])) > 1

                        tag_asociado = None
                        if es_conflicto1:
                            conflictos_despues_cambio += 1
                            tag_asociado = 'horario_salon'
                        elif es_conflicto2:
                            conflictos_despues_cambio += 1
                            tag_asociado = 'horario_docente'
                        elif es_conflicto3:
                            conflictos_despues_cambio += 1
                            tag_asociado = 'salon_docente'
                        elif es_conflicto4:
                            conflictos_despues_cambio += 1
                            tag_asociado = 'curso_obligatorio_traspale'

                        tree.insert(
                            "", "end",
                            values=(
                                a.curso.nombre,
                                (a.docente.nombre + " - " + a.docente.registro),
                                a.horario,
                                a.salon.nombre
                            ),
                            tags=(tag_asociado,) if tag_asociado else ()
                        )
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    # Lanzar traza para depuración
                    import traceback
                    traceback.print_exc()
                if conflictos_despues_cambio == 0:
                    messagebox.showinfo(
                        "Éxito", "El horario ya no tiene conflictos 🥳")

            tk.Button(popup, text="Aplicar", command=validar_y_aplicar).grid(
                row=2, columnspan=2, pady=10)

        def guardar_cambios():
            ExportadorExcel.exportar_horario(asignaciones)
            ExportadorPDF.exportar_horario(asignaciones)
            messagebox.showinfo(
                "Guardado", "Cambios guardados y exportados exitosamente.")

        boton_frame = tk.Frame(ventana)
        boton_frame.pack(pady=10)

        btn_editar = tk.Button(
            boton_frame, text="Editar selección", command=aplicar_cambio)
        btn_editar.pack(side="left", padx=10)

        btn_guardar = tk.Button(
            boton_frame, text="Guardar y exportar", command=guardar_cambios)
        btn_guardar.pack(side="left", padx=10)

        btn_grafica_aptitud = tk.Button(
            boton_frame, text="Gráfica de Aptitud", command=lambda: self.graficar_aptitud(algoritmo_genetico))
        btn_grafica_aptitud.pack(side="left", padx=10)

        btn_grafica_mejores_aptitudes = tk.Button(
            boton_frame, text="Gráfica Mejores Aptitudes", command=lambda: self.graficar_mejores_aptitudes(algoritmo_genetico))
        btn_grafica_mejores_aptitudes.pack(side="left", padx=10)

        btn_porcentajes_cursos_continuos = tk.Button(
            boton_frame, text="Porcentaje Cursos Continuos", command=lambda: self.mostrar_porcentaje_cursos_continuos(asignaciones))
        btn_porcentajes_cursos_continuos.pack(side="left", padx=10)
    
    def mostrar_porcentaje_cursos_continuos(self, asignaciones:List[Asignacion]):
        # Contamos la cantidad de cursos que hay por ingenieria
        cursos_por_carrera = {}
        continuos_por_carrera = {}
        asignaciones_carrera = {}
        for asignacion in asignaciones:
            carrera = asignacion.curso.carrera
            if carrera not in cursos_por_carrera:
                cursos_por_carrera[carrera] = 0
                asignaciones_carrera[carrera] = []
            asignaciones_carrera[carrera].append(asignacion)
            cursos_por_carrera[carrera] += 1
        # Contamos la cantidad de cursos continuos por ingenieria
        print("Cursos por carrera: ", cursos_por_carrera)

        def contar_continuos(asignaciones:List[Asignacion]):
            bonus = 0
            grupos = {}
            for asignacion in asignaciones:
                key = (asignacion.curso.carrera, asignacion.curso.semestre)
                grupos.setdefault(key, []).append(asignacion.horario)

            for horarios in grupos.values():
                horarios_int = sorted([self.hora_a_min(h) for h in horarios])
                consecutivos = sum(1 for i in range(1, len(horarios_int))
                                if horarios_int[i] - horarios_int[i-1] == 50)
                bonus += consecutivos
            return bonus
        
        # Contamos la cantidad de cursos continuos por ingenieria
        for carrera in cursos_por_carrera.keys():
            if carrera not in continuos_por_carrera:
                continuos_por_carrera[carrera] = 0
            continuos_por_carrera[carrera] = contar_continuos(asignaciones_carrera[carrera])
        
        print("Cursos continuos por carrera: ", continuos_por_carrera)

        ventana = Toplevel(self.root)
        ventana.title("Porcentaje de Cursos Continuos por Carrera")
        ventana.geometry("600x300")

        tree = ttk.Treeview(ventana, columns=("carrera", "cursos", "continuos", "porcentaje"), show="headings")
        tree.heading("carrera", text="Carrera")
        tree.heading("cursos", text="Cursos")
        tree.heading("continuos", text="Continuos")
        tree.heading("porcentaje", text="% Continuos")

        for carrera in cursos_por_carrera:
            total = cursos_por_carrera[carrera]
            continuos = continuos_por_carrera.get(carrera, 0)
            porcentaje = (continuos / total) * 100 if total > 0 else 0
            tree.insert("", "end", values=(carrera, total, continuos, f"{porcentaje:.2f}%"))

        tree.pack(expand=True, fill="both", padx=10, pady=10)


    def graficar_aptitud(self, algoritmo_genetico:AlgoritmoGenetico):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        aptitudes_por_generacion = algoritmo_genetico.historial_aptitudes_generaciones

        ventana_grafica = Toplevel(self.root)
        ventana_grafica.title("Gráfica de Aptitudes por Generación")
        ventana_grafica.geometry("700x450")

        claves = list(aptitudes_por_generacion.keys())
        clave_seleccionada = tk.StringVar(value=claves[0])
        selector = ttk.Combobox(ventana_grafica, values=claves, textvariable=clave_seleccionada, state="readonly")
        selector.pack(pady=10)

        fig, ax = plt.subplots(figsize=(6, 3.5))
        canvas = FigureCanvasTkAgg(fig, master=ventana_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def actualizar_grafico(datos:List[float],generacion:int):
            ax.clear()
            if datos:
                x = list(range(1, len(datos) + 1))
                ax.plot(x, datos, marker='o', color='blue')
                ax.set_title(f"Generacion: {generacion}")
                ax.set_xlabel("Iteraciones")
                ax.set_ylabel("Aptitud")
                ax.grid(True)
            else:
                ax.set_title(f"Sin datos para: {generacion}")
            canvas.draw()

        selector.bind("<<ComboboxSelected>>", lambda event: actualizar_grafico(aptitudes_por_generacion[clave_seleccionada.get()], clave_seleccionada.get()))

        # Mostrar primera clave
        actualizar_grafico(aptitudes_por_generacion[claves[0]], claves[0])

    def graficar_mejores_aptitudes(self, algoritmo_genetico:AlgoritmoGenetico):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        ventana_grafica = Toplevel(self.root)
        ventana_grafica.title("Evolución de la Aptitud")
        ventana_grafica.geometry("600x400")

        fig, ax = plt.subplots(figsize=(6, 3.5))
        horarios = list(range(1, len(algoritmo_genetico.aptitudes_mejores_generaciones) + 1))
        ax.plot(horarios, algoritmo_genetico.aptitudes_mejores_generaciones, marker='o', color='blue')
        ax.set_title("Mejores Apttitudes por Generacion")
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Aptitud")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=ventana_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppHorario(root)
    root.mainloop()
