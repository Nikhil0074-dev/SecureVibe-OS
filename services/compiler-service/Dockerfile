FROM python:3.12-slim
WORKDIR /app
COPY services/compiler-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/compiler-service/src ./src
COPY packages/tf-secure-templates /templates
ENV TEMPLATES_DIR=/templates/aws
RUN useradd -u 10001 app && chown -R app /app
USER app
EXPOSE 8002
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
