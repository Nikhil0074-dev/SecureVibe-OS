FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npx nest build
USER node
EXPOSE 4000
CMD ["node", "dist/main.js"]
