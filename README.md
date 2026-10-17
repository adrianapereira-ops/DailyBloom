# ✿ DailyBloom

Aplicación web para cuidar tus hábitos diarios, encontrar tu equilibrio y celebrar cada pequeño avance. Hecha con **Python** y **Streamlit**.

## Funcionalidades

- **Cuentas de usuario**: crea tu cuenta con nombre y contraseña; cada usuario tiene sus propios datos.
- **Hábitos diarios**: marca tus objetivos del día y añade o elimina hábitos propios por áreas (Mind, Body, Energy, Personal).
- **Daily Balance**: gráfico con tu equilibrio diario entre Mind, Body y Energy.
- **Calendario**: consulta el historial de cualquier día y su progreso.
- **Bienestar**: registro de pasos, vasos de agua, minutos de meditación y horas de sueño.
- **Progreso**: gráficas de los últimos 14 días.
- **Logros** y **Consejos** para mantener la motivación.

## Capturas

| Inicio | Dashboard |
|---|---|

 |<img width="911" height="409" alt="image" src="https://github.com/user-attachments/assets/6bc7503d-a717-455c-aac2-192566f19dd1" />
 ||<img width="935" height="413" alt="image" src="https://github.com/user-attachments/assets/9c6fc113-d7a7-4680-82a0-82e7d5b25fdc" />|

| Bienestar | Progreso |
|---|---|
|<img width="727" height="403" alt="image" src="https://github.com/user-attachments/assets/d09f0d8f-9a6c-468d-82eb-1574f54d5662" />
 | <img width="734" height="406" alt="image" src="https://github.com/user-attachments/assets/c5070847-63a9-42b3-96c7-80a809ccaaa4" />|

## Tecnologías

- Python 3
- Streamlit
- Pandas
- JSON para guardar los datos

## Cómo ejecutarlo

1. Clona el repositorio:
   ```
   git clone https://github.com/adrianapereira-ops/DailyBloom.git
   cd DailyBloom
   ```
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Arranca la app:
   ```
   streamlit run app.py
   ```

## Estructura

```
DailyBloom/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── .streamlit/
│   └── config.toml        # Tema de colores
└── screenshots/           # Capturas del README
```

## Nota

Es un prototipo: las contraseñas se guardan con hash SHA-256 en un archivo local, así que no uses una contraseña que utilices en otros servicios.

## Autora

Adriana Pereira Domènech
