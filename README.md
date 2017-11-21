# Tutoria

Limitations:
Since the server is supposed to working for most of the time continuously. Some functionalities require scheduling like lock sessions and end sessions use case have to run routinely each half an hour. So if the django server is not opening for a while. Some update may have to be done manually

Steps required to deploy:
extra package installed:
django-cron.

``` pip install django-cron ```

Then run the server.

``` python manage.py runserver ```

Start the schedule that run every 30 minutes using

``` crontab -e
*/30 * * * * source /home/ubuntu/.bashrc && 
source /home/ubuntu/work/your-project/bin/activate && 
python /home/ubuntu/work/your-project/src/manage.py runcrons ```