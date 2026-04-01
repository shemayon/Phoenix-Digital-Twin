FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/uv

WORKDIR /app

# Copy the backend project and the sample data
COPY backend ./backend
COPY ["Sample data.xlsx", "."]

# Install dependencies
RUN uv sync --project backend

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uv", "run", "--project", "backend", "backend"]
