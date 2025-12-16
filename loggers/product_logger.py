import logging

product_logger = logging.getLogger("product_logger")
product_logger.setLevel(logging.INFO)

fh = logging.FileHandler("product_sync.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)

product_logger.addHandler(fh)
