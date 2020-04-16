import configparser
import MySQLdb
from datetime import datetime


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
            db=config["DB"]["db"],
        )
        self._conn.autocommit(True)

    def _get_cursor(self):
        try:
            self._conn.ping(True)
        except MySQLdb.Error:
            # reconnect your cursor
            self._create_connection()
        self._cur = self._conn.cursor()

    async def set_notification(self, user_id, scope, status):
        set_ntf = 0
        if status == 'on':
            set_ntf = 1
        sql = f'UPDATE lang SET n_{scope}={set_ntf} WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)

    def get_notifications(self, user_id):
        sql = f'SELECT n_world, n_spain, n_italy FROM lang WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)
        notifications = self._cur.fetchone()
        return notifications

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

    async def get_users_lang(self, language="all"):
        sql = f'SELECT tg_id FROM lang WHERE lang = "{language}"'
        if language == "all":
            sql = f'SELECT tg_id FROM lang'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        flat_result = [item for sublist in result for item in sublist]
        return flat_result

    async def get_users_scope(self, scope="world"):
        sql = f'SELECT tg_id FROM lang WHERE n_{scope} = 1'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        flat_result = [item for sublist in result for item in sublist]
        return flat_result

    async def set_image_hash(self, hash, filename):
        sql = f'INSERT INTO `hashImage` (file_id,filename) VALUES ("{hash}","{filename}")'
        self._get_cursor()
        self._cur.execute(sql)

    async def get_image_hash(self, filename):
        sql = f'SELECT file_id FROM `hashImage` WHERE filename = "{filename}"'
        self._get_cursor()
        self._cur.execute(sql)
        file_id = self._cur.fetchone()
        if file_id:
            return file_id[0]
        else:
            return None

    async def has_image_hash(self, filename):
        sql = f'SELECT * FROM `hashImage` WHERE filename = "{filename}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        if result:
            return True
        else:
            return False

    async def has_image_filename(self, hash):
        sql = f'SELECT * FROM `hashImage` WHERE file_id = "{hash}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        if result:
            return True
        else:
            return False

    async def clean_hashes(self):
        sql = 'DELETE FROM `hashImage`'
        self._get_cursor()
        self._cur.execute(sql)

    def is_subscribed(self, user_id, region):
        sql = f'SELECT * FROM `subs` WHERE user_id="{user_id}" AND region="{region}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        if result:
            return True
        else:
            return False

    async def add_subcription(self, user_id, region):
        if not self.is_subscribed(user_id, region):
            sql = f'INSERT INTO `subs` (user_id,region) VALUES ("{user_id}","{region}")'
            self._get_cursor()
            self._cur.execute(sql)

    async def remove_subscription(self, user_id, region):
        if self.is_subscribed(user_id, region):
            sql = f'DELETE FROM `subs` WHERE user_id="{user_id}" AND region="{region}"'
            self._get_cursor()
            self._cur.execute(sql)

    async def get_subscribed(self, region):
        sql = f'SELECT user_id FROM `subs` WHERE region="{region}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        users_ids = [val for sublist in result for val in sublist]
        return users_ids

    async def get_subscriptions(self, user_id):
        sql = f'SELECT region FROM `subs` WHERE user_id="{user_id}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        regions = [val for sublist in result for val in sublist]
        return regions

    async def status_users(self):
        sql = f'SELECT lang, count(1) as users FROM `lang` GROUP BY lang'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        lang_users = [val for val in result]
        text = "**User stats**\n"
        for lang, users in lang_users:
            text += f"- {lang}: {users}\n"
        return text

    async def status_files(self):
        sql = f"Select date, count(1) as num_files from (SELECT file_id, SUBSTRING_INDEX(filename, '_', -1) as date FROM `hashImage`) as T group by date"
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        date_files = [val for val in result]
        text = "**Files stats**\n"
        for date, num_files in date_files:
            date = int(date.replace('.png', ''))
            date = datetime.fromtimestamp(date)
            text += f"- {date:%d %b %Y %H:%M:%S}: {num_files}\n"
        return text
