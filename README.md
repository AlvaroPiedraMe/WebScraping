# 🤖 WebScraping - Wallapop Furgonetas en Gijón

Este proyecto es un scraper web desarrollado con Python y Playwright. Su objetivo principal es automatizar la búsqueda de "Furgonetas" en Wallapop, aplicar un filtro de ubicación a "Gijón", y extraer la información relevante de los anuncios.

## 🚀 Características

- Navegación automatizada a Wallapop.
- Aceptación automática del banner de cookies.
- Selección de categoría "Coches".
- Simulación de búsqueda de un término específico (ej: "Furgonetas").
- Aplicación de filtro de ubicación (ej: "Gijón, Asturias").
- Extracción de títulos de los anuncios resultantes.
- Uso de Playwright para manejar contenido dinámico y Javascript.
- Estructura de proyecto limpia y modular.
- Configuración de logging para una mejor trazabilidad.

## 🛠️ Tecnologías Utilizadas

- **Python 3.12**
- **Playwright for Python** (para automatización del navegador)
- **Node.js** (para la herramienta `npx playwright codegen`)
- **Git** / **GitHub** para control de versiones

## ⚙️ Configuración del Entorno de Desarrollo

Sigue estos pasos para configurar el proyecto en tu máquina local.

### 1. Clonar el Repositorio

Primero, clona este repositorio a tu máquina local:

git clone https://github.com/AlvaroPiedraMe/WebScraping.git
cd WebScraping

### 2. Instalar Node.js

La herramienta `npx playwright codegen` requiere **Node.js**. Si aún no lo tienes instalado:

1. Descarga el instalador LTS desde [nodejs.org](https://nodejs.org).
2. Ejecuta el instalador y asegúrate de marcar la opción **"Add to PATH"** durante la instalación.
3. Verifica la instalación abriendo una nueva terminal (CMD o PowerShell) y ejecutando:

node -v
npm -v
npx -v

### 3. Instalar Playwright CLI

pm install -g playwright

### 4. Crear y Activar el Entorno Virtual de Python

Crear el entorno virtual con Python 3.12
Asegúrate de que 'py -3.12' apunta a tu instalación de Python 3.12
    py -3.12 -m venv venv

Activar el entorno virtual
    .\venv\Scripts\activate    # En Windows PowerShell/CMD
source venv/bin/activate # En macOS/Linux

### 5. Instalar Dependencias de Python

pip install -r requirements.txt

### 6. Instalar los Navegadores de Playwright

playwright install

### 7. Uso del Scraper
 1. Abre tu terminal y navega a la raíz del proyecto (WebScraping/).

 2. Activa tu entorno virtual:
    .\venv\Scripts\activate
 3. Ejecuta el script principal:
    python main.py
 
El navegador (en modo no headless para depuración inicial) se abrirá, realizará las acciones de búsqueda y filtrado en Wallapop, y los resultados (títulos de anuncios) se imprimirán en la consola.

### Depuración de Interacciones con npx playwright codegen

 ejemplo: npx playwright codegen https://es.wallapop.com

