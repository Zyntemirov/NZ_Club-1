git

    git add . 
    git pull origin master
    git commit -m "some commit"
    git push origin master
    git rm -r --cached .

Database
    
    create database reklama character set utf8 collate utf8_unicode_ci;
My Config

create file tournament/my.cnf in the project and edit this file
    
    [client]
    database = mydatabase
    user = your_username
    password = password
    default-character-set = utf8

Django

    pip3 freeze > requirements.txt.
    pip3 install -r requirements.txt
    python3 manage.py makemigrations
    python manage.py migrate
    

Run the collectstatic management command:

    python manage.py collectstatic
    

Start a Redis server on port 6379, run the following command:
    
    sudo docker run -p 6379:6379 -d redis:2.8
    
 
To kill container
    
    sudo docker container ls
    sudo docker rm -f <container-name>


To run gunicorn in venv
    
    gunicorn --bind 81.90.181.10:8005 tournament.wsgi
    
