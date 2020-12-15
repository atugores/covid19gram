import configparser
import MySQLdb
from datetime import datetime


config_file = "conf.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")


class DBHandler:
    """
    Create a database with this table:
        CREATE TABLE hashImage (
        id int(11) NOT NULL,
        file_id text NOT NULL,
        filename text CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
        date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

        CREATE TABLE subs (
        user_id bigint(20) NOT NULL,
        region text CHARACTER SET utf8 COLLATE utf8_spanish2_ci NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

        CREATE TABLE users (
        tg_id bigint(20) NOT NULL,
        lang text NOT NULL,
        n_world tinyint(1) NOT NULL DEFAULT '0',
        n_spain tinyint(1) NOT NULL DEFAULT '0',
        n_italy tinyint(1) NOT NULL DEFAULT '0',
        n_france tinyint(1) NOT NULL DEFAULT '0',
        n_austria tinyint(1) NOT NULL DEFAULT '0',
        botons set('gl','es','it','fr','at') NOT NULL DEFAULT 'gl,es,it'
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

        ALTER TABLE hashImage
        ADD PRIMARY KEY (id);

        ALTER TABLE subs
        ADD KEY s_key (user_id,region(255));

        ALTER TABLE users
        ADD UNIQUE KEY id (tg_id);

        ALTER TABLE hashImage
        MODIFY id int(11) NOT NULL AUTO_INCREMENT;
    """

    SCOPES = ['gl', 'es', 'it', 'fr', 'at', 'ar', 'au', 'br', 'ca', 'cl', 'cn', 'co', 'de', 'in', 'mx', 'pt', 'us', 'gb', 'ib', 'ma', 'me', 'ei', 'ct']
    NSCOPES = ['world', 'spain', 'italy', 'france', 'austria', 'argentina', 'australia', 'brazil', 'canada', 'chile', 'china', 'colombia', 'germany', 'india', 'mexico', 'portugal', 'us', 'unitedkingdom', 'balears', 'mallorca', 'menorca', 'eivissa', 'catalunya']

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
        notifications_list = self.get_notifications(user_id)
        if scope in self.NSCOPES:
            if status == 'on':
                notifications_list.append(scope)
            elif len(notifications_list) > 1:
                notifications_list.remove(scope)
            notifications = ','.join(notifications_list)
            sql = f"UPDATE users SET notifications='{notifications}' WHERE tg_id = {user_id}"
            self._get_cursor()
            self._cur.execute(sql)
            return True
        return False

    def get_notifications(self, user_id):
        sql = f'SELECT notifications FROM users WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)
        notifications = self._cur.fetchone()[0].strip("'").split(',')
        if '' in notifications:
            return []
        else:
            return notifications

    def get_buttons(self, user_id):
        sql = f'SELECT botons FROM users WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)
        results = self._cur.fetchone()[0].strip("'").split(',')
        if '' in results:
            return []
        else:
            return results

    async def set_button(self, user_id, button, status='on'):
        buttons_list = self.get_buttons(user_id)
        if button in self.SCOPES:
            if status == 'on':
                buttons_list.append(button)
            elif len(buttons_list) > 1:
                buttons_list.remove(button)
            else:
                return False
            buttons = ','.join(buttons_list)
            sql = f"UPDATE users SET botons = '{buttons}' WHERE tg_id = {user_id}"
            self._get_cursor()
            self._cur.execute(sql)
            return True
        return False

    async def set_language(self, user_id, language):
        sql = f'INSERT INTO users (tg_id,lang) VALUES ({user_id},"{language}") ON DUPLICATE KEY UPDATE lang = "{language}"'
        self._get_cursor()
        self._cur.execute(sql)

    async def get_language(self, user_id):
        sql = f'SELECT lang FROM users WHERE tg_id = {user_id}'
        self._get_cursor()
        self._cur.execute(sql)
        language = self._cur.fetchone()
        if language:
            return language[0]
        else:
            return 'None'

    async def get_users_lang(self, language="all"):
        sql = f'SELECT tg_id FROM users WHERE lang = "{language}"'
        if language == "all":
            sql = f'SELECT tg_id FROM users'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        flat_result = [item for sublist in result for item in sublist]
        return flat_result

    async def get_users_scope(self, scope="world"):
        sql = f'SELECT tg_id FROM users WHERE FIND_IN_SET("{scope}",notifications)>0'
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

    def is_subscribed(self, user_id, region, scope):
        sql = f'SELECT * FROM `subs` WHERE user_id="{user_id}" AND region="{region}" AND (scope="{scope}" OR scope="void")'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        if result:
            return True
        else:
            return False

    async def add_subscription(self, user_id, region, scope):
        if not self.is_subscribed(user_id, region, scope):
            sql = f'INSERT INTO `subs` (user_id,region,scope) VALUES ("{user_id}","{region}","{scope}")'
            self._get_cursor()
            self._cur.execute(sql)

    async def remove_subscription(self, user_id, region, scope):
        if self.is_subscribed(user_id, region, scope):
            sql = f'DELETE FROM `subs` WHERE user_id="{user_id}" AND region="{region}" AND (scope="{scope}" OR scope="void")'
            self._get_cursor()
            self._cur.execute(sql)

    async def get_subscribed(self, region, scope):
        sql = f'SELECT user_id FROM `subs` WHERE region="{region}" AND (scope="{scope}" OR scope="void")'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        users_ids = [val for sublist in result for val in sublist]
        return users_ids

    async def get_subscriptions(self, user_id):
        sql = f'SELECT region, scope FROM `subs` WHERE user_id="{user_id}"'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        regions = [{'region': val[0], 'scope': val[1]} for val in result]
        return regions

    async def status_users(self):
        sql = f'SELECT lang, count(1) as users FROM users GROUP BY lang'
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        lang_users = [val for val in result]
        text = ""
        total = 0
        for lang, users in lang_users:
            text += f"- {lang}: {users}\n"
            total += users
        return f"**User stats ({total})**\n" + text

    async def status_notifications(self):
        sql = "SELECT 'world', COUNT(*) FROM users WHERE FIND_IN_SET('world',notifications)>0"
        for scope in self.NSCOPES:
            if scope not in ['none', 'world']:
                sql += f" UNION SELECT '{scope}', COUNT(*) FROM users WHERE FIND_IN_SET('{scope}',notifications)>0"
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        notf_users = [val for val in result]
        text = ""
        for notf, users in notf_users:
            text += f"- {notf}: {users}\n"
        return f"**Subscription stats**\n" + text

    async def status_files(self):
        sql = f"Select date, count(1) as num_files from (SELECT file_id, SUBSTRING_INDEX(filename, '_', -1) as date FROM `hashImage`) as T group by date"
        self._get_cursor()
        self._cur.execute(sql)
        result = self._cur.fetchall()
        date_files = [val for val in result]
        text = "**Files stats**\n"
        for date, num_files in date_files[-10:]:
            date = int(date.replace('.png', ''))
            date = datetime.fromtimestamp(date)
            text += f"- {date:%d %b %Y %H:%M:%S}: {num_files}\n"
        return text
