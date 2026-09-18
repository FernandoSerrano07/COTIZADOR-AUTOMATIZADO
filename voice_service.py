import os
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from gtts import gTTS
import tempfile
from datetime import datetime

class VoiceAssistant:
    """Asistente de voz inteligente con Google Gemini"""
    
    def __init__(self, db_session):
        self.db = db_session
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.conversation_history = []
        
    def process_voice_command(self, transcript: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un comando de voz y ejecuta acciones
        
        Args:
            transcript: Texto transcrito del audio
            context: Contexto actual (página, usuario, productos, etc.)
            
        Returns:
            Dict con respuesta, acción a ejecutar, y datos
        """
        
        # Construir prompt contextual para Gemini
        system_prompt = self._build_system_prompt(context)
        
        # Agregar mensaje del usuario
        self.conversation_history.append({
            "role": "user",
            "parts": [transcript]
        })
        
        # Llamar a Gemini con función calling
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=self.conversation_history,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                tools=[self._get_function_declarations()],
            )
        )
        
        # Procesar respuesta
        result = self._parse_gemini_response(response)
        
        # Agregar respuesta del asistente al historial
        self.conversation_history.append({
            "role": "model",
            "parts": [result["response_text"]]
        })
        
        return result
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Construye el prompt del sistema según el contexto"""
        
        base_prompt = """Eres un asistente virtual inteligente para un sistema de cotizaciones llamado COTIZADOR-AUTOMATIZADO de la empresa RECOELECTRIC.

Tu función es ayudar al usuario a realizar operaciones mediante comandos de voz de forma natural y conversacional.

CAPACIDADES:
1. Agregar productos a cotizaciones
2. Crear nuevos productos en el catálogo
3. Modificar información de empresa
4. Consultar cotizaciones existentes
5. Generar cotizaciones completas
6. Buscar productos por nombre o descripción

ESTILO DE CONVERSACIÓN:
- Sé amable, profesional y conciso
- Confirma las acciones antes de ejecutarlas
- Si falta información, pregunta de forma natural
- Usa lenguaje salvadoreño cuando sea apropiado (cliente está en El Salvador)

REGLAS:
- Siempre confirma precios y cantidades
- Para crear productos, necesitas: nombre, precio y descripción
- Para agregar a cotización, necesitas: producto y cantidad
- Números de teléfono salvadoreños tienen formato: +503 XXXX-XXXX
"""
        
        # Agregar contexto específico
        if context.get("current_page"):
            base_prompt += f"\n\nPÁGINA ACTUAL: {context['current_page']}"
        
        if context.get("products"):
            products_list = "\n".join([
                f"- {p['name']} (${p['price']})" 
                for p in context['products'][:10]  # Limitar a 10
            ])
            base_prompt += f"\n\nPRODUCTOS DISPONIBLES:\n{products_list}"
        
        if context.get("current_quotation"):
            base_prompt += f"\n\nCOTIZACIÓN ACTUAL:\n{json.dumps(context['current_quotation'], indent=2)}"
        
        return base_prompt
    
    def _get_function_declarations(self) -> list:
        """Define las funciones que Gemini puede llamar"""
        
        return [
            types.FunctionDeclaration(
                name="agregar_producto_cotizacion",
                description="Agrega un producto existente a la cotización actual",
                parameters={
                    "type": "object",
                    "properties": {
                        "producto_nombre": {
                            "type": "string",
                            "description": "Nombre del producto a agregar"
                        },
                        "cantidad": {
                            "type": "integer",
                            "description": "Cantidad de unidades",
                            "minimum": 1
                        }
                    },
                    "required": ["producto_nombre", "cantidad"]
                }
            ),
            types.FunctionDeclaration(
                name="crear_producto",
                description="Crea un nuevo producto en el catálogo",
                parameters={
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "Nombre del producto"
                        },
                        "precio": {
                            "type": "number",
                            "description": "Precio en dólares",
                            "minimum": 0
                        },
                        "descripcion": {
                            "type": "string",
                            "description": "Descripción del producto"
                        }
                    },
                    "required": ["nombre", "precio"]
                }
            ),
            types.FunctionDeclaration(
                name="actualizar_datos_empresa",
                description="Actualiza información de la empresa",
                parameters={
                    "type": "object",
                    "properties": {
                        "campo": {
                            "type": "string",
                            "enum": ["nombre", "telefono", "direccion", "condiciones_pago", "garantias"],
                            "description": "Campo a actualizar"
                        },
                        "valor": {
                            "type": "string",
                            "description": "Nuevo valor"
                        }
                    },
                    "required": ["campo", "valor"]
                }
            ),
            types.FunctionDeclaration(
                name="buscar_producto",
                description="Busca productos por nombre o descripción",
                parameters={
                    "type": "object",
                    "properties": {
                        "termino": {
                            "type": "string",
                            "description": "Término de búsqueda"
                        }
                    },
                    "required": ["termino"]
                }
            ),
            types.FunctionDeclaration(
                name="generar_cotizacion",
                description="Genera una cotización completa en PDF",
                parameters={
                    "type": "object",
                    "properties": {
                        "cliente_nombre": {
                            "type": "string",
                            "description": "Nombre del cliente"
                        },
                        "cliente_telefono": {
                            "type": "string",
                            "description": "Teléfono del cliente"
                        },
                        "cliente_direccion": {
                            "type": "string",
                            "description": "Dirección del cliente"
                        },
                        "aplicar_iva": {
                            "type": "boolean",
                            "description": "Si se aplica IVA (13%)",
                            "default": False
                        }
                    },
                    "required": ["cliente_nombre"]
                }
            ),
            types.FunctionDeclaration(
                name="consultar_cotizaciones",
                description="Consulta cotizaciones anteriores",
                parameters={
                    "type": "object",
                    "properties": {
                        "filtro": {
                            "type": "string",
                            "description": "Filtro opcional (cliente, fecha, etc.)"
                        }
                    }
                }
            )
        ]
    
    def _parse_gemini_response(self, response) -> Dict[str, Any]:
        """Procesa la respuesta de Gemini"""
        
        result = {
            "response_text": "",
            "action": None,
            "action_params": {},
            "success": True,
            "error": None
        }
        
        # Extraer texto de respuesta
        if hasattr(response, 'text'):
            result["response_text"] = response.text
        
        # Procesar function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call'):
                        fc = part.function_call
                        result["action"] = fc.name
                        result["action_params"] = dict(fc.args)
                        
                        # Ejecutar la acción
                        execution_result = self._execute_action(fc.name, fc.args)
                        
                        if execution_result["success"]:
                            result["response_text"] = execution_result["message"]
                        else:
                            result["success"] = False
                            result["error"] = execution_result["error"]
        
        return result
    
    def _execute_action(self, action_name: str, params: Dict) -> Dict[str, Any]:
        """Ejecuta una acción solicitada por Gemini"""
        
        from models import Product, Quotations, QuotationItem
        import json
        
        try:
            if action_name == "crear_producto":
                producto = Product(
                    name=params["nombre"],
                    price=float(params["precio"]),
                    description=params.get("descripcion", ""),
                    is_active=True
                )
                self.db.add(producto)
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Perfecto, el producto '{params['nombre']}' ha sido creado exitosamente con un precio de ${params['precio']}. ¿Deseas agregarlo a la cotización?"
                }
            
            elif action_name == "agregar_producto_cotizacion":
                # Buscar producto
                producto = self.db.query(Product).filter(
                    Product.name.ilike(f"%{params['producto_nombre']}%"),
                    Product.is_active == True
                ).first()
                
                if not producto:
                    return {
                        "success": False,
                        "error": f"No encontré el producto '{params['producto_nombre']}'. ¿Podrías repetirlo o ser más específico?"
                    }
                
                # Aquí normalmente agregarías a la cotización en sesión
                # Por ahora solo confirmamos
                subtotal = producto.price * params["cantidad"]
                
                return {
                    "success": True,
                    "message": f"Excelente, he agregado {params['cantidad']} unidad(es) de '{producto.name}' a la cotización. Subtotal: ${subtotal:.2f}. ¿Deseas agregar algo más?"
                }
            
            elif action_name == "actualizar_datos_empresa":
                config_file = "company_config.json"
                
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Mapeo de campos
                field_mapping = {
                    "nombre": "name",
                    "telefono": "phone",
                    "direccion": "address",
                    "condiciones_pago": "condiciones_pago",
                    "garantias": "garantias_texto"
                }
                
                config_field = field_mapping.get(params["campo"])
                if config_field:
                    config[config_field] = params["valor"]
                    
                    with open(config_file, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    
                    return {
                        "success": True,
                        "message": f"Perfecto, he actualizado {params['campo']} a: {params['valor']}"
                    }
            
            elif action_name == "buscar_producto":
                productos = self.db.query(Product).filter(
                    Product.name.ilike(f"%{params['termino']}%"),
                    Product.is_active == True
                ).limit(5).all()
                
                if not productos:
                    return {
                        "success": False,
                        "error": f"No encontré productos con '{params['termino']}'"
                    }
                
                lista = "\n".join([f"- {p.name} (${p.price})" for p in productos])
                
                return {
                    "success": True,
                    "message": f"Encontré estos productos:\n{lista}\n¿Cuál deseas agregar?"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Acción no implementada"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al ejecutar la acción: {str(e)}"
            }
    
    def text_to_speech(self, text: str, lang: str = "es") -> str:
        """Convierte texto a audio"""
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Guardar en archivo temporal
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            
            return temp_file.name
        
        except Exception as e:
            print(f"Error en TTS: {e}")
            return None
