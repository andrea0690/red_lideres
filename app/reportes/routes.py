# app/reports/routes.py
import io
import xlsxwriter
from flask import send_file
from flask_login import login_required
from . import reports_bp
from app.models import Miembro

@reports_bp.route('/miembros/exportar')
@login_required
def exportar_miembros_excel():
    # 1. Prepara el archivo en memoria
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Miembros')

     # --- Formato de encabezados ---
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',  # azul claro
        'border': 1,
        'align': 'center'
    })

    # 2. Define los encabezados
    headers = ['Nombre Completo', 'Email', 'Rol', 'Líder', 'Fecha de Ingreso']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header, header_format)

    # 3. Obtiene los datos y los escribe en el archivo
    miembros = Miembro.query.order_by(Miembro.nombre_completo.asc()).all()
    for row_num, miembro in enumerate(miembros, 1): # Empezamos en la fila 1
        lider_nombre = miembro.lider.nombre_completo if miembro.lider else 'N/A'
        worksheet.write(row_num, 0, miembro.nombre_completo)
        worksheet.write(row_num, 1, miembro.email)
        worksheet.write(row_num, 2, miembro.rol.nombre)
        worksheet.write(row_num, 3, lider_nombre)
        worksheet.write(row_num, 4, miembro.fecha_ingreso.strftime('%Y-%m-%d'))

    # --- Ajustar anchos de columnas ---
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 20)
    
    # 4. Cierra el libro de trabajo y prepara el envío
    workbook.close()
    output.seek(0) # Vuelve al inicio del "archivo" en memoria

    return send_file(
        output,
        as_attachment=True,
        download_name='reporte_miembros.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
