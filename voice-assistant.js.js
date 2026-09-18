/**
 * Sistema de Asistente de Voz Inteligente
 * Usa Web Speech API + Backend con Google Gemini
 */

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.currentContext = {};
        
        this.initSpeechRecognition();
        this.initUI();
    }
    
    initSpeechRecognition() {
        // Verificar soporte del navegador
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('Este navegador no soporta reconocimiento de voz');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configuración
        this.recognition.lang = 'es-SV'; // Español de El Salvador
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        
        // Eventos
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUIListening(true);
            console.log('Escuchando...');
        };
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('Transcripción:', transcript);
            
            this.processVoiceCommand(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Error de reconocimiento:', event.error);
            this.updateUIListening(false);
            this.isListening = false;
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUIListening(false);
        };
    }
    
    initUI() {
        // Crear botón flotante de voz
        const voiceButton = document.createElement('div');
        voiceButton.id = 'voice-assistant-btn';
        voiceButton.innerHTML = `
            <button id="voiceBtn" class="voice-btn">
                <i class="fas fa-microphone"></i>
            </button>
            <div id="voiceStatus" class="voice-status">
                <span class="pulse"></span>
                <span class="status-text">Presiona para hablar</span>
            </div>
        `;
        document.body.appendChild(voiceButton);
        
        // Event listener
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleListening();
        });
        
        // Agregar estilos
        this.injectStyles();
    }
    
    toggleListening() {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.startListening();
        }
    }
    
    startListening() {
        // Actualizar contexto antes de escuchar
        this.updateContext();
        
        try {
            this.recognition.start();
        } catch (e) {
            console.error('Error al iniciar reconocimiento:', e);
        }
    }
    
    updateContext() {
        // Recopilar contexto de la página actual
        this.currentContext = {
            current_page: this.getCurrentPage(),
            products: this.getAvailableProducts(),
            current_quotation: this.getCurrentQuotation()
        };
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('productos')) return 'productos';
        if (path.includes('cotizaciones')) return 'cotizaciones';
        if (path.includes('configuracion')) return 'configuracion';
        if (path.includes('dashboard')) return 'dashboard';
        return 'general';
    }
    
    getAvailableProducts() {
        // Extraer productos de la tabla si existe
        const productRows = document.querySelectorAll('table tbody tr');
        const products = [];
        
        productRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 3) {
                products.push({
                    name: cells[0].textContent.trim(),
                    price: parseFloat(cells[1].textContent.replace('$', '').trim())
                });
            }
        });
        
        return products;
    }
    
    getCurrentQuotation() {
        // Leer datos del formulario de cotización si existe
        const quotationData = {};
        
        const clientName = document.getElementById('client_name');
        if (clientName) quotationData.client_name = clientName.value;
        
        // Agregar más campos según necesites
        
        return quotationData;
    }
    
    async processVoiceCommand(transcript) {
        // Mostrar transcripción
        this.showTranscript(transcript);
        
        try {
            // Enviar al backend
            const formData = new FormData();
            formData.append('transcript', transcript);
            formData.append('context', JSON.stringify(this.currentContext));
            
            const response = await fetch('/voice-command', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Mostrar respuesta
                this.showResponse(result.text);
                
                // Reproducir audio de respuesta
                if (result.audio_url) {
                    this.playAudio(result.audio_url);
                } else {
                    this.speakText(result.text);
                }
                
                // Ejecutar acción si existe
                if (result.action) {
                    this.executeAction(result.action, result.action_params);
                }
            } else {
                this.showError(result.error);
                this.speakText(result.error);
            }
            
        } catch (error) {
            console.error('Error al procesar comando:', error);
            this.showError('Error al procesar tu solicitud');
        }
    }
    
    speakText(text) {
        // Usar Web Speech Synthesis API
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        this.synthesis.speak(utterance);
    }
    
    playAudio(audioUrl) {
        const audio = new Audio(audioUrl);
        audio.play();
    }
    
    showTranscript(text) {
        this.showNotification(text, 'user');
    }
    
    showResponse(text) {
        this.showNotification(text, 'assistant');
    }
    
    showError(text) {
        this.showNotification(text, 'error');
    }
    
    showNotification(text, type) {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = `voice-notification voice-notification-${type}`;
        notification.textContent = text;
        
        document.body.appendChild(notification);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    executeAction(action, params) {
        // Ejecutar acciones específicas en el frontend
        console.log('Ejecutando acción:', action, params);
        
        // Por ejemplo, recargar lista de productos si se creó uno nuevo
        if (action === 'crear_producto' || action === 'agregar_producto_cotizacion') {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    }
    
    updateUIListening(isListening) {
        const btn = document.getElementById('voiceBtn');
        const status = document.getElementById('voiceStatus');
        
        if (isListening) {
            btn.classList.add('listening');
            status.querySelector('.status-text').textContent = 'Escuchando...';
            status.classList.add('active');
        } else {
            btn.classList.remove('listening');
            status.querySelector('.status-text').textContent = 'Presiona para hablar';
            status.classList.remove('active');
        }
    }
    
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #voice-assistant-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9999;
            }
            
            .voice-btn {
                width: 70px;
                height: 70px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                font-size: 30px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
            }
            
            .voice-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            .voice-btn.listening {
                animation: pulse 1.5s infinite;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .voice-status {
                position: absolute;
                bottom: 80px;
                right: 0;
                background: white;
                padding: 10px 20px;
                border-radius: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                opacity: 0;
                transition: opacity 0.3s;
                white-space: nowrap;
            }
            
            .voice-status.active {
                opacity: 1;
            }
            
            .voice-status .pulse {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #f5576c;
                margin-right: 10px;
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.3; }
            }
            
            .voice-notification {
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                padding: 15px 30px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                z-index: 10000;
                max-width: 500px;
                animation: slideDown 0.3s ease;
            }
            
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateX(-50%) translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
            
            .voice-notification-user {
                border-left: 4px solid #667eea;
            }
            
            .voice-notification-assistant {
                border-left: 4px solid #48bb78;
            }
            
            .voice-notification-error {
                border-left: 4px solid #f56565;
            }
        `;
        document.head.appendChild(style);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.voiceAssistant = new VoiceAssistant();
});
