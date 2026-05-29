FROM python:3.14-slim-bookworm

# Install uv from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /frontend

# Enable bytecode compilation and disable uv cache for the build process
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first (leveraging Docker layer caching)
COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY src ./src

# Ensure the project itself is installed
RUN uv sync --frozen

# Use the project's virtual environment
ENV PATH="/frontend/.venv/bin:$PATH"

#ENTRYPOINT ["ls"]
#CMD ["-R"]
ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "main:app"]

EXPOSE 8000
