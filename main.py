import sys
from gevent.pywsgi import WSGIServer
from src import create_app  # Import method to start application

if __name__ == '__main__':  # If this is the main entry point...
    addr = ''
    port = 433
    debug = False
    localDB = False

    if len(sys.argv) == 2:
        debug = sys.argv[0].lower() == "true"
        localDB = sys.argv[1].lower() == "true"
    elif len(sys.argv) == 3:
        port = sys.argv[0]
        debug = sys.argv[1].lower() == "true"
        localDB = sys.argv[2].lower() == "true"
    elif len(sys.argv) == 4:
        addr = sys.argv[0]
        port = sys.argv[1]
        debug = sys.argv[2].lower() == "true"
        localDB = sys.argv[3].lower() == "true"

    app = create_app(debug, localDB)  # Create instance of application

    if debug:
        app.run(port=433)
    else:
        http_server = WSGIServer((addr, port), app)
        http_server.serve_forever()  # Run the application
