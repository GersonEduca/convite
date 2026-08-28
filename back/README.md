# Backend do convite

Projeto Django que serve a pagina existente em `../front` e disponibiliza a API de confirmacao.

## Executar no Windows

```powershell
cd back
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abra http://127.0.0.1:8000/. O painel administrativo fica em `/admin/`.

## Rotas da API

- `GET /api/guests/`: lista convidados.
- `POST /api/guests/<id>/respond/`: recebe `{"response":"confirmed"}` ou `{"response":"declined"}`.