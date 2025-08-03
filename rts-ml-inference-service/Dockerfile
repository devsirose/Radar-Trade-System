FROM python:3.10-slim

WORKDIR /app

# Copy requirements trước để tận dụng layer cache
COPY requirements.txt .

# Cài dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code sau khi cài pip xong (tối ưu cache)
COPY . .

EXPOSE 8081

# Chạy app FastAPI
CMD ["uvicorn", "inference.api:app", "--host", "0.0.0.0", "--port", "8081"]
