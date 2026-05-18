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

## 🛡️ Auditoría y Mitigación de Vulnerabilidades (Mayo 2026)

En mayo de 2026, el código de **HermitVault** se sometió a una exhaustiva auditoría de seguridad para elevarlo de un prototipo de desarrollo a un estándar de grado de producción altamente seguro (escalando de una calificación inicial no apta para MVP a una arquitectura robusta de nivel empresarial). 

Se identificaron y mitigaron por completo las siguientes 12 vulnerabilidades críticas de seguridad y estabilidad:

### 1. Autenticación Robusta en Sincronización P2P
* **Vulnerabilidad:** El servidor de sincronización escuchaba en todas las interfaces (`0.0.0.0`) y transmitía el archivo `.vault` cifrado a cualquier dispositivo que se conectara al puerto, sin token, TLS ni emparejamiento.
* **Solución:** Se implementó un flujo de **emparejamiento con PIN aleatorio de 6 dígitos**. El servidor anfitrión genera un código PIN de un solo uso criptográficamente seguro y lo muestra en pantalla; el cliente debe enviar el PIN correcto para autenticarse antes de que se inicie la transferencia de datos.

### 2. Prevención de Inyección HTML y Cross-Site Scripting (XSS)
* **Vulnerabilidad:** El renderizado de tarjetas de credenciales y carpetas en el WebView utilizaba interpolaciones directas con `innerHTML` sobre entradas de usuario no sanitizadas (título, sitio, usuario, contraseña), permitiendo la inyección de JS malicioso capaz de invocar comandos privilegiados del sistema operativo a través del bridge de Python.
* **Solución:** Se implementó una función de sanitización global `escapeHtml()` en el frontend. Se eliminó la inyección directa de texto no sanitizado, y las acciones en los elementos (como copiar o editar) pasaron a usar referencias por índices seguros (`dataset` y números enteros) en lugar de cadenas de texto crudas.

### 3. Cero Exposición de Credenciales en Memoria JS/DOM
* **Vulnerabilidad:** Las llamadas del bridge `get_all_items()` y `get_credentials()` entregaban la base de datos completamente descifrada (incluyendo contraseñas en texto plano) al contexto JS del frontend, manteniéndolas en la memoria del DOM y exponiéndolas a accesos no autorizados en tiempo de ejecución.
* **Solución:** Arquitectura de **descifrado bajo demanda**. Las llamadas globales del bridge ahora devuelven contraseñas enmascaradas (`••••••••`). Se implementó un endpoint seguro `get_credential_password(index)` en el backend de Python que descifra y entrega individualmente la contraseña **únicamente** cuando el usuario hace clic explícito en "Copiar" o "Editar".

