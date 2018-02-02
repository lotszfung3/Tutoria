# Tutoria
# Overview
* This is a django project that maintains a tutoring system. In which user can be acts as tutors/ students.
* We try to include the modules provided by Django. including
  - authentication
  - Database into ORM
  - middleware
  - Django-admin
  - Template
 

# Main functionalities
* Book sessions
* Cancel sessions
* Manage account
* Mange wallet
* Authentication
* Django-admin

# To Run
* Install Django
* clone this repository
* Run it
```
python manage.py runserver
```

* Explore it


Limitations:
Since the server is supposed to working for most of the time continuously. Some functionalities require scheduling like lock sessions and end sessions use case have to run routinely each half an hour. So if the django server is not opening for a while. Some update may have to be done manually

Steps required to deploy:
extra package installed:
django-cron.

``` pip install django-cron ```

Then run the server.

``` python manage.py runserver ```

Start the schedule that run every 30 minutes using

``` 

>  env EDITOR=nano crontab -e
*/30 * * * * source /home/ubuntu/.bashrc && 
source /home/ubuntu/work/your-project/bin/activate && 
python /home/ubuntu/work/your-project/src/manage.py runcrons 

CTRL + 0
CTRL + X

```
