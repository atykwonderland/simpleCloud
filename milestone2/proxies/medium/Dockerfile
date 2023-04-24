FROM python 

COPY /app .

RUN apt update; apt install -y libgl1

RUN pip3 install -r requirements.txt
CMD ["python3", "app.py", "15000"]