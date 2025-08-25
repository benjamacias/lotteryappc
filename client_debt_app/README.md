# Client Debt App (Flask)

## Migraciones

Para registrar cambios en los modelos, después de modificar `models.py` generar y aplicar una nueva migración:

```bash
export FLASK_APP=app.py
flask db migrate -m "descripcion"
flask db upgrade
```
