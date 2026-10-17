# DailyBloom

Dashboard web de hábitos y bienestar personal con Python y Streamlit.

## Ejecutar localmente

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La página inicial permite crear una cuenta local o iniciar sesión. Cada perfil guarda sus hábitos y registros en un archivo local separado.

**Importante:** es un prototipo local. No uses una contraseña real ni publiques `users.json` o `habits_*.json`. Para producción necesitarías autenticación más robusta y una base de datos.
