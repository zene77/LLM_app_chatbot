---
title: Mi Chatbot Flask
emoji: 
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 500
pinned: false
---

#  LLM Application Chatbot

Aplicación web interactiva de chatbot impulsada por un Modelo de Lenguaje (LLM), desarrollada con **Flask** en el backend e integrada con un frontend dinámico en JavaScript.

##  Características principales
- **Backend:** Flask (Python 3) sirviendo respuestas de IA.
- **Frontend:** HTML5, CSS3 y JavaScript asíncrono (`fetch` con manejo de estados de carga).
- **Despliegue:** Contenerizado con Docker en Hugging Face Spaces.
- **Interfaz:** Control de concurrencia de entrada y desplazamiento automático de mensajes.

##  Tecnologías utilizadas
* **Lenguajes:** Python, JavaScript, HTML, CSS
* **Framework:** Flask
* **Infraestructura:** Docker, Hugging Face Spaces

##  Estructura del proyecto
```text
.
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── script.js
    └── images/
