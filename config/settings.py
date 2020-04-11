import MySQLdb
import configparser


config_file = "conf.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")


class DBHandler:
    """
    Create a database with this table:
    CREATE TABLE lang (
    tg_id INT(16) UNSIGNED PRIMARY KEY,
    lang VARCHAR(4) NOT NULL
    )
    """
    _conn = None
    _cur = None

    def __init__(self):
        self._create_connection()

    def _create_connection(self):
        self._conn = MySQLdb.connect(
            host=config["DB"]["host"],
            user=config["DB"]["user"],
            passwd=config["DB"]["passwd"],
            db=config["DB"]["db"])
        self._conn.autocommit(True)

    def _get_cursor(self):
        try:
            self._conn.ping(True)
        except MySQLdb.Error:
            # reconnect your cursor
            self._create_connection()
        self._cur = self._conn.cursor()

    async def set_language(self, user_id, language):
        sql = f'INSERT INTO lang (tg_id,lang) VALUES ({user_id},"{language}") ON DUPLICATE KEY UPDATE lang = "{language}"'
        self._get_cursor()
        self._cur.execute(sql)

    async def get_language(self, user_id):
        sql = f'SELECT lang FROM lang WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)
        language = self._cur.fetchone()
        if language:
            return language[0]
        else:
            return 'None'
