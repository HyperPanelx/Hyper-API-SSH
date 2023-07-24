# SSH Tunnel With API

SSH tunnel dynamic is a method of creating a secure connection between two computers over an unsecured network. It involves using the SSH protocol to create a tunnel through which data can be transmitted securely.

In this case, a Python backend with FastAPI is used to control the SSH tunnel dynamic. The backend is connected to a MongoDB database for storage and retrieval of data.

Overall, this setup provides a secure and efficient way to transmit data over an unsecured network while also allowing for easy control and management through the use of Python and FastAPI.

## Installation

There are two ways to install and run this project: 
First You can pull the project and install the Python requirements, then run the API using uvicorn. 

```bash
uvicorn --host <your-hostname> --port <your-port> api:app 
```

Alternatively, you can use the pre-built image of this project that is available in my Dockerhub.


```bash
https://hub.docker.com/u/officialalikhani
```

For Pull and run docker image you can use this command after install docker:
```bash
docker run -it -e ENVMONGOPASS=<your-db-password> -e ENVPORT=<your-api-port> -e ENVUSER=<your username> -e ENVPASS=<your password> -p <container-port>:<your-api-port> officialalikhani/ssh_api:latest

```
<img src="preview/login.png" alt="Alt text">


