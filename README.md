# 🛡️ HermitVault - Professional Offline Password Manager (v2.0)

![HermitVault Logo](logo.png)

**HermitVault** es un gestor de contraseñas local, offline y de alta seguridad diseñado para usuarios que priorizan la privacidad absoluta. Con una interfaz web moderna basada en arquitectura Glassmorphism y un backend robusto en Python, la aplicación mantiene tus secretos bajo tu control en todo momento.

---

## ✨ Características Destacadas

### 🔒 Seguridad de Grado Militar
- **Arquitectura "Zero Knowledge"**: Tu contraseña maestra nunca se guarda. Se utiliza exclusivamente para derivar la clave de cifrado en memoria mediante PBKDF2 y AES-256.
- **Análisis Pro (zxcvbn)**: Análisis de entropía profesional que detecta patrones, repeticiones y palabras del diccionario en tiempo real.
- **Protección Anti-Brute-Force**: Bloqueo progresivo con retardos exponenciales y persistencia entre reinicios mediante archivos de estado ofuscados.
- **Verificación Humana (Slide to Verify)**: Deslizador dinámico con objetivo aleatorio para prevenir ataques automatizados.

### 🔄 Sincronización e Interoperabilidad
- **Sincronización P2P Avanzada**: Sincronización directa entre dispositivos en la misma red local con fusión inteligente de datos y control de puertos personalizable.
- **Importación desde Navegadores**: Migra tus contraseñas desde **Chrome, Edge, Firefox** o archivos de texto genéricos con un solo clic. Soporta formatos `.csv` y `.txt`.
- **Exportación a Excel**: Genera informes detallados de tus credenciales para auditorías personales.

### 🎨 Experiencia de Usuario Premium
- **Diseño Glassmorphism**: Interfaz ultra-moderna con efectos de desenfoque, degradados y micro-animaciones.
- **Modo Claro/Oscuro**: Soporte nativo para temas con persistencia de preferencias.
- **Organización por Carpetas**: Clasifica tus secretos (contraseñas y notas) en contextos como "Trabajo", "Personal" o "Finanzas".
- **Notas Seguras**: Almacenamiento cifrado de texto libre integrado en el flujo de trabajo global.

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
- **Directorio de Datos:** `%USERPROFILE%\HermitVault` (Windows).
- **Archivos `.vault`:** Contenedores cifrados con AES-256 que almacenan tus credenciales.
- **Archivo `.cache.dat`:** Estado de seguridad y bloqueo anti-fuerza bruta.

---

## 🛡️ Auditoría y Mitigación de Vulnerabilidades (Mayo 2026)

En mayo de 2026, el código de **HermitVault** se sometió a una exhaustiva auditoría de seguridad para elevarlo de un prototipo de desarrollo a un estándar de grado de producción altamente seguro.

Se identificaron y mitigaron por completo las siguientes 12 vulnerabilidades críticas de seguridad y estabilidad:

### 1. Autenticación Robusta en Sincronización P2P
* **Vulnerabilidad:** El servidor de sincronización escuchaba en todas las interfaces (`0.0.0.0`) y transmitía el archivo `.vault` cifrado a cualquier dispositivo que se conectara al puerto, sin una verificación apropiada de identidad.
* **Solución:** Se implementó un flujo de **emparejamiento con PIN aleatorio de 6 dígitos**. El servidor anfitrión genera un código PIN de un solo uso criptográficamente seguro y lo muestra al solicitante, asegurando que solo el dispositivo correcto pueda sincronizarse.

### 2. Prevención de Inyección HTML y Cross-Site Scripting (XSS)
* **Vulnerabilidad:** El renderizado de tarjetas de credenciales y carpetas en el WebView utilizaba interpolaciones directas con `innerHTML` sobre entradas de usuario no sanitizadas (título, usuario, notas, etc.).
* **Solución:** Se implementó una función de sanitización global `escapeHtml()` en el frontend. Se eliminó la inyección directa de texto no sanitizado y se restringieron los manejadores de eventos a alternativas seguras.

### 3. Cero Exposición de Credenciales en Memoria JS/DOM
* **Vulnerabilidad:** Las llamadas del bridge `get_all_items()` y `get_credentials()` entregaban la base de datos completamente descifrada, incluyendo contraseñas en texto plano, al contexto JS.
* **Solución:** Se adoptó una arquitectura de **descifrado bajo demanda**. Las llamadas del bridge ahora devuelven contraseñas enmascaradas (`••••••••`) por defecto y permiten acceso seguro por elemento para visualización.

