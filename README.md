#  Zacharias Web Services
The Public Web Server of the T38 Workgroup : [https://t38webservices.nat.tum.de/](https://t38webservices.nat.tum.de/)

## Guide to Website Operation

*Authors: 

Yasmin Saremi, y.saremi@tum.de*  
Brianda L. Santini, brianda.santini@tum.de*  

*Physics Department T38, Technical University of Munich, Garching, Germany*.

This project runs the website for the T38 Zacharias Group. It is implemented using Django 3.2.13 and Python 3.7.11.

## Installation
It is beneficial to have a specific conda environment to host the website, so begin by creating an environment 
```bash
conda create -n "webserver" python=3.7.11

conda activate webserver
```
and installing all of the key requirements.
```bash
  pip install -r requirements.txt
``` 
You must use conda to install some additional modules.
It is recommended to use Anaconda rather than Miniconda because the modeller module may cause issues. </br>
 ```bash
 conda install -c conda-forge vmd.python

conda config --add channels salilab

conda install modeller
```
However, it will instruct you to modify /home/user/miniconda3/envs/server/lib/modeller-10.3/modlib/modeller/config.py ~~or wherever your config.py is located,~~ and replace XXXX with your Modeller licence key (in this case: MODELIRANJE). Execute the command again. </br>
If the installation of vmd-python doesn't work, go to https://github.com/Eigenstate/vmd-python, download the repo, and run it.

Finally, setup the local configurations. Open a new file **.env** and write the following:
```
SECRET_KEY=***
DEBUG=True
ALLOWED_HOSTS=***
DATABASE_URL=***
EMAIL_HOST=***
EMAIL_HOST_USER=***
EMAIL_HOST_PASSWORD=***
RECIPIENT_ADDRESS=***
```

**Congratulations!** Now you should be all set.


### Update QUEUE-ING
Added a queue-ing system with Celery, redis, redis-server. SQL couldn't handle multiple submited jobs.
All three are now in the requierements.
To activate this, one must run in the terminal before running the django server:
```bash
redis-server
```
It should automatically run in localhols:6379. 
Celery is now in control of the backend job tasks, you can monitor how they're doing by running the following command from the root directory:

```bash
celery -A myproject worker --loglevel=info
``` 
Task code error will be now written here.

## Running The Sever
First, create the database:
```bash
python manage.py migrate
```
Finally, run the development server. If you add 0.0.0.0, other devices in the local network will be able to access the web server; just remember to provide the port on which you want to operate it, which is commonly port 8000.
```bash
python manage.py runserver 0.0.0.0:8000
```
The project will be available at **http://10.152.219.203:8000/**.

## Code Documentation
Each file contains notes that describe its function. Before adding or altering files, please read Manuel.md. It describes the general project structure and the interconnectivity of the file system. It serves as a manual to change exisiting features and add new ones. </br>
ToDoList.md contains suggestions to implement and items to improve.

## Access to the Email
**https://www.sitepoint.com/django-send-email/**
We needed an email address for the contact formular. 
email adress: t38webservices@gmail.com
password: t38BSc13
app password: **bzwa txvl pbcv urue**
