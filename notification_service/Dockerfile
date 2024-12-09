FROM python

WORKDIR /app
ENV PYTHONUNBUFFERED = 1
ENV PYTHONPATH="/app:$PYTHONPATH"

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
