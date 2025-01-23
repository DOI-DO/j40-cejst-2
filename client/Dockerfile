FROM node:14

ENV PORT=6000

# Set working directory like 'cd' command, any subsequent instructions in this docker file, will start from 
# this working directory
WORKDIR /client

# install all packages as a layer in the docker image / container
COPY package*.json ./
RUN npm ci && npm cache clean --force 

# copy all local files from the working directory to the docker image/container however we must use 
# dockerignore to ignore node_modules so that the image can use what what was just installed from the above
# step.
COPY . .

EXPOSE 6000

CMD [ "npm", "start"]