FROM python 

COPY /app .

RUN pip3 install -r requirements.txt
CMD ["python3", "app.py", "15000"]

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