### 4. Mitigación de Path Traversal en Creación/Carga de Vaults
* **Vulnerabilidad:** La concatenación directa de `vault_name` permitía realizar Path Traversal (ej. `../../archivo`) al crear o abrir bóvedas, permitiendo leer y escribir archivos arbitrarios fuera del directorio central de datos.
* **Solución:** Se implementó el helper `sanitize_vault_name()` en `vault_storage.py` y `bridge.py` que remueve secuencias peligrosas (`..`, `/`, `\`) y restringe los nombres estrictamente a nombres de archivos válidos dentro de la carpeta central de datos.

### 5. Funcionamiento 100% Offline (Independencia de CDNs)
* **Vulnerabilidad:** La aplicación cargaba hojas de estilo de Tailwind CSS, fuentes de Google Fonts, iconos de Material Symbols y librerías de fuerza de contraseñas (`zxcvbn.js`) desde CDNs externos, rompiendo la premisa de funcionamiento offline y exponiendo al usuario a posibles ataques de secuestro de red (MITM) o caídas de conexión.
* **Solución:** Se descargaron y empaquetaron localmente todas las librerías CSS, JavaScript y tipografías directamente en la carpeta `/web`, garantizando que la aplicación cargue al 100% de manera aislada y local.

### 6. Criptografía Conforme a Estándares FIPS y OWASP (KDF)
* **Vulnerabilidad:** El cifrado derivaba la clave mediante PBKDF2-HMAC-SHA256 con 480,000 iteraciones, por debajo de las 600,000 recomendadas por OWASP para entornos criptográficos conformes a FIPS en almacenamiento local.
* **Solución:** Se incrementaron las iteraciones de la función KDF en `crypto_logic.py` a **600,000 iteraciones**, incrementando drásticamente el costo computacional de cualquier ataque de fuerza bruta offline.

### 7. Firmado Criptográfico con UUID de Estado Anti-Fuerza Bruta
* **Vulnerabilidad:** La información de intentos fallidos y bloqueos en `.cache.dat` se guardaba con una simple codificación Base64, lo que permitía a un atacante borrar o alterar el archivo para reiniciar instantáneamente los contadores de bloqueo.
* **Solución:** El archivo de estado `.cache.dat` ahora se **firma digitalmente con un HMAC-SHA256 utilizando una clave única derivada del identificador de hardware del sistema (UUID del procesador/placa)**. Cualquier intento de alteración o falta de coincidencia en la firma bloquea defensivamente la interfaz por 60 segundos por seguridad.

### 8. Advertencia de Exportación Plaintext a Excel
* **Vulnerabilidad:** La función de exportar a Excel escribía credenciales y contraseñas completas en texto plano en disco sin ningún tipo de advertencia previa.
* **Solución:** Se añadió un **cuadro de confirmación interactivo de alto impacto (Modal)** que alerta detalladamente sobre los riesgos de seguridad que implica almacenar contraseñas sin cifrar en disco antes de procesar el archivo.

### 9. Escrituras Atómicas contra la Corrupción de Datos
* **Vulnerabilidad:** `save_vault()` escribía directamente sobre el archivo de bóveda activo mediante un flujo `open("wb")` síncrono. Si la aplicación se cerraba inesperadamente, se congelaba el hilo o se cortaba la energía del disco a mitad del proceso, la bóveda completa del usuario se corrompía y se perdía para siempre.
* **Solución:** Se implementó una **escritura transaccional atómica**. La aplicación escribe los datos de la bóveda en un archivo temporal seguro (`.tmpvault`) en el mismo directorio de datos y, una vez completada la escritura de forma exitosa, realiza una sustitución atómica instantánea (`os.replace`) sobre el archivo original.

### 10. Corrección de Rutas en Operaciones de Importación/Backup
* **Vulnerabilidad:** Las funciones `backup_vault()` e `import_vault()` operaban sobre el directorio de trabajo del proceso (`os.getcwd()`) en lugar del directorio de datos configurado centralmente (`~/HermitVault`), lo que provocaba errores fatales o pérdida de archivos según desde dónde se iniciara la aplicación.
* **Solución:** Se reestructuraron todos los accesos a disco para resolver rutas sistemáticamente a través del helper unificado `get_data_dir()`.

### 11. Robustez del Protocolo de Red (DoS y Salt Cryptographic Alignment)
* **Vulnerabilidad:** 
  1. `receive_vault()` leía flujos de red acumulando datos recursivamente en memoria en base a la cabecera de tamaño recibida de 4 bytes sin límites, exponiendo a la aplicación a ataques DoS por agotamiento de memoria.
  2. Al conectarse en sincronización, el cliente intentaba descifrar la base de datos remota usando la clave local derivada con su propia sal local, lo cual rompía la sincronización de cualquier bóveda que utilizara una sal aleatoria distinta (incluso teniendo la misma contraseña maestra).
* **Solución:** 
  1. Se limitó el tamaño máximo de flujo de red a **50 MB** y se establecieron **timeouts de red de 15 segundos** en sockets de lectura.
  2. Se almacenó temporalmente de forma segura en memoria la contraseña maestra ingresada al abrir la bóveda y se re-derivó la clave de descifrado del cliente utilizando la **sal específica de la bóveda remota** recibida, logrando un proceso de descifrado y fusión criptográficamente correcto.

### 12. Entornos de Construcción Deterministas y Reproducibles
* **Vulnerabilidad:** El archivo `requirements.txt` usaba operadores abiertos (`>=`) y el instalador instalaba PyInstaller en tiempo real, lo que rompía la reproducibilidad de los binarios ante actualizaciones de dependencias de terceros.
* **Solución:** Se congelaron y fijaron todas las dependencias con sus versiones exactas y estables (`pywebview==5.0.1`, `cryptography==42.0.5`, `pyinstaller==6.5.0`, etc.) en `requirements.txt` y se adaptó `build_exe.bat` para evitar la instalación dinámica.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
Desarrollado con ❤️ por [Alberto](https://github.com/alberto2005-coder)
