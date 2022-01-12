from src import create_app  # Import method to start application

app = create_app()  # Create instance of application

if __name__ == '__main__':  # If this is the main entry point...
    app.run(port=9000)  # Run the application
