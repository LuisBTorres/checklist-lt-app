import flet as ft
import datetime
import urllib.parse
import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors, pagesizes

# ================= APP =================
def main(page: ft.Page):
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE_700)
    page.bgcolor = "#F4F6F9"
    page.title = "Recepción Vehicular PRO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0 

    if page.platform not in ["android", "ios"]:
        page.window.width = 450
        page.window.height = 800

    def mostrar_snack(mensaje, color=ft.colors.GREEN):
        snack = ft.SnackBar(
            content=ft.Text(mensaje, size=16, weight="bold"),
            bgcolor=color,
            duration=4000,
            action="OK"
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # ================= CAMPOS =================
    txt_fecha = ft.TextField(
        label="Fecha",
        value=datetime.datetime.now().strftime("%d/%m/%Y"),
        border_radius=12,
        read_only=True
    )

    # Campos de Cliente [cite: 7, 8, 9, 10, 11]
    inputs_cliente = {
        "Nombre": ft.TextField(label="Nombre", border_radius=12, capitalization=ft.TextCapitalization.WORDS),
        "Apellido": ft.TextField(label="Apellido", border_radius=12, capitalization=ft.TextCapitalization.WORDS),
        "Domicilio": ft.TextField(label="Domicilio", border_radius=12),
        "Teléfono": ft.TextField(
            label="Teléfono (Ej: 54911...)", 
            value="549", 
            border_radius=12, 
            keyboard_type=ft.KeyboardType.PHONE,
            prefix_icon=ft.icons.PHONE_ANDROID
        ),
        "DNI/CUIT": ft.TextField(label="DNI/CUIT", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER),
        "e-mail": ft.TextField(label="e-mail", border_radius=12, keyboard_type=ft.KeyboardType.EMAIL),
    }

    col_cliente = ft.Column(controls=list(inputs_cliente.values()), spacing=8)

    # Campos de Vehículo [cite: 13, 14, 15, 16, 17, 18]
    inputs_vehiculo = {
        "Marca": ft.TextField(label="Marca", border_radius=12, capitalization=ft.TextCapitalization.WORDS),
        "Modelo": ft.TextField(label="Modelo", border_radius=12, capitalization=ft.TextCapitalization.WORDS),
        "Año": ft.TextField(label="Año", border_radius=12, keyboard_type=ft.KeyboardType.NUMBER),
        "Patente": ft.TextField(label="Patente", border_radius=12, capitalization=ft.TextCapitalization.CHARACTERS),
        "Motor": ft.TextField(label="Motor", border_radius=12),
        "Transmisión": ft.Dropdown(
            label="Transmisión", 
            border_radius=12, 
            options=[ft.dropdown.Option("Manual"), ft.dropdown.Option("Automática")]
        ),
    }

    col_vehiculo = ft.Column(controls=list(inputs_vehiculo.values()), spacing=8)

    # ================= INVENTARIO (S/N) [cite: 19, 21, 22, 26, 27, 28, 29, 30, 31, 32] =================
    inventario_items = [
        "Estereo", "Extintor", "Balizas", "Crique", "R.Auxilio",
        "Herramientas", "Alfombras", "Cintos Seg.", "Parasol Der.", 
        "Parasol Izq.", "Tapa de combustible"
    ]
    inputs_inventario = {item: ft.Checkbox(label=item) for item in inventario_items}
    col_inventario = ft.Column(controls=list(inputs_inventario.values()), spacing=5)

    # ================= TABLERO [cite: 20, 23, 24, 25, 48, 49, 50, 51, 52, 53, 54, 55, 56] =================
    tablero_items = [
        "Aceite", "Batería", "Temperatura", "Check Engine", "ABS",
        "Airbag", "Freno Mano", "Neumáticos", "Precalentamiento",
        "Dirección", "DPF", "Inmovilizado", "Lámpara Quem.", "Caja Automática"
    ]
    inputs_tablero = {item: ft.Checkbox(label=item) for item in tablero_items}
    col_tablero = ft.Column(controls=list(inputs_tablero.values()), spacing=5)

    # ================= EXTERIOR (B/M) [cite: 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46] =================
    exterior_items = [
        "Limpiaparabrisas DI", "Limpiaparabrisas DD", "Limpiaparabrisas Tras.",
        "Tasa rueda DD", "Tasa rueda DI", "Tasa rueda TD", "Tasa rueda TI",
        "Parabrisas", "Luneta", "Vidrio DD", "Vidrio DI", "Vidrio TD", "Vidrio TI"
    ]
    
    inputs_exterior = {}
    col_exterior = ft.Column(spacing=5)
    for item in exterior_items:
        rg = ft.RadioGroup(
            content=ft.Row([
                ft.Text(item, width=150, size=12),
                ft.Radio(value="B", label="B"),
                ft.Radio(value="M", label="M"),
            ])
        )
        inputs_exterior[item] = rg
        col_exterior.controls.append(rg)

    txt_obs = ft.TextField(
        label="Observaciones",
        multiline=True,
        min_lines=3,
        border_radius=12,
        capitalization=ft.TextCapitalization.SENTENCES
    )

    # ================= ACCIONES =================
    ultimo_pdf_generado = [None] 

    def generar_pdf(e):
        try:
            if not inputs_vehiculo["Patente"].value:
                mostrar_snack("Error: La patente es obligatoria", ft.colors.RED)
                return

            patente = inputs_vehiculo["Patente"].value
            fecha_archivo = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            
            # Ruta de descargas
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads, exist_ok=True)

            nombre_archivo = os.path.join(downloads, f"Checklist_{patente}_{fecha_archivo}.pdf")
            ultimo_pdf_generado[0] = nombre_archivo

            doc = SimpleDocTemplate(
                nombre_archivo,
                pagesize=pagesizes.A4,
                topMargin=20, bottomMargin=20, leftMargin=20, rightMargin=20,
            )

            styles = getSampleStyleSheet()
            style_title = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=14, alignment=0, spaceAfter=10)
            style_small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8.5, leading=10)

            elementos = []
            elementos.append(Paragraph(f"<b>CHECKLIST RECEPCION by LT</b> - Fecha: {txt_fecha.value}", style_title))
            elementos.append(Spacer(1, 10))

            def crear_tabla_seccion(titulo, datos_dict, columnas=2):
                data = [[Paragraph(f"<b>{titulo}</b>", styles["Normal"])]]
                items = list(datos_dict.items())
                for i in range(0, len(items), columnas):
                    fila = []
                    for j in range(columnas):
                        if i + j < len(items):
                            k, v = items[i + j]
                            if isinstance(v, ft.TextField): valor = v.value or ""
                            elif isinstance(v, ft.Checkbox): valor = "SI" if v.value else "NO"
                            elif isinstance(v, ft.RadioGroup): valor = v.value or "-"
                            else: valor = ""
                            fila.append(Paragraph(f"<b>{k}:</b> {valor}", style_small))
                        else: fila.append("")
                    data.append(fila)
                
                t = Table(data, colWidths=[540/columnas]*columnas)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("SPAN", (0, 0), (-1, 0)),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]))
                return t

            elementos.append(crear_tabla_seccion("CLIENTE", inputs_cliente))
            elementos.append(Spacer(1, 10))
            elementos.append(crear_tabla_seccion("VEHICULO", inputs_vehiculo))
            elementos.append(Spacer(1, 10))
            elementos.append(crear_tabla_seccion("REVISION TECNICA - INVENTARIO (S/N)", inputs_inventario, 3))
            elementos.append(Spacer(1, 10))
            elementos.append(crear_tabla_seccion("INDICADORES DE TABLERO", inputs_tablero, 3))
            elementos.append(Spacer(1, 10))
            elementos.append(crear_tabla_seccion("ESTADO EXTERIOR (B/M)", inputs_exterior, 3))
            elementos.append(Spacer(1, 10))

            obs_data = [[Paragraph("<b>OBSERVACIONES</b>", styles["Normal"])], [Paragraph(txt_obs.value or "-", style_small)]]
            t_obs = Table(obs_data, colWidths=[540])
            t_obs.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("GRID", (0, 0), (-1, -1), 0.5, colors.black), ("PADDING", (0, 0), (-1, -1), 5)]))
            elementos.append(t_obs)

            doc.build(elementos)
            
            # NUEVO AVISO SOLICITADO
            mostrar_snack("✅ PDF GENERADO EN CARPETA DE DESCARGAS", ft.colors.GREEN_800)

        except Exception as ex:
            mostrar_snack(f"❌ Error al generar: {str(ex)}", ft.colors.RED)

    def enviar_whatsapp(e):
        num = inputs_cliente["Teléfono"].value
        num_limpio = "".join(filter(str.isdigit, str(num)))
        if not num_limpio or len(num_limpio) < 8:
            mostrar_snack("⚠️ Ingrese un teléfono de contacto válido", ft.colors.ORANGE_800)
            return
        if not ultimo_pdf_generado[0]:
            mostrar_snack("⚠️ Primero debe generar el PDF", ft.colors.ORANGE_800)
            return
        
        mensaje = f"Hola! Le enviamos el checklist de recepción de su vehículo (Patente: {inputs_vehiculo['Patente'].value})."
        page.launch_url(f"https://wa.me/{num_limpio}?text={urllib.parse.quote(mensaje)}")
        mostrar_snack("Abriendo WhatsApp... Adjunte el archivo desde Descargas", ft.colors.BLUE_700)

    # ================= LAYOUT =================
    def card(titulo_txt, contenido):
        return ft.Container(
            content=ft.Column([ft.Text(titulo_txt, size=16, weight="bold"), ft.Divider(), contenido]),
            bgcolor=ft.colors.WHITE, border_radius=12, padding=15,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.colors.BLACK12),
        )

    page.add(
        ft.SafeArea(
            ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text("RECEPCIÓN VEHICULAR PRO", size=22, weight="bold", color=ft.colors.BLUE_800),
                    txt_fecha,
                    card("👤 DATOS DEL CLIENTE", col_cliente),
                    card("🚗 DATOS DEL VEHÍCULO", col_vehiculo),
                    card("🧰 INVENTARIO (S/N)", col_inventario),
                    card("⚠ INDICADORES TABLERO", col_tablero),
                    card("🚘 EXTERIOR (B/M)", col_exterior),
                    card("📝 OBSERVACIONES", txt_obs),
                    ft.ElevatedButton(
                        "GENERAR PDF", 
                        icon=ft.icons.PICTURE_AS_PDF, 
                        on_click=generar_pdf, 
                        width=400, height=55, 
                        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                    ft.ElevatedButton(
                        "ENVIAR POR WHATSAPP", 
                        icon=ft.icons.SEND, 
                        on_click=enviar_whatsapp, 
                        width=400, height=55, 
                        style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                    ft.Container(height=30)
                ], scroll=ft.ScrollMode.AUTO)
            )
        )
    )

ft.app(target=main)
