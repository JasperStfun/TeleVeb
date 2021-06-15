# TeleVeb - ВЕБ версия чата телеграм.

Приложение, для чата в веб-браузере в стиле телеграм.

# Установка
## Windows:

Скачать проект с github:
```
git clone https://github.com/JasperStfun/TeleVeb.git
```
Создать виртуальное окружение:
```
python -m venv env
```
Войти в виртуальное окружение:
```
.\env\Scripts\activate
```
Установить зависимости:
```
pip install -r requirements.txt
```
## MacOS/Linux:

Скачать проект с github:
```
git clone https://github.com/JasperStfun/TeleVeb.git
```
Создать виртуальное окружение:
```
python3 -m venv env
```
Войти в виртуальное окружение:
```
suorce env/bin/activate
```
Установить зависимости:
```
pip install -r requirements.txt
```

# Запуск
Указать flask файл приложения:
```
FLASK_APP="televeb.py"
```
Запустить flask:
```
flask run
```