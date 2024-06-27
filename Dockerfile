#Dockerfile para criar imagem padrao seguros
#Ele usa a imagem com python pre compilada no repositorio amopromo
FROM amopromo/python3.11-nginx:latest
#########################################################
#Instala dependencias e remove temporarios
RUN apk add --no-cache  tzdata \
        gcc \
        sqlite \
        bash \
        openssh 

RUN cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime

COPY ./requirements.txt /tmp

RUN pip install --no-cache-dir --upgrade  pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir gunicorn 

RUN apk del gcc

RUN mkdir -p /usr/share/zoneinfo/America/ && \
        cp /etc/localtime /usr/share/zoneinfo/America/Sao_Paulo

RUN apk --no-cache add ca-certificates

# copia o codigo
COPY . /usr/src/

WORKDIR /usr/src/

EXPOSE 8080/tcp

CMD ["sh","/usr/src/start.sh"]
