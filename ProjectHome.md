# django-webproxy #
a proxy django app

## Useage ##
Install Python

Install Django

Edit settings.py, in the end add 2 lines, like:
```
WEB_PROXY_DOMAIN = 'www.google.com'
WEB_PROXY_PORT = 80
```

Run the django site:
```
python manage.py runserver
```
Then you success to made a proxy to the site.