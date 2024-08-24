FROM python:3.11-slim

RUN pip install uv

WORKDIR /app
COPY pyproject.toml ./
COPY requirements.lock ./
RUN uv pip install --no-cache --system -r requirements.lock

COPY . .

# Dummy command (this will be overwritten by ECS task definition or entrypoint)
CMD ["echo", "This is a placeholder CMD, replace with actual command in ECS task definition"]
