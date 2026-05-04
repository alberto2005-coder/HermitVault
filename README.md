# 🛡️ HermitVault - Professional Offline Password Manager (v2.0)

![HermitVault Logo](logo.png)

**HermitVault** es un gestor de contraseñas local, offline y de alta seguridad diseñado para usuarios que priorizan la privacidad absoluta. Con una interfaz web-moderna basada en arquitectura Glassmorphism, HermitVault ofrece una experiencia premium sin comprometer la seguridad.

---

## ✨ Características Destacadas

### 🔒 Seguridad de Grado Militar
- **"Zero Knowledge" Architecture:** Tu contraseña maestra nunca se guarda. Se utiliza exclusivamente para derivar la clave de cifrado en memoria mediante PBKDF2 y AES-256.
- **Análisis Pro (zxcvbn):** Análisis de entropía de nivel profesional que detecta patrones, repeticiones y palabras del diccionario en tiempo real.
- **Protección Anti-Brute-Force:** Sistema de bloqueo progresivo con retardo exponencial y persistencia entre reinicios mediante archivos de estado ofuscados.
- **Verificación Humana (Slide to Verify):** Deslizador dinámico con objetivo aleatorio para prevenir ataques automatizados.

### 🔄 Sincronización e Interoperabilidad
- **Sincronización P2P Avanzada:** Sincronización directa entre dispositivos en la misma red local con fusión inteligente de datos y control de puertos personalizable.
- **Importación desde Navegadores:** Migra tus contraseñas desde **Chrome, Edge, Firefox** o archivos de texto genéricos con un solo clic. Soporta formatos `.csv` y `.txt`.
- **Exportación a Excel:** Genera informes detallados de tus credenciales para auditorías personales.

### 🎨 Experiencia de Usuario Premium
- **Diseño Glassmorphism:** Interfaz ultra-moderna con efectos de desenfoque, degradados y micro-animaciones.
- **Modo Claro/Oscuro:** Soporte nativo para temas con persistencia de preferencias.
- **Organización por Carpetas:** Clasifica tus secretos (contraseñas y notas) en contextos como "Trabajo", "Personal" o "Finanzas".
- **Notas Seguras:** Almacenamiento cifrado de texto libre integrado en el flujo de trabajo global.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.13+ (Core Logic & Security)
- **Frontend:** HTML5, Tailwind CSS, JavaScript (ES6+)
- **GUI Bridge:** [pywebview](https://pywebview.flowrl.com/)
- **Criptografía:** [cryptography.io](https://cryptography.io/en/latest/) (AES-256 Fernet)
- **Análisis de Seguridad:** [zxcvbn](https://github.com/dropbox/zxcvbn)
- **Procesamiento de Datos:** Pandas & Openpyxl

---

## 🚀 Instalación y Despliegue

### 💻 Para Usuarios (Instalador Windows)
Si eres un usuario final, lo más sencillo es utilizar el instalador profesional generado con Inno Setup:
1. Descarga el archivo `HermitVault_Setup.exe` (si está disponible en Releases).
2. Sigue el asistente de instalación.
3. La aplicación se instalará en `Program Files` y tus datos se guardarán de forma persistente y segura en `%USERPROFILE%\HermitVault`.

### 👨‍💻 Para Desarrolladores
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

---

## 📦 Generación de Binarios y Distribución

El proyecto incluye herramientas automatizadas para crear versiones distribuibles:

### 1. Crear el Ejecutable (.EXE)
Ejecuta el archivo `build_exe.bat`. Este script realizará lo siguiente:
- Instalará/actualizará todas las dependencias necesarias.
- Utilizará PyInstaller para empaquetar el código, los activos web y las librerías críticas (`zxcvbn`, `pandas`) en un único archivo independiente en la carpeta `dist/`.

### 2. Crear el Instalador de Windows
Utiliza el archivo `installer_script.iss` con **Inno Setup**:
- Genera un instalador profesional con iconos personalizados.
- Configura los accesos directos y los metadatos del autor.
- Asegura que la desinstalación sea limpia pero mantenga tus datos cifrados a salvo.

---

## 🔒 Arquitectura de Almacenamiento

HermitVault utiliza un sistema de almacenamiento persistente para garantizar que no pierdas tus datos al actualizar la aplicación:
- **Directorio de Datos:** `%USERPROFILE%\HermitVault` (en Windows).
- **Archivos `.vault`:** Contenedores cifrados con AES-256 que almacenan tus credenciales.
- **Archivo `.cache.dat`:** Estado de seguridad y bloqueo anti-fuerza bruta.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
Desarrollado con ❤️ por [Alberto](https://github.com/alberto2005-coder)
