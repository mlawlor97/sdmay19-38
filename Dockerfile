FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN apk add python3-dev chromium chromium-chromedriver && pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
CMD python3 test.py


#Both the other ones need .dockerignore files

# Stage 1
#FROM node:8 as react-build
#WORKDIR /app
#COPY . ./
#RUN yarn
#RUN yarn build

# Stage 2 - the production environment
#FROM nginx:alpine
#COPY nginx.conf /etc/nginx/conf.d/default.conf
#COPY --from=react-build /app/build /usr/share/nginx/html
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]




#FROM node:8

# Create app directory
#WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
#COPY package*.json ./

#RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
#COPY . .

#EXPOSE 8080
#CMD [ "npm", "start" ]

