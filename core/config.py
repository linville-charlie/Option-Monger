import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    TWS_HOST = os.getenv('TWS_HOST', '10.255.255.254')  # Windows host from WSL
    TWS_PORT = int(os.getenv('TWS_PORT', '4002'))  # IB Gateway port
    TWS_CLIENT_ID = int(os.getenv('TWS_CLIENT_ID', '1'))
    
    TWS_PAPER_PORT = int(os.getenv('TWS_PAPER_PORT', '4002'))  # IB Gateway paper
    TWS_LIVE_PORT = int(os.getenv('TWS_LIVE_PORT', '4001'))  # IB Gateway live
    
    USE_PAPER_TRADING = os.getenv('USE_PAPER_TRADING', 'true').lower() == 'true'
    
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '10'))
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '5'))
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'option_monger.log')
    
    CACHE_EXPIRY_SECONDS = int(os.getenv('CACHE_EXPIRY_SECONDS', '300'))
    
    @classmethod
    def get_port(cls):
        if cls.USE_PAPER_TRADING:
            return cls.TWS_PAPER_PORT
        return cls.TWS_LIVE_PORT
    
    @classmethod
    def setup_logging(cls):
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)