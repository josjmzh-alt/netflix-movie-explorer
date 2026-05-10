# ── Stage 1: Build React app ──────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .
RUN npm run build
# Output: /app/dist

# ── Stage 2: Serve with nginx ─────────────────────────────────────
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config — proxies /api and /auth to the backend service
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000
