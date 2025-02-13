
FROM python:3.13-alpine

RUN mkdir auth
WORKDIR /auth
COPY ./pyproject.toml ./
COPY ./.python-version ./
COPY ./uv.lock ./
RUN pip3 install uv
RUN uv sync --frozen
ADD . /auth

CMD [ "uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8080"]
