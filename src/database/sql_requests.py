CHECK_EMAIL = '''
--проверка полученного email от пользователя
SELECT id FROM users WHERE email = $1
'''

CREATE_USER = '''
--создание нового пользователя
INSERT INTO users (name, email, created_at) VALUES ($1, $2, $3) RETURNING id
'''

CREATE_WALLET = '''
--создание кошелька для пользователя
INSERT INTO wallet (user_id, user_balance) VALUES ($1, $2) RETURNING id
'''

GET_USERS = '''
--получение списка всех пользователей
SELECT u.id,
        u.name,
        u.email,
        w.user_balance AS balance
FROM users u
INNER JOIN wallet w ON w.user_id = u.id
'''

CHECK_WALLET = '''
--проверка наличия кошелька
SELECT id, user_balance FROM wallet WHERE user_id = $1

'''

UPDATE_BALANCE = '''
--обновление баланса пользователя
UPDATE wallet SET user_balance = $2 WHERE id = $1
'''

CREATE_TRANSFER = '''
--создание кошелька для пользователя
INSERT INTO transactions (user_id, to_wallet_id, from_wallet_id, before, amount, after, creation_date) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
'''