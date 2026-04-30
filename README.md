# 🛡️ HermitVault - Offline Password Manager

![HermitVault Logo](logo.png)

**HermitVault** es un gestor de contraseñas local, offline y de alta seguridad diseñado para usuarios que priorizan la privacidad absoluta. No hay nubes, no hay servidores externos; tus datos nunca salen de tu máquina.

## ✨ Características Principales

- **Seguridad "Zero Knowledge":** Tu contraseña maestra nunca se guarda. Se utiliza exclusivamente para derivar la clave de cifrado en memoria.
- **Criptografía de Grado Militar:**
  - **KDF:** PBKDF2HMAC con SHA256 y **480,000 iteraciones**.
  - **Cifrado:** Fernet (AES-128 en modo CBC/GCM con HMAC para autenticación).
  - **Salt:** Generación de salt aleatorio único por bóveda.
- **Interfaz Moderna:** Desarrollado con `CustomTkinter` para una experiencia visual premium en modo oscuro.
- **🧙 Generador de Contraseñas:** Crea contraseñas aleatorias criptográficamente fuertes con longitud y caracteres personalizables.
- **📊 Medidor de Fortaleza:** Validación en tiempo real de la seguridad de tus contraseñas manuales.
- **👁️ Visibilidad Controlada:** Alterna la visualización de contraseñas con un solo clic.
- **📋 Portapapeles Seguro:** Botones dedicados para copiar usuario/contraseña sin mostrarlos en pantalla.

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Criptografía:** [cryptography.io](https://cryptography.io/en/latest/)
- **Imágenes:** Pillow (PIL)
- **Portapapeles:** Pyperclip

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

## 🔒 Arquitectura de Seguridad

Los datos se almacenan en un archivo binario `vault.vault`. El archivo tiene la siguiente estructura:
1. Primeros 16 bytes: **Salt** aleatorio.
2. Resto del archivo: **Payload cifrado** (JSON con credenciales).

Incluso si alguien obtiene acceso a tu archivo `.vault`, necesitaría romper 480,000 iteraciones de PBKDF2 para intentar un ataque de fuerza bruta contra tu contraseña maestra.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
Desarrollado con ❤️ por [Alberto](https://github.com/alberto2005-coder)
