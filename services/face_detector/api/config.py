
import os


class Config:
    LOG_FILE = "api.log"  # where logs are outputted to
    FACE_OUTPUT_DIR = ".faces"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    REDIS_URL = os.getenv("REDIS_URL", 'redis://localhost:6379/0')
    QUEUES = os.getenv("QUEUE")
    if QUEUES is None:
        logger.error("QUEUE not chosen")
        raise Exception("Please choose queue names")
    if not isinstance(QUEUES, list):
        QUEUES = [QUEUES]


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False



# way to map the value of `FLASK_ENV` to a configuration
config = {"dev": DevelopmentConfig, "prod": ProductionConfig}
