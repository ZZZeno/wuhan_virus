
class Config():
    SCHEDULER_API_ENABLED = True


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wuhan:wuhan_virus@localhost:3306/wuhan?charset=utf8"

class DebugConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/wuhan?charset=utf8"