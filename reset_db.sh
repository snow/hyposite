sudo -u postgres dropdb hypo
sudo -u postgres createdb hypo
./manage.py syncdb
