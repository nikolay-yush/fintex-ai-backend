import logging
import os
import sys
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue


LOG_DIR = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

def setup_logging():
    """
    Initializes a non-blocking asynchronous logger using a QueueHandler.
    Logs are collected via a queue and written to both stdout and a rolling file in a background thread.
    """
    # Ensure the log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger("fintex_ai")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if the logger is already initialized
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # 1. Create target handlers for final output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # High-performance rolling file handler: max 5MB per file, max 5 files total (1 main + 4 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=4, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        # 2. Setup an unbounded thread-safe queue for log events
        log_queue = Queue(-1)
        
        # 3. Main logger routes events to the queue instantly (non-blocking)
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)

        # 4. Start a background listener thread to process logs from the queue
        listener = QueueListener(log_queue, console_handler, file_handler, respect_handler_level=True)
        listener.start()

    return logger


logger = setup_logging()