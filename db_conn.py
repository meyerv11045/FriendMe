import sqlalchemy

class DbConn:
    def __init__(self):
        self.db_conn = None

    def create_conn(self):
        connection_name = "integrated-hawk-328518:us-central1:friendme-db"
        db_name = "users"
        db_user = "root"

        driver_name = 'mysql+pymysql'
        query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})
        db = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername=driver_name,
                username=db_user,
                database=db_name,
                query=query_string,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800
        )
        self.db_conn = db.connect()

    def query(self,query):
        return self.db_conn.execute(query)

    def __del__(self):
        self.db_conn.close()