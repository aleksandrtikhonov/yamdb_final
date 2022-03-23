docker-compose exec web python manage.py makemigrations reviews
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
