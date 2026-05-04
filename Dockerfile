FROM python:3.11-alpine

# Create non-root user (security requirement)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Create logs directory
RUN mkdir -p /logs && chown appuser:appgroup /logs

USER appuser

EXPOSE 3000

CMD ["python", "main.py"]