FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["make", "migrate", "run"]