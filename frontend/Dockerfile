# Dockerfile
FROM node:20 AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clean npm cache and install with exact versions
RUN npm cache clean --force
RUN npm install next@15.1.6
RUN npm install

# Copy source files
COPY . .

# Ensure we're building in production mode
ENV NODE_ENV=production
RUN npm run build

# Production image
FROM node:20-slim

WORKDIR /app

# Copy standalone output and required files
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

ENV NODE_ENV=production
EXPOSE 3000

# Change the start command to use the standalone server
CMD ["node", "server.js"]