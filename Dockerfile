FROM python:3.12-slim

RUN apt-get update && apt-get install -y libreoffice && apt-get clean
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         libreoffice-core libreoffice-writer libreoffice-calc libreoffice-common libreoffice-java-common \
#         fonts-dejavu-core && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app
WORKDIR /app

CMD ["python", "app.py"]