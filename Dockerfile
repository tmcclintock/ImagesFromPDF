FROM python:3

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir output

COPY extract_images_from_pdf.py extract_images_from_pdf.py

ENTRYPOINT ["python", "extract_images_from_pdf.py"]
