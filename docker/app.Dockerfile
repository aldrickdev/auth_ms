FROM python:3.10.4

# detail that port 8000 will be used
EXPOSE 3000/tcp

# create and move to the project directory
WORKDIR /project
# copy project files and give app ownership
COPY ../requirements.txt requirements.txt

# install project requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# create the directory for the app
WORKDIR /project/app
# copy the contents of the app directory into the container
COPY ../app .

# move into app directory and run the application
WORKDIR /project/app

# start app
CMD ["python", "main.py"]
