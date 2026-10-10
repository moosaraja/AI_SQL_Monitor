import time
import logging
from datetime import datetime

from collector import process_snapshot
from deadlock_monitor import process_deadlocks


MONITOR_INTERVAL = 10  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_monitoring():

    logging.info("AI SQL Monitor scheduler started")

    while True:

        try:
            logging.info("Starting SQL Server monitoring")

            process_snapshot()

            logging.info("Monitoring cycle completed")

        except Exception:
            logging.exception("Monitoring cycle failed")

        try:
            logging.info("Checking SQL Server deadlocks")

            processed = process_deadlocks()

            logging.info(
                "New deadlocks processed: %s",
                len(processed)
            )

        except Exception:
            logging.exception("Deadlock monitoring failed")

        time.sleep(MONITOR_INTERVAL)


if __name__ == "__main__":
    try:
        run_monitoring()

    except KeyboardInterrupt:
        logging.info("Monitoring scheduler stopped")