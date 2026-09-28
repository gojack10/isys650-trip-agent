FROM ghcr.io/astral-sh/uv:python3.12-alpine
WORKDIR /app
COPY app.py ./
COPY docs/trip-calendar.html docs/trip-calendar.html
ENV PYTHONDONTWRITEBYTECODE=1
USER 1000:1000
CMD ["uv", "run", "--no-project", "python", "app.py"]
