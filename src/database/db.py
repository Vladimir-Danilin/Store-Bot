import asyncpg


class DataBaseConnection:
    def __init__(self, host: str = 'localhost', port: int = 5454, user: str = 'postgres',
                 password: str = None, database: str = None):
        self.conn = None
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database

    async def connection(self) -> None:
        self.conn = await asyncpg.connect(host=self.__host,
                                          port=self.__port,
                                          user=self.__user,
                                          password=self.__password,
                                          database=self.__database)

    async def close(self) -> None:
        await self.conn.close()

    async def transaction_insert_registration(self, login: str, password: str, user_id: int) -> None:
        async with self.conn.transaction():
            await self.conn.execute(
                f"insert into users (login, password, user_id) values('{login}', '{password}', '{user_id}')")

    async def transaction_update_phone_number(self, phone_number: str, user_id: int) -> None:
        async with self.conn.transaction():
            await self.conn.execute(
                f"update users set phone = {phone_number} where user_id = {user_id}")

    async def transaction_update_location(self, location: list[int], user_id: int) -> None:
        location = str(location).replace('[', '{').replace(']', '}')
        async with (self.conn.transaction()):
            await self.conn.execute(
                f"update users set location = '{location}' where user_id = {user_id}")

    async def query_select_types(self) -> list[list]:
        return await self.conn.fetch(
            f"select type from products")

    async def query_select_categories_by_type(self, type_product: str) -> list[list]:
        return await self.conn.fetch(
            f"select category from products where type = '{type_product}'")

    async def query_select_products_by_category(self, category: str) -> list[list]:
        return await self.conn.fetch(
            f"select title, cost, sale, image, description, id from products where category = '{category}'")

    async def query_select_user_info(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select login, money, phone, location from users where user_id = '{user_id}'")

    async def query_select_user_id(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select user_id from users where user_id = '{user_id}'")

    async def query_select_login(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select login from users where user_id = '{user_id}'")

    async def query_select_password(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select password from users where user_id = '{user_id}'")

    async def query_select_location(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select location from users where user_id = '{user_id}'")

    async def query_select_phone(self, user_id: int) -> list[list[str]]:
        return await self.conn.fetch(
            f"select phone from users where user_id = '{user_id}'")

    async def reset_user(self, user_id: int):
        await self.conn.fetch(f"delete from users where user_id = '{user_id}'")
