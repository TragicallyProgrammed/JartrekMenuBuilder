from src import create_app  # Import method to start application

app = create_app(True)  # Create instance of application

if __name__ == '__main__':  # If this is the main entry point...
    app.run(port=443)  # Run the application
