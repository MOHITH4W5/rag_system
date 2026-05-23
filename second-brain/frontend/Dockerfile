FROM node:20-alpine

WORKDIR /app

COPY second-brain/frontend/package*.json ./
RUN npm install

COPY second-brain/frontend/ ./

RUN npm run build

EXPOSE 3001

CMD ["npm", "run", "start", "--", "-H", "0.0.0.0"]
