# Sử dụng image Python
FROM python:3.12-slim

# Đặt thư mục làm việc
WORKDIR /app

# Copy file vào container
COPY . .

# Cài đặt các thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Chạy ứng dụng Flask
CMD ["python", "main.py"]
