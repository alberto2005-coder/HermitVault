# 🛡️ HermitVault - Offline Password Manager (v2.0)

![HermitVault Logo](logo.png)

**HermitVault** es un gestor de contraseñas local, offline y de alta seguridad diseñado para usuarios que priorizan la privacidad absoluta. Con una interfaz web-moderna basada en arquitectura Glassmorphism, HermitVault ofrece una experiencia premium sin comprometer la seguridad.

## ✨ Características Principales

- **Seguridad "Zero Knowledge":** Tu contraseña maestra nunca se guarda. Se utiliza exclusivamente para derivar la clave de cifrado en memoria mediante PBKDF2 y AES-256.
- **Sistema de Papelera (Trash):** Protección contra borrados accidentales. Restaura tus credenciales o elimínalas permanentemente.
- **🧙 Generador Avanzado:** Panel de creación de contraseñas con control granular sobre longitud, mayúsculas, números y símbolos.
- **📊 Medidor de Fortaleza (zxcvbn):** Análisis de entropía de nivel profesional que detecta patrones, repeticiones y palabras del diccionario en tiempo real.
- **🎨 Personalización Premium:** Soporte para iconos personalizados por servicio (favicon) y estética ultra-moderna con Glassmorphism.
- **💾 Backup & Importación:** Exporta tu bóveda completa a un archivo de respaldo cifrado o importa bóvedas existentes de forma sencilla.
- **🛡️ Protección Anti-Brute-Force:** Sistema de bloqueo progresivo con retardo exponencial y persistencia entre reinicios.
- **🧩 Verificación Humana (Slide to Verify):** Deslizador dinámico con objetivo aleatorio para prevenir ataques automatizados y bots locales.
- **📉 Exportación a Excel:** Genera informes de tus credenciales de forma rápida y sencilla.
- **🔐 Cambio de Master Password:** Re-cifrado completo de la bóveda al cambiar la contraseña maestra, impidiendo el uso de la contraseña anterior.
- **👁️ Visibilidad Controlada:** Alterna la visualización de contraseñas en cualquier campo.
- **🔄 Sincronización P2P:** Sincronización directa entre dispositivos en la misma red local con fusión inteligente de datos.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.10+
- **Frontend:** HTML5, Tailwind CSS, JavaScript (ES6+)
- **GUI Bridge:** [pywebview](https://pywebview.flowrl.com/)
- **Criptografía:** [cryptography.io](https://cryptography.io/en/latest/) (Fernet/AES)
- **Análisis de Seguridad:** [zxcvbn](https://github.com/dropbox/zxcvbn)
- **Procesamiento de Datos:** Pandas & Openpyxl (para exportación Excel)

## 🚀 Instalación y Uso

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/alberto2005-coder/HermitVault.git
   cd HermitVault
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python main.py
   ```

### 📦 Generar Ejecutable (.EXE)

Si quieres generar un archivo `.exe` para usar HermitVault sin necesidad de Python:

1. Ejecuta el archivo `build_exe.bat` incluido en la carpeta raíz.
2. Espera a que PyInstaller termine el proceso.
3. Encontrarás tu ejecutable listo para usar en la carpeta `dist/`.

## 🔒 Arquitectura de Seguridad

Los datos se almacenan en archivos binarios `.vault`. El archivo tiene la siguiente estructura:
1. Primeros 16 bytes: **Salt** criptográfico único generado por bóveda.
2. Resto del archivo: **Payload cifrado** con AES-256 (CBC/GCM) que contiene el JSON de credenciales y papelera.

Para prevenir ataques de diccionario locales, HermitVault mantiene un archivo de estado de seguridad ofuscado (`.cache.dat`) que rastrea los intentos fallidos e impone bloqueos temporales persistentes, incluso tras reiniciar la aplicación.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🛠️ Próximas Mejoras (Roadmap)

- [ ] **Importación desde Navegadores:** Importar automáticamente desde archivos CSV de Chrome, Edge y Firefox.
- [ ] **Categorización por Carpetas:** Organización avanzada de items mediante etiquetas o directorios virtuales.
- [ ] **Autobloqueo por Inactividad:** Bloqueo automático de la bóveda tras X minutos de inactividad.
- [ ] **Soporte para Notas Seguras:** Almacenamiento de texto libre cifrado más allá de simples credenciales.

---
Desarrollado con ❤️ por [Alberto](https://github.com/alberto2005-coder)
