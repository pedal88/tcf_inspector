from app import create_app

application = create_app()
app = application  # For Gunicorn to find the app

if __name__ == "__main__":
    application.run() 