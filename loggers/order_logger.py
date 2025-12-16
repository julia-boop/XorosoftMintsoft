import logging

order_logger = logging.getLogger("order_logger")
order_logger.setLevel(logging.INFO)

fh = logging.FileHandler("order_sync.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)

order_logger.addHandler(fh)
