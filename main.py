from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import engine, get_db
import models
import os
import shutil
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")
os.makedirs("pdf_files", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/pdf_files", StaticFiles(directory="pdf_files"), name="pdf_files")

templates = Jinja2Templates(directory=".")

pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__truncate_error=False
)

CONFIG_FILE = "company_config.json"

def get_company_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "Soluciones Integrales de Ingeniería Informática",
        "phone": "+503 7054 4109",
        "address": "San Salvador, El Salvador",
        "next_cotizacion_num": "COT-2026-001",
        "validez_oferta": "5 días hábiles",
        "condiciones_pago": "50% de anticipo al confirmar la orden y 50% contra entrega / recepción al finalizar el proyecto.",
        "instalacion_nota": "Incluye la puesta en marcha del sistema y la configuración en el teléfono móvil del cliente.",
        "garantias_texto": "- Los equipos cuentan con 1 año de garantía. La garantía no cubre cables cortados ni equipos sucios por falta de mantenimiento."
    }

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.is_active == True).all()
    return templates.TemplateResponse(request, "dashboard.html", {"request": request, "products": products})

@app.get("/configuracion", response_class=HTMLResponse)
def configuracion_page(request: Request):
    config = get_company_config()
    return templates.TemplateResponse(request, "configuracion.html", {"request": request, "config": config})

@app.post("/actualizar-empresa")
async def actualizar_empresa(
    company_name: str = Form(...),
    company_phone: str = Form(...),
    company_address: str = Form(...),
    next_cotizacion_num: str = Form(...),
    validez_oferta: str = Form(...),
    condiciones_pago: str = Form(...),
    instalacion_nota: str = Form(...),
    garantias_texto: str = Form(...),
    company_logo: UploadFile = File(None)
):
    config = {
        "name": company_name,
        "phone": company_phone,
        "address": company_address,
        "next_cotizacion_num": next_cotizacion_num,
        "validez_oferta": validez_oferta,
        "condiciones_pago": condiciones_pago,
        "instalacion_nota": instalacion_nota,
        "garantias_texto": garantias_texto
    }
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
        
    if company_logo and company_logo.filename:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        logo_path = os.path.join(upload_dir, "company_logo.png")
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(company_logo.file, buffer)
            
    return RedirectResponse(url="/configuracion", status_code=303)

# --- RUTAS DE GESTIÓN DE PRODUCTOS ---

@app.get("/productos", response_class=HTMLResponse)
def productos_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return templates.TemplateResponse(request, "productos.html", {"request": request, "products": products})

