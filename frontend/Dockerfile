FROM node:18-alpine

WORKDIR /app

# Run as root
USER root

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

RUN npm run dev