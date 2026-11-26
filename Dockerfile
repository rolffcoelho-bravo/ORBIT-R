FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[server]' && useradd -r -u 10001 monitor && mkdir -p /app/data/state && chown -R monitor:monitor /app/data
USER monitor
EXPOSE 8080
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=3).read()"
CMD ["uvicorn","orbitr.app:app","--host","0.0.0.0","--port","8080","--workers","1"]
