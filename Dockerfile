FROM python:3.10.6
COPY ./req.txt .
RUN pip install --upgrade pip
RUN pip install  -r req.txt
RUN echo 'MONGO_PASSWD = "password"
    MONGO_USER ="admin"
    MONGO_ADDR = "mongodb://mongodb:27017/"
    MONGO_ADDR_URI = "mongodb:27017/"' > db/.env
COPY docker-entrypoint.sh /docker-entrypoint.sh
ADD ./ .
EXPOSE 3838
EXPOSE 22
ARG user
ENV ENVUSER=$user
ARG pass
ENV ENVPASS=$pass
ARG PORT
ENV ENVPORT=$PORT
ARG MONGO
ENV ENVMONGOPASS=$MONGO
RUN apt update
RUN apt install openssh-server tmux -y
# RUN service ssh start
ENTRYPOINT ["sh", "/docker-entrypoint.sh"]
CMD ["sh", "-c","sed -i s/password/$ENVMONGOPASS/g /db/.env ; python3 hash.py $ENVUSER $ENVPASS ; tmux new-session -d -s 'kill' 'python3 killuser.py';tmux new-session -d -s 'exdate' 'python3 exdate.py';uvicorn api:app --host 0.0.0.0 --port ${ENVPORT} --workers 3"]
