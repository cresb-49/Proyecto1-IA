from jinja2 import Template
from pdfkit.api import configuration
import pdfkit
import platform


class ExportadorPDF:
    @staticmethod
    def exportar_horario(asignaciones, nombre_pdf="horario_generado"):
        horarios = ["13:40", "14:30", "15:20", "16:10",
                    "17:00", "17:50", "18:40", "19:30", "20:20"]
        salones = list({a.salon.nombre for a in asignaciones})

        tabla = {hora: {s: "" for s in salones} for hora in horarios}
        for a in asignaciones:
            content = f"{a.curso.nombre}<br>{a.curso.codigo}<br>{a.docente.nombre}<br>Semetre: {a.curso.semestre}<br>{a.curso.carrera}"
            tabla[a.horario][a.salon.nombre] = content

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; text-align: center; padding: 6px; font-size: 11px; }
            th { background-color: #f2f2f2; }
          </style>
        </head>
        <body>
          <h2>Horario de Clases</h2>
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
        </body>
        </html>
        """)

        html = template.render(horarios=horarios, salones=salones, tabla=tabla)

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
