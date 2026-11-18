FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
USER node
EXPOSE 8005
CMD ["node", "dist/server.js"]
