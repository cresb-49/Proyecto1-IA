from typing import List
from jinja2 import Template
from pdfkit.api import configuration
import pdfkit
import platform

from clases import Asignacion, Salon

class ExportadorPDF:
    @staticmethod
    def exportar_horario(asignaciones:List[Asignacion],salones:List[Salon], nombre_pdf="horario_generado"):
        horarios = ["13:40", "14:30", "15:20", "16:10",
                    "17:00", "17:50", "18:40", "19:30", "20:20"]
        nombres_salones = sorted({s.nombre for s in salones})

        tabla = {hora: {s: "" for s in nombres_salones} for hora in horarios}
        for a in asignaciones:
            content = f"{a.curso.nombre}<br>{a.curso.codigo}<br>{a.docente.nombre}<br>Semetre: {a.curso.semestre}<br>{a.curso.carrera}"
            tabla[a.horario][a.salon.nombre] = content

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            @page {
              size: A4 landscape;
              margin: 1cm;
            }
            body {
              font-family: Arial, sans-serif;
              margin: 0;
              padding: 0;
            }
            .escalado {
              transform: scale(0.75); /* Ajusta según necesidad */
              transform-origin: top left;
            }
            table {
              border-collapse: collapse;
              width: 100%;
              table-layout: fixed;
            }
            th, td {
              border: 1px solid #ccc;
              min-width: 120px;
              text-align: center;
              padding: 6px;
              font-size: 10px;
              word-wrap: break-word;
            }
            th {
              background-color: #f2f2f2;
            }
          </style>
        </head>
        <body>
          <h2>Horario de Clases</h2>
          <div class="escalado">
            <table>
              <tr>
                <th>Hora</th>
                {% for salon in salones %}
                <th>{{ salon }}</th>
                {% endfor %}
              </tr>
              {% for hora in horarios %}
              <tr>
                <td>{{ hora }}</td>
                {% for salon in salones %}
                <td>{{ tabla[hora][salon]|safe }}</td>
                {% endfor %}
              </tr>
              {% endfor %}
            </table>
          </div>
        </body>
        </html>
        """)

        html = template.render(horarios=horarios, salones=nombres_salones, tabla=tabla)

        with open("horario_generado.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Detectamos si estamos en windows o linux
        sysos = platform.system()
        print(f"Sistema operativo detectado: {sysos}")
        if sysos == "Linux":
            pdfkit.from_file("horario_generado.html", (nombre_pdf+"landscape.pdf"),
                             options={"orientation": "Landscape"})
            pdfkit.from_file("horario_generado.html", nombre_pdf+".pdf")
            print(f"PDF generado: {nombre_pdf}")
        elif sysos == "Windows":
            wkhtml_config = configuration(
                wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
            pdfkit.from_file("horario_generado.html", (nombre_pdf+"landscape.pdf"),
                             configuration=wkhtml_config, options={"orientation": "Landscape"})
            pdfkit.from_file("horario_generado.html", nombre_pdf+".pdf",
                             configuration=wkhtml_config)
            print(f"PDF generado: {nombre_pdf}")
        elif sysos == "Darwin":
            from weasyprint import HTML
            HTML("horario_generado.html").write_pdf(
                (nombre_pdf+".pdf"))