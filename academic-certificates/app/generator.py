import reportlab
print(reportlab.Version)

import pandas as pd
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

# =========================
# FILES
# =========================

xlsx = "Notas_Demo.xlsx"
logo = "logo.png"
output_pdf = "CertificadoNotas_Demo.pdf"

# =========================
# READ EXCEL FILE
# =========================

raw = pd.read_excel(xlsx, sheet_name=0, header=None)
institution = str(raw.iloc[0, 0]).strip().title()
level = str(raw.iloc[1, 0]).split(":", 1)[-1].strip().title()
course = str(raw.iloc[2, 0]).split(":", 1)[-1].strip().title()
school_shift = str(raw.iloc[3, 0]).split(":", 1)[-1].strip().title()
section = str(raw.iloc[4, 0]).split(":", 1)[-1].strip().upper()
academic_period = str(raw.iloc[5, 0]).split(":", 1)[-1].strip().title()

subjects = [
    str(x).strip().title()
    for x in raw.iloc[6, 1:12].tolist()
]

data = raw.iloc[8:, 0:12].copy()
data = data[data.iloc[:, 0].notna()].reset_index(drop=True)
students = []

for _, row in data.iterrows():
    name = str(row.iloc[0]).strip().title()
    grades = []
    values = []

    for subject, value in zip(
        subjects,
        row.iloc[1:12].tolist()
    ):
        try:
            grade = float(value)
        except:
            continue
        grades.append((subject, grade))
        values.append(grade)

    average = sum(values) / len(values)
    students.append({

        "name": name,
        "grades": grades,
        "average": average
    })

# =========================
# HELPER FUNCTIONS
# =========================

def format_number(value):
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")
def fit_text(
    pdf,
    text,
    font="Helvetica-Bold",
    max_font_size=14,
    min_font_size=8,
    max_width=100 * mm

):

    font_size = max_font_size
    while (
        font_size > min_font_size
        and stringWidth(text, font, font_size) > max_width
    ):

        font_size -= 0.3
    pdf.setFont(font, font_size)

    return font_size

# =========================

# PDF CONFIGURATION

# =========================

PAGE_WIDTH, PAGE_HEIGHT = A4
HALF_PAGE = PAGE_HEIGHT / 2

pdf = canvas.Canvas(
    output_pdf,
    pagesize=A4 #Define pagesize
)

blue = colors.HexColor("#173d6d")
light_blue = colors.HexColor("#e9eff7")
light_gray = colors.HexColor("#cbd7e6")
gray = colors.HexColor("#666666")

# Logo aspect ratio
logo_image = Image.open(logo)
logo_ratio = (
    logo_image.width /
    logo_image.height
)

# =========================
# DRAW CERTIFICATE
# =========================

