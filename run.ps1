if (Test-Path "core\migrations") { Remove-Item "core\migrations" -Recurse -Force }
python manage.py makemigrations core
python manage.py migrate
python manage.py import_json
python manage.py createsuperuser


# .\run.ps1
