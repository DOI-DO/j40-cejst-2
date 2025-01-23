FROM node:23-slim
RUN apt-get update -y
RUN npm install -g http-server
CMD ["http-server", "./", "--cors"]
