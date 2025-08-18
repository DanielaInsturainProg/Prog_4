from code import make_celery, app

# Crear instancia de Celery
celery = make_celery(app)

if __name__ == '__main__':
    celery.start()