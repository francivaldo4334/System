FROM python:3.13-slim AS base

# Instala dependências do sistema necessárias para o psycopg2, uv e Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instala o Node.js (necessário para o hot-reload do Tailwind via app Django)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Instala o 'uv' diretamente do binário oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Variáveis de ambiente para o Python e uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Copia os arquivos de dependências primeiro (otimização de cache de camada)
COPY pyproject.toml uv.lock ./

# Cria o ambiente virtual e instala as dependências usando o uv
RUN uv sync --frozen --no-install-project

# O restante do código será montado via volume no docker-compose, 
# mas copiamos aqui para garantir integridade da imagem de base
COPY . .
