
import os


class Config:
    LOG_FILE = "api.log"  # where logs are outputted to
    FACE_OUTPUT_DIR = ".faces"
class DevelopmentConfig(Config):
    pass

class ProductionConfig(Config):
    pass



# way to map the value of `FLASK_ENV` to a configuration
config = {"dev": DevelopmentConfig, "prod": ProductionConfig}
