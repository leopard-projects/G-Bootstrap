# stage 1
FROM node:latest as node
# FROM alpine:latest

RUN curl -s https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && apt-get update && apt-get install -y google-chrome-stable

ENV CHROME_BIN /usr/bin/chromium-browser

WORKDIR /app
COPY . .
RUN npm install --force
RUN npm run brewbuild
RUN npm run testerbuild
# RUN npm run test

# stage 2
FROM nginx:alpine
COPY --from=node /app/dist/brew-tester /usr/share/nginx/html

# RUN docker run -d -p 8822:80 gbootstrap:v0



