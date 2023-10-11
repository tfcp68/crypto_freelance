FROM python:3.8

ENV JS_PYTHON_API_URL="http://js_api:6666/"
ENV WEB3_ENDPOINT="https://rpc.sepolia.org/"
ENV REDIS_HOST="redis"
ENV REDIS_PORT="6379"

WORKDIR /project
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD python3 manage.py collectstatic --noinput
CMD python3 manage.py migrate
CMD ["python3", "manage.py", "runserver", "0.0.0.0:5555"]
