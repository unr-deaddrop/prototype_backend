FROM python:3.11.4

WORKDIR /app

# prevent .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure output ios sent directly to terminal without buffering
ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT=8000
EXPOSE 8000