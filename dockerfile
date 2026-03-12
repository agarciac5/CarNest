#Usa la imagen oficial de Python
FROM python:3.12-slim

#Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#crear y establecer directorio de trabajo
WORKDIR /app

# copiar dependencias
COPY requirements.txt .

#instalar dependencias 
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo el proyecto
COPY . .

#exponer el puerto(Django default)
EXPOSE 8000

#Comando para correr Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]