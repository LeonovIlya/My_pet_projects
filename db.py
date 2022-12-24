import logging
import aiosqlite as asq


class BotDB:
    def __init__(self, db_file):
        self._db_file = db_file

    # получаем булево значение по запросу
    async def get_check(self, query, **kwargs):
        async with asq.connect(self._db_file) as connection:
            query += ' WHERE ' + ' AND '.join(['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
            async with connection.execute(query, values) as cursor:
                return bool(await cursor.fetchone())

    # получаем значение по запросу
    async def get_stuff(self, query, **kwargs):
        async with asq.connect(self._db_file) as connection:
            query += ' WHERE ' + ' AND '.join(['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
            async with connection.execute(query, values) as cursor:
                fetch = await cursor.fetchone()
                return fetch[0]

    # получаем список по запросу
    async def get_stuff_list(self, query, **kwargs):
        async with asq.connect(self._db_file) as connection:
            if kwargs:
                query += ' WHERE ' + ' AND '.join(['' + k + ' = ?' for k in kwargs.keys()])
                values = list(kwargs.values())
            else:
                values = ''
            async with connection.execute(query, values) as cursor:
                fetch = await cursor.fetchall()
                if int(len(fetch[0])) == 1:
                    result = [i[0] for i in fetch]
                elif int(len(fetch[0])) == 2:
                    result = [(i[0], str(i[1])) for i in fetch]
                return result

    # запрос на изменение данных в бд
    async def record_to_db(self, query, **kwargs):
        async with asq.connect(self._db_file) as connection:
            values = list(kwargs.values())
            await connection.execute(query, values)
            await connection.commit()
            logging.info(f'NEW SQL QUERY : {query, values}')
