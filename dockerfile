FROM python:3.11.3

WORKDIR /home/app
EXPOSE 8200
COPY . ./
# CMD ["ifconfig"]
RUN pip install -r client_requierments
CMD [ "python","client.py"]

