from fastapi.responses import JSONResponse

from log.logger import logger
from database.connection import JobDb
import database.sql_requests as sql

from .model_answer import AllUser


from datetime import datetime
from email_validator import validate_email



async def create_user(user):
    try:
        async with JobDb() as connector:
            try:
                validate_email(user.email)
                check_email = await connector.fetchval(sql.CHECK_EMAIL, user.email)
                if check_email:
                    logger.info(f"Попытка создать пользователя с существующим email - {user.email}")
                    return JSONResponse(status_code=400,
                                        content={"error": "Ошибка: Пользователь с данным email уже присутствует в базе данных."})
            except Exception:
                return JSONResponse(status_code=400,
                                    content={"error": "Ошибка: Введенный email не является электронным адресом."})
            user_create = await connector.fetchval(sql.CREATE_USER, user.name, user.email, datetime.now())
            if user_create:
                wallet_create = await connector.fetchval(sql.CREATE_WALLET, user_create, user.balance)
                if wallet_create:
                    logger.info(f"Создан пользователь: Id - {user_create}, email - {user.email}")
                    return JSONResponse(status_code=200,
                                        content={"answer": "Пользователь успешно создан."})
                else:
                    return JSONResponse(status_code=400,
                                        content={"error": "Не удалось создать кошелек для пользователя"})
    except Exception as e:
        logger.error(f"Получено исключение при исполнении кода {e}")
        return JSONResponse(status_code=500, content={"error": "Ошибка: Во время создания пользователя произошла ошибка."})


async def receive_users():
    try:
        async with JobDb() as connector:
            users = await connector.fetch(sql.GET_USERS)
            if users:
                transformation_user = [dict(AllUser(**user)) for user in users]
                logger.info(f"Запрошен список всех пользователей")
                return JSONResponse(status_code=200,
                                    content={"answer": transformation_user})
            else:
                return JSONResponse(status_code=200,
                                    content={"answer": "Нет пользователей в базе данных."})
    except Exception as e:
        logger.error(f"Получено исключение при исполнении кода {e}")
        return JSONResponse(status_code=500, content={"error": "Ошибка: Во время получения списка пользователей произошла ошибка."})


async def create_transfer(transfer):
    try:
        if transfer.from_user_id == transfer.to_user_id:
            logger.error(f"Запрещено переводить средства самому себе. Id пользователя - {transfer.from_user_id}")
            return JSONResponse(status_code=400,
                                content={"error": "Запрещено переводить средства самому себе."})

        async with JobDb() as connector:
            check_from_wallet = await connector.fetchrow(sql.CHECK_WALLET, transfer.from_user_id)
            if check_from_wallet is not None:
               if transfer.amount > check_from_wallet["user_balance"]:
                   logger.error(f"Попытка списать с баланса кошелька пользователя id - {transfer.from_user_id} сумму превышающую имеющийся баланс")
                   return JSONResponse(status_code=400,
                                       content={"error": "Баланса кошелька не хватает для списания указанной суммы."})
            else:
               logger.error(f"Не найден пользователь id - {transfer.from_user_id} для списания средств")
               return JSONResponse(status_code=400,
                                   content={"error": "Не удается найти пользователя для списания средств."})
            check_to_wallet = await connector.fetchrow(sql.CHECK_WALLET, transfer.to_user_id)
            if check_to_wallet is None:
               logger.error(f"Не найден пользователь id - {transfer.to_user_id} для пополнения средств")
               return JSONResponse(status_code=400,
                                   content={"error": "Не удается найти пользователя для пополнения средств."})
            await connector.fetch(sql.UPDATE_BALANCE, check_from_wallet["id"], check_from_wallet["user_balance"] - transfer.amount)
            await connector.fetch(sql.UPDATE_BALANCE, check_to_wallet["id"], check_to_wallet["user_balance"] + transfer.amount)
            await connector.fetch(sql.CREATE_TRANSFER, transfer.from_user_id, check_to_wallet["id"], check_from_wallet["id"], check_to_wallet["user_balance"], transfer.amount, check_to_wallet["user_balance"] + transfer.amount, datetime.now())
            await connector.fetch(sql.CREATE_TRANSFER, transfer.from_user_id, check_from_wallet["id"], check_to_wallet["id"], check_from_wallet["user_balance"], transfer.amount, check_from_wallet["user_balance"] - transfer.amount, datetime.now())
            logger.error(f"Сумма {transfer.amount} успешно переведена с кошелька {check_from_wallet['id']} в кошелек {check_to_wallet['id']}")
            return JSONResponse(status_code=400,
                                content={"answer": "Средства успешно переведены."})

    except Exception as e:
        logger.error(f"Получено исключение при исполнении кода {e}")
        return JSONResponse(status_code=500,
                            content={"error": "Ошибка: Во время получения списка пользователей произошла ошибка."})