@app.post("/productos/crear")
def crear_producto(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    nuevo_prod = models.Product(name=name, price=price, description=description, is_active=True)
    db.add(nuevo_prod)
    db.commit()
    return RedirectResponse(url="/productos", status_code=303)

@app.post("/productos/editar/{product_id}")
def editar_producto(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.name = name
        product.price = price
        product.description = description
        db.commit()
    return RedirectResponse(url="/productos", status_code=303)

@app.get("/productos/toggle/{product_id}")
def toggle_producto(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        product.is_active = not product.is_active
        db.commit()
    return RedirectResponse(url="/productos", status_code=303)

# --- RUTA DE HISTORIAL DE COTIZACIONES ---

@app.get("/cotizaciones", response_class=HTMLResponse)
def listar_cotizaciones(
    request: Request, 
    q: str = None, 
    fecha: str = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Quotations)
    
    if q:
        query = query.filter(models.Quotations.client_name.ilike(f"%{q}%"))
        
    if fecha:
        query = query.filter(models.Quotations.date == fecha)
        
    cotizaciones = query.order_by(models.Quotations.id.desc()).all()
    
    return templates.TemplateResponse(request, "cotizaciones.html", {
        "request": request, 
        "cotizaciones": cotizaciones,
        "q": q or "",
        "fecha": fecha or ""
    })

# ------------------------------------

@app.post("/crear-cotizacion")
def crear_cotizacion(
    request: Request,
    client_name: str = Form(...),
    client_address: str = Form(...),
    client_phone: str = Form(None),
    product_id: list[int] = Form(...),
    quantity: list[int] = Form(...),
    apply_iva: bool = Form(False),
    db: Session = Depends(get_db)
):
    subtotal_general = 0.0
    items_data = []

    for p_id, qty in zip(product_id, quantity):
        product = db.query(models.Product).filter(models.Product.id == p_id).first()
        if product:
            subtotal = product.price * qty
            subtotal_general += subtotal
            items_data.append({
                "name": product.name,
                "price": product.price,
                "quantity": qty,
                "subtotal": subtotal,
                "description": product.description
            })

    iva_amount = subtotal_general * 0.13 if apply_iva else 0.0
    total_general = subtotal_general + iva_amount

    comp_config = get_company_config()
    current_cot_num = comp_config.get("next_cotizacion_num", "COT-2026-001")
    
    try:
        parts = current_cot_num.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            prefix = parts[0]
            num_len = len(parts[1])
            next_num_val = int(parts[1]) + 1
            next_cot_num_auto = f"{prefix}-{str(next_num_val).zfill(num_len)}"
            comp_config["next_cotizacion_num"] = next_cot_num_auto
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(comp_config, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

    nueva_cotizacion = models.Quotations(
        client_name=client_name,
        client_phone=client_phone if client_phone else "N/A",
        client_address=client_address,
        subtotal=subtotal_general,
        apply_iva=apply_iva,
        total=total_general,
        date=datetime.datetime.now().strftime('%Y-%m-%d')
    )
    db.add(nueva_cotizacion)
    db.commit()
    db.refresh(nueva_cotizacion)

    for item in items_data:
        prod_obj = db.query(models.Product).filter(models.Product.name == item["name"]).first()
        nuevo_item = models.QuotationItem(
            quotation_id=nueva_cotizacion.id,
            product_id=prod_obj.id,
            quantity=item["quantity"],
            subtotal=item["subtotal"]
        )
        db.add(nuevo_item)
    db.commit()

    pdf_dir = "pdf_files"
    filename = f"cotizacion_{nueva_cotizacion.id}_{client_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(pdf_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A252C")
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=2,
        textColor=colors.HexColor("#0056b3")
    )

    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )

    # 1. ENCABEZADO CON LOGOTIPO AJUSTADO Y PROPORCIONAL
    logo_path = os.path.join("uploads", "company_logo.png")
    if os.path.exists(logo_path):
        logo = RLImage(logo_path)
        
        orig_w = logo.imageWidth or 100
        orig_h = logo.imageHeight or 100
        max_size = 40  
        
        if orig_w > orig_h:
            logo.drawWidth = max_size
            logo.drawHeight = max_size * (orig_h / orig_w)
        else:
            logo.drawHeight = max_size
            logo.drawWidth = max_size * (orig_w / orig_h)

        company_text = Paragraph(f"<b>{comp_config['name']}</b><br/><font size=8 color='#555555'>{comp_config['address']} &bull; Tel: {comp_config['phone']}</font>", cell_style)
        
        left_header_table = Table([[logo, company_text]], colWidths=[logo.drawWidth + 10, 322 - logo.drawWidth])
        left_header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        company_col = left_header_table
    else:
        company_col = Paragraph(f"<b>{comp_config['name']}</b><br/><font size=8 color='#555555'>{comp_config['address']} &bull; Tel: {comp_config['phone']}</font>", title_style)

    cot_title_html = f"<b>COTIZACIÓN</b><br/><font size=10 color='#444444'>N° {current_cot_num}</font>"

    header_table = Table([
        [company_col, Paragraph(cot_title_html, subtitle_style)]
    ], colWidths=[332, 210])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#0056b3")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # 2. BLOQUES DE CLIENTE Y DETALLES DE OFERTA
    cliente_info = f"<b>CLIENTE</b><br/><br/><b>Nombre:</b> {client_name}<br/><b>Teléfono:</b> {client_phone if client_phone else 'N/A'}<br/><b>Ubicación:</b> {client_address}"
    oferta_info = f"<b>DETALLES DE OFERTA</b><br/><br/><b>Fecha de Emisión:</b> {datetime.datetime.now().strftime('%d/%m/%Y')}<br/><b>Validez de Oferta:</b> {comp_config.get('validez_oferta', '5 días')}"

    info_table = Table([
        [Paragraph(cliente_info, cell_style), Paragraph(oferta_info, cell_style)]
    ], colWidths=[271, 271])
    
    info_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#BCE8F1")),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#F9FBFB")),
        ('BOX', (1,0), (1,0), 0.5, colors.HexColor("#BCE8F1")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#F9FBFB")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # 3. TABLA DE PRODUCTOS / SERVICIOS
    table_data = [["CANT.", "DESCRIPCIÓN DEL PRODUCTO / SERVICIO", "P. UNITARIO", "TOTAL"]]
    for item in items_data:
        desc_text = f"<b>{item['name']}</b>"
        if item.get("description"):
            desc_text += f"<br/><font size=8 color='#666'>• {item['description']}</font>"
        
        table_data.append([
            str(item["quantity"]),
            Paragraph(desc_text, cell_style),
            f"${item['price']:.2f}",
            f"${item['subtotal']:.2f}"
        ])

    t = Table(table_data, colWidths=[40, 332, 85, 85])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A252C")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t)

    # 4. TOTALES
    totales_data = [
        ["", "", "Subtotal:", f"${subtotal_general:.2f}"]
    ]
    if apply_iva:
        totales_data.append(["", "", "IVA (13%):", f"${iva_amount:.2f}"])
    
    totales_data.append(["", "", "Total a Pagar:", f"${total_general:.2f}"])

    t_totales = Table(totales_data, colWidths=[40, 332, 85, 85])
    t_totales.setStyle(TableStyle([
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (2,-1), (3,-1), colors.HexColor("#0056b3")),
        ('TEXTCOLOR', (2,-1), (3,-1), colors.whitesmoke),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_totales)
    elements.append(Spacer(1, 20))

    # 5. TÉRMINOS, CONDICIONES Y GARANTÍAS
    cond_pago = comp_config.get('condiciones_pago', '')
    validez = comp_config.get('validez_oferta', '')
    garantias = comp_config.get('garantias_texto', '')
    instalacion = comp_config.get('instalacion_nota', '')

    garantias_formatted = garantias.replace('\n', '<br/>&bull; ')

    terms_html = f"""
    <b>TÉRMINOS, CONDICIONES Y FORMAS DE PAGO</b><br/><br/>
    &bull; <b>Condición de pago:</b> {cond_pago}<br/>
    &bull; <b>Validez de la cotización:</b> Esta oferta es válida por {validez} a partir de la fecha de emisión.<br/>
    &bull; <b>Garantía:</b> {garantias_formatted}<br/>
    &bull; <b>Instalación:</b> {instalacion}
    """

    terms_table = Table([[Paragraph(terms_html, cell_style)]], colWidths=[542])
    terms_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#0056b3")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FBFB")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(terms_table)

    doc.build(elements)

    nueva_cotizacion.pdf_path = filepath
    db.commit()

    return FileResponse(filepath, media_type='application/pdf', filename=filename)
