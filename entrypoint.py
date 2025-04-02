import os
import threading
import uvicorn
from exporter_listener import init_listener

def start_flask():
    """
    Start Flask app (if using Flask, this can be customized for FastAPI).
    """
    os.system("flask run --host=0.0.0.0 --reload")

if __name__ == "__main__":
    # Start Kafka listener in a separate thread
    kafka_thread = threading.Thread(target=init_listener)
    kafka_thread.start()

    # Start FastAPI app (Flask is optional depending on your framework)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

    # Wait for Kafka listener thread to finish (if needed)
    kafka_thread.join()