def draw_certificate(
    pdf,
    start_y,
    student
):
    # ---------------------
    # BORDER
    # ---------------------

    horizontal_margin = 10 * mm
    top_margin = 8 * mm
    bottom_margin = 7 * mm
    box_x = horizontal_margin
    box_y = start_y + bottom_margin
    box_width = PAGE_WIDTH - 2 * horizontal_margin
    box_height = (

        HALF_PAGE
        - top_margin
        - bottom_margin
    )

    pdf.setStrokeColor(blue) #DEfine border Color blue
    #pdf.setStrokeColor(colors.red) #DEfine border color red
    pdf.setLineWidth(1.3)
    pdf.roundRect(

        box_x,
        box_y,
        box_width,
        box_height,

        3 * mm # DEFINE ROUNDED EDGE SIZE

    )

    # TOP DECORATIVE LINE

    pdf.setLineWidth(0.8)
    pdf.line(

        box_x + 2.5 * mm,
        box_y + box_height - 0.8 * mm,
        box_x + box_width - 3 * mm,
        box_y + box_height - 0.8 * mm
    )

    # =====================
    # LOGO
    # =====================

    logo_width = 40 * mm
    logo_height = logo_width / logo_ratio
    logo_x = box_x + 7 * mm

    # Adjust the logo vertical position here
    logo_y = (
        box_y
        + box_height
        - logo_height
        + 9 * mm
    )

    pdf.drawImage(
        logo,
        logo_x,
        logo_y,
        width=logo_width,
        height=logo_height,
        preserveAspectRatio=True,
        mask="auto"
    )

    # =====================
    # HEADER
    # =====================

    center_x = box_x + box_width / 2
    title_y = (
        box_y
        + box_height
        - 6 * mm
    )

    fit_text(
        pdf,
        institution,
        "Helvetica-Bold",
        13.8,
        10,
        120 * mm
    )

    pdf.setFillColor(blue)
    pdf.drawCentredString(
        center_x,
        title_y,
        institution
    )

    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 8.7)
    pdf.drawCentredString(
        center_x,
        title_y - 5.1 * mm,
        "AÑO LECTIVO 2026-2027" #DEFINE "AÑO LECTIVO"
    )

    pdf.setFillColor(colors.black)
    pdf.setFont(
        "Helvetica-Bold",
        10.8
    )
    pdf.drawCentredString(
        center_x,
        title_y - 12.8 * mm,
        "CERTIFICADO DE CALIFICACIONES"
    )

    # =====================
    # STUDENT
    # =====================
    band_y = (
        title_y
        - 24 * mm
    )

    # COLOR BOX AND POSITION (ESTUDIANTE:NAME)
    pdf.setFillColor(light_blue)
    pdf.roundRect(
        box_x + 4 * mm,
        band_y,
        box_width - 8 * mm,
        7.5 * mm,
        1.2 * mm,

        fill=1,
        stroke=0
    )

    pdf.setFillColor(blue)
    pdf.setFont(
        "Helvetica-Bold",
        8.7
    )

    pdf.drawString(
        box_x + 6 * mm,
        band_y + 2.25 * mm,
        "ESTUDIANTE: "
    )

    fit_text(
        pdf,
        student["name"],
        "Helvetica-Bold",
        10,
        8,
        box_width - 40 * mm
    )

    pdf.setFillColor(colors.black)
    pdf.drawString(
        box_x + 28 * mm,
        band_y + 2.2 * mm,
        student["name"]
    )

    # =====================
    # COURSE DETAILS
    # =====================

    metadata_y = (
        band_y
        - 7.8 * mm
    )

    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 7.9)
    pdf.drawString(
        box_x + 5 * mm,
        metadata_y,
        f"Nivel: {level}"
    )

    pdf.drawString(
        box_x + 5 * mm,
        metadata_y - 5 * mm,
        f"Paralelo: {section}"
    )

    pdf.drawCentredString(
        center_x + 0.5 * mm,
        metadata_y - 5 * mm,
        f"Jornada: {school_shift}"
    )

    pdf.drawRightString(
        box_x + box_width - 4.5 * mm,
        metadata_y,
        f"Curso: {course}"

    )

    pdf.drawRightString(
        box_x + box_width - 4.5 * mm,
        metadata_y - 5 * mm,
        f"Periodo: {academic_period}"
    )

    # =====================
    # TABLES
    # =====================

    left_grades = (
        student["grades"][:6]
    )

    right_grades = (
        student["grades"][6:]
    )

    table_top = (
        metadata_y
        - 9 * mm
    )

    table_x1 = (
        box_x
        + 5 * mm
    )

    table_gap = 4 * mm
    table_width = (
        box_width
        - 10 * mm
        - table_gap
    ) / 2

    table_x2 = (
        table_x1
        + table_width
        + table_gap
    )

    header_height = 6 * mm
    row_height = 5.8 * mm

    def draw_table(
        x,
        subjects_to_draw,
        number_of_rows=6
    ):

        # Header
        pdf.setFillColor(blue)
        pdf.setStrokeColor(blue)
        pdf.rect(
            x,
            table_top - header_height,
            table_width,
            header_height,

            fill=1,
            stroke=1

        )

        pdf.setFillColor(colors.white)
        pdf.setFont(
            "Helvetica-Bold",
            8.5
        )

        pdf.drawString(
            x + 2.2 * mm,
            table_top
            - header_height
            + 1.8 * mm,
            "ASIGNATURA"
        )

        pdf.drawRightString(
            x
            + table_width
            - 2.2 * mm,
            table_top
            - header_height
            + 1.8 * mm,
            "NOTA"
        )

        subject_col_width = (
            table_width * 0.84
        )
        body_y = (
            table_top
            - header_height
        )

        pdf.setStrokeColor(
            light_gray
        )

        pdf.setFillColor(
            colors.black
        )

        for i in range(
            number_of_rows
        ):
            y = (
                body_y
                - (i + 1)
                * row_height
            )
            pdf.rect(
                x,
                y,
                table_width,
                row_height
            )

            pdf.line(
                x + subject_col_width,
                y,
                x + subject_col_width,
                y + row_height
            )

            if i < len(subjects_to_draw):
                subject, grade = (
                    subjects_to_draw[i]
                )
                font_size = 7.3
                available_width = (
                    subject_col_width
                    - 4.2 * mm
                )

                while (
                    font_size > 6
                    and stringWidth(
                        subject,
                        "Helvetica",
                        font_size
                    ) > available_width

                ):
                    font_size -= 0.2
                pdf.setFont(
                    "Helvetica",
                    font_size
                )

                pdf.drawString(
                    x + 1.8 * mm,
                    y + 1.7 * mm,
                    subject
                )

                pdf.setFont(
                    "Helvetica-Bold",
                    7.4
                )

                pdf.drawRightString(
                    x
                    + table_width
                    - 1.9 * mm,
                    y
                    + 1.7 * mm,
                    format_number(grade)
                )

        return (
            body_y
            - number_of_rows
            * row_height
        )

    left_bottom = draw_table(
        table_x1,
        left_grades
    )

    right_bottom = draw_table(
        table_x2,
        right_grades
    )

    tables_bottom = min(
        left_bottom,
        right_bottom
    )

    # =====================
    # AVERAGE
    # =====================

    average_y = (
        tables_bottom
        - 7 * mm
    )

    pdf.setFillColor(blue)
    pdf.setFont(
        "Helvetica-Bold",
        9.3
    )

    pdf.drawString(
        table_x1,
        average_y,
        f"PROMEDIO GENERAL:  "
        f"{format_number(student['average'])}"
        " / 10"

    )

    pdf.setFillColor(gray)
    pdf.setFont(
        "Helvetica",
        7.8
    )

    pdf.drawRightString(
        box_x
        + box_width
        - 5 * mm,
        average_y,
        "Escala de calificación: 0 a 10"
    )
    # =====================
    # CERTIFICATION TEXT
    # =====================

    certificate_text_y = (
        average_y
        - 5.4 * mm
    )

    pdf.setFillColor(
        colors.black
    )

    pdf.setFont(
        "Helvetica",
        8

    )

    pdf.drawCentredString(
        center_x,
        certificate_text_y,
        "Se certifica que las calificaciones anteriores "
        "corresponden al registro académico del "
        "Trimestre 1 del año lectivo 2026-2027." #NEXT EVENT UPDATE "Trimestre 1" AND "año lectivo" GLOBALLY
    )

    # =====================
    # SIGNATURES
    # =====================

    signature_y = (
        box_y
        + 14 * mm
    )

    signature_line_width = (
        36 * mm
    )

    signature_positions = [
        box_x + 33 * mm,
        center_x,
        box_x
        + box_width
        - 33 * mm
    ]

    signatory_names = [
        "Mgtr. Meriadoc Brandigamo",
        "Lic. Théoden",
        ""
    ]

    roles = [
        "RECTOR",
        "TUTOR",
        "REPRESENTANTE"
    ]

    pdf.setStrokeColor(
        colors.black
    )

    pdf.setLineWidth(0.7)
    for i, x in enumerate(
        signature_positions
    ):
        pdf.line(
            x - signature_line_width / 2,
            signature_y + 7.5 * mm,
            x + signature_line_width / 2,
            signature_y + 7.5 * mm
        )
        if signatory_names[i]:
            pdf.setFont(
                "Helvetica",
                7.8
            )
            pdf.drawCentredString(
                x,
                signature_y + 3 * mm,
                signatory_names[i]
            )

        pdf.setFont(
            "Helvetica-Bold",
            8.1
        )
        pdf.drawCentredString(
            x,
            signature_y - 1.5 * mm,
            roles[i]
        )
    # =====================
    # FOOTER
    # =====================

    pdf.setFillColor(gray)
    pdf.setFont(
        "Helvetica",
        6.2
    )

    pdf.drawRightString(
        box_x
        + box_width
        - 3 * mm,
        box_y
        + 2.8 * mm,
        "Documento generado a partir "
        "del reporte oficial de calificaciones" #REPORT DOWNLOAD OF ACADEMICO.GOB

    )

# =========================
# GENERATE ALL CERTIFICATES
# =========================

for i, student in enumerate(students):
    # Even-indexed student -> top half
    if i % 2 == 0:
        start_y = HALF_PAGE
    # Odd-indexed student -> bottom half

    else:
        start_y = 0
    draw_certificate(

        pdf,
        start_y,
        student
    )
    #Correctly bugs

    #=========================
    # After processing two students, finish the page
    if (
        i % 2 == 1
        or i == len(students) - 1
    ):
        # Cutting line
        pdf.setDash(3, 2)
        pdf.setStrokeColor(

            colors.HexColor("#bbbbbb")
        )

        pdf.line(
            10 * mm,
            HALF_PAGE,
            PAGE_WIDTH - 10 * mm,
            HALF_PAGE
        )

        pdf.setDash()
        pdf.showPage()
    #========================

pdf.save()

print(

    f"PDF_Generated_: {output_pdf}"

)
