FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["sh", "-c", "python3 -u /usr/local/patriot/update_database.py & tail -f /dev/null"]
CMD ["python3", "-u", "/usr/local/patriot/walkthrough_recorder_app.py"]