### 4. Mitigación de Path Traversal en Creación/Carga de Vaults
* **Vulnerabilidad:** La concatenación directa de `vault_name` permitía realizar Path Traversal (por ejemplo `../../archivo`), permitiendo leer y escribir archivos arbitrarios fuera del directorio previsto.
* **Solución:** Se implementó el helper `sanitize_vault_name()` en `vault_storage.py` y `bridge.py` que elimina secuencias peligrosas (`..`, `/`, `\`) y aplica un criterio estricto de nombres permitidos.

### 5. Funcionamiento 100% Offline (Independencia de CDNs)
* **Vulnerabilidad:** La aplicación cargaba hojas de estilo de Tailwind CSS, fuentes de Google Fonts, iconos de Material Symbols y librerías de seguridad desde CDNs, lo que rompa el uso offline y añadía dependencias externas.
* **Solución:** Se descargaron y empaquetaron localmente todas las librerías CSS, JavaScript y tipografías directamente en la carpeta `/web`, garantizando que la aplicación cargue al 100% sin internet.

### 6. Criptografía Conforme a Estándares FIPS y OWASP (KDF)
* **Vulnerabilidad:** El cifrado derivaba la clave mediante PBKDF2-HMAC-SHA256 con 480.000 iteraciones, por debajo de las 600.000 recomendadas por OWASP para entornos criptográficos conformes.
* **Solución:** Se aumentaron las iteraciones de la función KDF en `crypto_logic.py` a **600.000**, elevando drásticamente el costo computacional de ataques por fuerza bruta.

### 7. Firmado Criptográfico con UUID de Estado Anti-Fuerza Bruta
* **Vulnerabilidad:** La información de intentos fallidos y bloqueos en `.cache.dat` se guardaba con una simple codificación Base64, lo que permitía a un atacante modificar o borrar ese archivo.
* **Solución:** El archivo de estado `.cache.dat` ahora se **firma digitalmente con un HMAC-SHA256** usando una clave única derivada del identificador de hardware del sistema (UUID del dispositivo), evitando la manipulación del estado de bloqueo.

### 8. Advertencia de Exportación Plaintext a Excel
* **Vulnerabilidad:** La función de exportar a Excel escribía credenciales y contraseñas completas en texto plano en disco sin ninguna advertencia previa.
* **Solución:** Se añadió un **cuadro de confirmación interactivo de alto impacto** que alerta sobre los riesgos de guardar secretos sin cifrar en el disco.

### 9. Escrituras Atómicas contra la Corrupción de Datos
* **Vulnerabilidad:** `save_vault()` escribía directamente sobre el archivo de bóveda activo usando un flujo `open("wb")` síncrono. Si la aplicación se cerraba inesperadamente, el archivo podía quedar corrupto o parcialmente sobrescrito.
* **Solución:** Se implementó una **escritura transaccional atómica**. La aplicación escribe los datos en un archivo temporal seguro (`.tmpvault`) en el mismo directorio y luego renombra el archivo de forma atómica al completarse la escritura.

### 10. Corrección de Rutas en Operaciones de Importación/Backup
* **Vulnerabilidad:** Las funciones `backup_vault()` e `import_vault()` operaban sobre el directorio de trabajo del proceso (`os.getcwd()`) en lugar del directorio de datos configurado centralmente, provocando rutas incorrectas.
* **Solución:** Se reestructuraron todos los accesos a disco para resolverse a través del helper unificado `get_data_dir()`.

### 11. Robustez del Protocolo de Red (DoS y Salt Cryptographic Alignment)
* **Vulnerabilidad:**
  1. `receive_vault()` leía flujos de red acumulando datos recursivamente en memoria según la cabecera de tamaño recibida de 4 bytes, exponiendo la aplicación a ataques DoS.
  2. Al sincronizarse, el cliente intentaba descifrar la base de datos remota usando la sal local del sistema, lo que rompía la sincronización entre dispositivos.
* **Solución:**
  1. Se limitó el tamaño máximo del flujo de red a **50 MB** y se añadieron **timeouts de red de 15 segundos** en los sockets de lectura.
  2. Se almacenó temporalmente de forma segura la contraseña maestra al abrir la bóveda y se re-derivó la clave de descifrado del cliente usando la **sal específica del servidor remoto**, corrigiendo la sincronización.

### 12. Entornos de Construcción Deterministas y Reproducibles
* **Vulnerabilidad:** El archivo `requirements.txt` usaba operadores abiertos (`>=`) y el instalador instalaba PyInstaller en tiempo real, lo que hacía que los binarios no fueran reproducibles.
* **Solución:** Se congelaron y fijaron todas las dependencias con versiones exactas y estables (`pywebview==5.0.1`, `cryptography==42.0.5`, `pyinstaller==6.5.0`, etc.) en `requirements.txt`, garantizando compilaciones deterministas.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

Desarrollado con ❤️ por [Alberto](https://github.com/alberto2005-coder)

---

# 🛡️ HermitVault - Professional Offline Password Manager (v2.0)

![HermitVault Logo](logo.png)

**HermitVault** is a local, offline, high-security password manager designed for users who prioritize absolute privacy. With a modern web-based interface built on a Glassmorphism architecture and a robust Python backend, the application keeps your data under your complete control—without cloud dependency, without external servers, and without exposing your secrets to third parties.

---

## ✨ Highlighted Features

### 🔒 Military-Grade Security
- **"Zero Knowledge" Architecture:** Your master password is never stored. It is used only to derive the encryption key in memory using PBKDF2 and AES-256.
- **Pro Security Analysis (zxcvbn):** Professional-grade entropy checks that detect repetition patterns, dictionary words, and weak structures in real time.
- **Anti-Brute-Force Protection:** Progressive lockout with exponential delays and persistence across restarts via obfuscated state files.
- **Human Verification (Slide to Verify):** A dynamic slider with a random target to prevent automated attack attempts.

### 🔄 Synchronization and Interoperability
- **Advanced P2P Sync:** Direct synchronization between devices on the same local network with smart data merge logic and configurable port control.
- **Browser Import:** Migrate credentials from **Chrome, Edge, Firefox**, or generic text files with one click. Supports `.csv` and `.txt` formats.
- **Excel Export:** Generate detailed reports of your credentials for personal auditing.

### 🎨 Premium User Experience
- **Glassmorphism Design:** Modern interface with blur effects, gradients, and subtle micro-animations.
- **Light/Dark Mode:** Native support with persistent preference settings.
- **Folder Organization:** Organize secrets (passwords and notes) into contexts like "Work", "Personal", or "Finance".
- **Secure Notes:** Encrypted text storage integrated into the main workflow.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.13+ (Core Logic & Security)
- **Frontend:** HTML5, Tailwind CSS, JavaScript (ES6+)
- **GUI Bridge:** [pywebview](https://pywebview.flowrl.com/)
- **Cryptography:** [cryptography.io](https://cryptography.io/en/latest/) (AES-256 Fernet)
- **Security Analysis:** [zxcvbn](https://github.com/dropbox/zxcvbn)
- **Data Processing:** Pandas & Openpyxl

---

## 🚀 Installation and Deployment

### 💻 For End Users (Windows Installer)
If you are an end user, the easiest route is to use the professional installer generated with Inno Setup:
1. Download the `HermitVault_Setup.exe` file (if available in Releases).
2. Follow the installation wizard.
3. The application will be installed under `Program Files`, and your data will be stored securely and persistently in `%USERPROFILE%\HermitVault`.

### 👨‍💻 For Developers
1. **Clone the repository:**
   ```bash
   git clone https://github.com/alberto2005-coder/HermitVault.git
   cd HermitVault
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📦 Binary Generation and Distribution

The project includes automated tools for generating distributable builds:

### 1. Create the Executable (.EXE)
Run `build_exe.bat`. This script will:
- Install or update all required dependencies.
- Use PyInstaller to package the code, web assets, and critical libraries (`zxcvbn`, `pandas`) into a single standalone file in the `dist/` folder.

### 2. Create the Windows Installer
Use `installer_script.iss` with **Inno Setup**:
- Generates a professional installer with custom icons.
- Configures shortcuts and author metadata.
- Ensures clean uninstallation while keeping encrypted data safe.

---

## 🔒 Storage Architecture

HermitVault uses persistent storage to ensure you do not lose your data during updates:
- **Data Directory:** `%USERPROFILE%\HermitVault` (Windows).
- **`.vault` Files:** AES-256 encrypted containers that store credentials.
- **`.cache.dat` File:** Security state and anti-bruteforce lock information.

---

## 🛡️ Security Audit and Vulnerability Remediation (May 2026)

In May 2026, the code for **HermitVault** underwent a rigorous security audit to elevate it from a development prototype to a production-grade standard.

The following 12 critical vulnerabilities were identified and fully mitigated:

### 1. Robust Authentication in P2P Sync
* **Vulnerability:** The synchronization server listened on all interfaces (`0.0.0.0`) and exposed the encrypted `.vault` file to any device connecting to the port without adequate verification.
* **Solution:** Introduced a **randomized 6-digit PIN pairing flow**. The host server generates a cryptographically secure one-time PIN and shows it to the requester, ensuring that only the intended device can sync.

### 2. Prevention of HTML Injection and Cross-Site Scripting (XSS)
* **Vulnerability:** Credential and folder card rendering in the WebView used direct `innerHTML` interpolation on unsanitized user input (title, username, notes, and more).
* **Solution:** Added a global `escapeHtml()` sanitization function in the frontend. Direct injection of unsanitized text was removed, and handlers were restricted to safe alternatives.

### 3. Zero Exposure of Credentials in JS Memory / DOM
* **Vulnerability:** Bridge calls such as `get_all_items()` and `get_credentials()` returned the full decrypted database—including plaintext passwords—to the JS context.
* **Solution:** Implemented a **decrypt-on-demand** architecture. The bridge now returns masked passwords (`••••••••`) by default and exposes secure per-item retrieval for display-only access.

### 4. Mitigation of Path Traversal in Vault Creation / Loading
* **Vulnerability:** Direct concatenation of `vault_name` allowed Path Traversal attacks such as `../../file`, enabling read/write access outside the intended directory.
* **Solution:** Added `sanitize_vault_name()` in `vault_storage.py` and `bridge.py` to strip dangerous sequences (`..`, `/`, `\`) and enforce strict allowed naming.

### 5. 100% Offline Operation (No CDN Dependency)
* **Vulnerability:** The app loaded Tailwind CSS, Google Fonts, Material Symbols, and password-strength libraries from CDNs, which broke offline use and introduced external trust dependencies.
* **Solution:** All CSS/JS/font assets were downloaded and bundled locally in the `/web` folder so the app works fully offline.

### 6. Cryptography Aligned with FIPS and OWASP KDF Standards
* **Vulnerability:** Encryption derived the key using PBKDF2-HMAC-SHA256 with 480,000 iterations, below the 600,000 recommended by OWASP for compliant cryptographic environments.
* **Solution:** Increased the KDF iteration count in `crypto_logic.py` to **600,000** to significantly raise the cost of brute-force attacks.

### 7. Cryptographic Signed State with Anti-Bruteforce UUID
* **Vulnerability:** Failed attempts and lock state were stored in `.cache.dat` using simple Base64 encoding, which an attacker could modify or delete.
* **Solution:** The state file now uses a **digital signature with HMAC-SHA256** derived from a unique hardware UUID, preventing tampering and preserving lock integrity.

### 8. Plaintext Export Warning for Excel
* **Vulnerability:** Exporting to Excel saved credentials and passwords in plaintext without an upfront warning.
* **Solution:** Added a **high-impact confirmation modal** warning clearly about the risks of storing secrets unencrypted on disk.

### 9. Atomic Writes to Prevent Data Corruption
* **Vulnerability:** `save_vault()` wrote directly over the active vault file using a synchronous `open("wb")` call. If the app crashed or hung mid-write, the file could become corrupted.
* **Solution:** Implemented **atomic transactional writes**. Data is written to a secure temporary file (`.tmpvault`) in the same directory and then atomically renamed when complete.

### 10. Fixing Import/Backup Paths
* **Vulnerability:** `backup_vault()` and `import_vault()` used the process working directory (`os.getcwd()`) instead of the configured data directory, leading to unpredictable writes.
* **Solution:** Centralized all disk access through the unified helper `get_data_dir()`.

### 11. Resilience of the Network Protocol (DoS and Salt Alignment)
* **Vulnerability:**
  1. `receive_vault()` accumulated network data recursively in memory according to the 4-byte header length, risking DoS conditions.
  2. During sync, the client attempted to decrypt the remote database using a local salt derived from the local machine, breaking synchronization compatibility.
* **Solution:**
  1. Limited the maximum network payload to **50 MB** and added **15-second socket read timeouts**.
  2. Stored the master password in secure memory during vault opening and re-derived the decryption key using the **specific remote salt** to keep sync valid.

### 12. Deterministic and Reproducible Build Environments
* **Vulnerability:** `requirements.txt` used open version ranges (`>=`), and the installer installed PyInstaller at runtime, undermining binary reproducibility.
* **Solution:** All dependencies were frozen to exact stable versions (`pywebview==5.0.1`, `cryptography==42.0.5`, `pyinstaller==6.5.0`, etc.) in `requirements.txt` to ensure repeatable builds.

---

## 📄 License

This project is under the MIT License. See the `LICENSE` file for details.

---

Developed with ❤️ by [Alberto](https://github.com/alberto2005-coder)
