## A BBS BASED ON DJANGO

### requirements:
* Python 2.6+
* Django 1.3.1
* Mysql
* Memcached
* uWSGI
* Nginx (uwsgi supported)
    
    
Project deployed with **Virtualenv**.


### How to initial a NEW server for python-gears:

1. apt-get update && apt-get upgrade

2. add a non root user (optional)

```bash
mkdir -p /home/yueyoum
groupadd yueyoum
useradd yueyoum -d /home/yueyoum -g yueyoum -s /bin/bash
passwd yueyoum
usermod -a -G www-data yueyoum
usermod -a -G sudo yueyoum
```

3. apt-get install build-essential

4. apt-get install mysql-server

   _ubuntu 12.04 will install mysql 5.5_

5. vim /etc/mysql/my.cnf

```bash
add the following in [client]
    default-character-set = utf8

add the following in [mysqld]
    default-storage-engine = InnoDB
    character-set-server = utf8
```
        

6. /etc/init.d/mysql restart


7. install requirments

```bash
apt-get install libmysqld-dev
apt-get install python-dev
apt-get install memcached
apt-get install nginx
apt-get install python-virtualenv
```

8. deploy 

```bash
cd /
mkdir -p data/project
chmod 777 data
cd data
chown yueyoum:www-data project
chmod g+w project

cd project
su yueyoum
mkdir python_gears  # and locate code here
cd python_gears
virtualenv env --no-site-packages --distribute --prompt="(python-gears)"
source env/bin/activate

pip install -r deploy/requirements.txt

python manage.py validate
```


9. final, set uwsgi, nginx, and run project


### NOTICE

This project was hosted bitbucket.org originally

Then simply migrate to github, So, `deploy/get_code.sh` should be adjusted.  **But, I haven't do this :)**
