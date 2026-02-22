# ============================================
# Multi-stage Dockerfile for React Frontend
# ============================================

FROM node:20-alpine as base

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* bun.lockb* ./
RUN if [ -f bun.lockb ]; then \
    npm install -g bun && bun install; \
    else \
    npm ci; \
    fi


# ============================================
# Builder stage - Build production assets
# ============================================
FROM base as builder

COPY . .

# Build the application
RUN if [ -f bun.lockb ]; then \
    bun run build; \
    else \
    npm run build; \
    fi


# ============================================
# Production stage - Serve with nginx
# ============================================
FROM nginx:alpine as production

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Add health endpoint to nginx
RUN echo 'server { listen 80; location /health { return 200 "OK"; } }' > /etc/nginx/conf.d/health.conf

CMD ["nginx", "-g", "daemon off;"]


# ============================================
# Development stage - Run with Vite dev server
# ============================================
FROM base as development

COPY . .

EXPOSE 8080

CMD if [ -f bun.lockb ]; then \
    bun run dev; \
    else \
    npm run dev; \
    fi
