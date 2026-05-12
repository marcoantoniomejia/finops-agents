# 📜 GEMINI.md: Estándar de Desarrollo Web & SEO (Plantilla Maestra)

Este documento define la arquitectura, convenciones y estándares de calidad para el desarrollo de Landing Pages y Sitios Web de Alto Impacto. Diseñado para ser reutilizado como la "verdad absoluta" en nuevos proyectos.

---

## 1. 🎯 Objetivos del Proyecto (Personalizar por Proyecto)

- **Nombre del Proyecto:** [NOMBRE_DEL_PROYECTO]
- **Misión:** Crear una presencia digital autoritaria, estética y performante.
- **Público Objetivo:** [DEFINIR_TARGET, ej: Empresarios, Clientes Premium, etc.]
- **Conversión:** [DEFINIR_KPI, ej: Formulario de Contacto, Suscripción, Venta]

---

## 2. 🛠️ Stack Tecnológico (Filosofía "Cero Dependencias")

Priorizamos el rendimiento nativo y la mantenibilidad a largo plazo sobre frameworks pesados.

- **Frontend:**
  - **HTML5:** Semántico y accesible.
  - **CSS3:** Vanilla con Arquitectura de Variables (Custom Properties) y metodología BEM.
  - **JavaScript:** Vanilla ES6+ (Sin jQuery, React o Vue para sitios estáticos).
- **Assets:**
  - Iconos: FontAwesome (vía CDN o local optimizado).
  - Fuentes: Google Fonts (Carga asíncrona optimizada).
- **Infraestructura:**
  - **Docker:** Contenedor Nginx Alpine para servir contenido estático.
  - **Cloud:** Google Cloud Run (Serverless).

---

## 3. 📂 Estructura de Directorios Estándar

```text
/
├── .agent/             # Workflows y reglas del agente AI
├── src/                # Código Fuente Web
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css       # Único archivo CSS (con @import si es necesario, pero preferible unificado)
│   │   ├── js/
│   │   │   └── main.js         # Lógica JS unificada (Nav, Form, Animaciones)
│   │   ├── images/             # Imágenes optimizadas (WebP preferido)
│   │   └── videos/
│   ├── _header.html    # Server Side Include (SSI) para Header
│   ├── _footer.html    # Server Side Include (SSI) para Footer
│   ├── index.html      # Landing Page Principal
│   ├── 404.html        # Página de Error
│   ├── sitemap.xml     # Mapa del sitio
│   └── robots.txt      # Reglas de indexación
├── Dockerfile          # Configuración de build Nginx
├── nginx.conf          # Configuración del servidor (Gzip, Cache, Security Headers)
└── README.md           # Documentación específica del proyecto
```

---

## 4. 🎨 Sistema de Diseño "Premium" (CSS Architecture)

Todo proyecto debe iniciar definiendo el sistema de variables en `:root`.

### 4.1 Variables CSS Esenciales

- **Paleta:** `--color-primario`, `--color-secundario`, `--color-acento`, `--color-texto`.
- **Gradientes:** `--gradient-primary`, `--gradient-gold` (o acento correspondiente).
- **Tipografía:** `--font-principal` (Cuerpo), `--font-secundaria` (Títulos).
- **Espaciado:** `--space-xs` a `--space-xl`.
- **Efectos (The "Juice"):**
  - `--shadow-premium-sm/md/lg`: Sombras suaves y difusas.
  - `--transition-smooth`: `all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`.

### 4.2 Efectos Visuales Obligatorios

1.  **Glassmorphism:** En Headers y Modales (`backdrop-filter: blur()`).
2.  **Scroll Reveal:** Elementos entran con `opacity: 0` -> `1` y `translateY` al hacer scroll.
3.  **Hover States:** Feedback visual inmediato (elevación, brillo, cambio de borde).
4.  **Micro-interacciones:** Botones con efectos de shimmer o glow.

---

## 5. 🔎 SEO Técnico Avanzado (Zero Compromise)

El SEO no es un afterthought, es la base del desarrollo.

### 5.1 Metadatos Base

- **Title:** `[Palabra Clave Principal] | [Nombre Marca]` (aprox 60 caracteres).
- **Description:** Única por página, persuasiva, incluye CTA (aprox 155 caracteres).
- **Canonical:** Autoreferencial obligatoria `<link rel="canonical" href="...">`.
- **Robots:** `index, follow` por defecto.

### 5.2 Datos Estructurados (JSON-LD)

Implementar en `<head>` de cada página relevante:

- **LocalBusiness/Organization:** En `index.html` y `contacto`.
- **BreadcrumbList:** En todas las páginas internas.
- **Article:** En páginas de blog.
- **FAQPage:** Si hay sección de preguntas frecuentes.

### 5.3 Open Graph & Twitter Cards

Etiquetas `og:title`, `og:description`, `og:image`, `og:type` configuradas para compartir en redes sociales de forma atractiva.

---

## 6. ⚡ Performance & Core Web Vitals

### 6.1 Imágenes

- Uso de formatos modernos (**WebP**) donde sea posible.
- Atributo `loading="lazy"` en todas las imágenes bajo el "fold".
- Dimensiones explícitas `width` y `height` para evitar **CLS** (Cumulative Layout Shift).

### 6.2 Fuentes (Typography)

- **Preconnect:** A `fonts.googleapis.com` y `fonts.gstatic.com`.
- **Async Loading:** Carga con `media="print" onload="this.media='all'"` para evitar bloqueo de renderizado.
- **Display Swap:** `&display=swap` en la URL de la fuente.

### 6.3 Scripts

- `defer` en scripts no críticos (`main.js`).
- Scripts de terceros (Analytics, Chat) diferidos hasta interacción del usuario o `window.onload`.

---

## 7. ♿ Accesibilidad (A11y - WCAG 2.1 AA)

- **Contraste:** Ratio mínimo de 4.5:1 para texto normal.
- **Semántica:** Uso correcto de `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`.
- **Navegación:** Focus visible (`outline`) y orden lógico de tabulación.
- **Multimedia:** Atributos `alt` descriptivos en todas las imágenes.
- **Formularios:** Etiquetas `<label>` explícitas asociadas a inputs.

---

## 8. 🚀 Workflow de Despliegue (Docker + Cloud Run)

### 8.1 Dockerfile Estándar

```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY src/ /usr/share/nginx/html/
# Opcional: Pasos de minificación aquí si no se hacen pre-build
```

### 8.2 Nginx.conf (Optimizado)

- Habilitar **Gzip Compression**.
- Configurar **Cache-Control** agresivo para assets estáticos (imágenes, css, js).
- Configurar **Security Headers** (X-Frame-Options, X-Content-Type-Options).
- Manejo de errores 404 personalizados.

---

## 9. 🔄 Mantenimiento y Evolución

Al crear una nueva página para el proyecto, seguir este checklist:

1.  [ ] Crear HTML con estructura semántica base.
2.  [ ] Definir Metadatos y Canonical.
3.  [ ] Añadir JSON-LD específico.
4.  [ ] Aplicar clases de utilidad del Sistema de Diseño (`.container`, `.grid`, `.text-justify`, `.btn`).
5.  [ ] Integrar clases de animación (`.animate-on-scroll`).
6.  [ ] Validar en Lighthouse (Mobile/Desktop) buscando >95 en todas las métricas.
