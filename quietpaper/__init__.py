import logging
import os
from logging import handlers

QP_LOG_FILE = os.environ.get("QP_LOGPATH", "log/qp.log")

logger = logging.getLogger('qp')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = handlers.RotatingFileHandler(QP_LOG_FILE, mode='a', maxBytes=1024*1024*1024, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)
