# Stage 1: Build
FROM node:20-slim AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
ENV NEXT_PUBLIC_API_BASE_URL=""
RUN npm run build

# Stage 2: Run standalone
FROM node:20-slim AS runner

WORKDIR /app
ENV NODE_ENV=production

# Copy only what Next.js standalone needs
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
