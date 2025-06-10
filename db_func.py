import aiosqlite
import os

cwd = os.getcwd()+"\\TBOT\\"
DB_NAME = cwd+'quiz_bot.db'

async def create_table():
  async with aiosqlite.connect(DB_NAME) as db:
    await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state \
                     (user_id INTEGER PRIMARY KEY, question_index INTEGER, \
                     total_played INTEGER, total_right_answers INTEGER, \
                     total_questions INTEGER, last_game INTEGER)''')
    await db.commit()

async def add_user(user_id):
  async with aiosqlite.connect(DB_NAME) as db:
    async with db.execute('SELECT user_id FROM quiz_state WHERE user_id = ?', (user_id, )) as cursor:
      results = await cursor.fetchone()
      if results is None:
        await db.execute('INSERT INTO quiz_state (user_id, question_index, total_played, total_right_answers, total_questions, last_game) \
                         VALUES (?, ?, ?, ?, ?, ?)', (user_id, 0, 0, 0, 0, 0))
        await db.commit()

async def get_quiz_index(user_id):
  async with aiosqlite.connect(DB_NAME) as db:
    async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id, )) as cursor:
      results = await cursor.fetchone()
      if results is not None:
        return results[0]
      else:
        return 0

async def update_quiz_index(user_id, index):
  async with aiosqlite.connect(DB_NAME) as db:
    await db.execute('UPDATE quiz_state SET question_index = ? \
                     WHERE user_id = ?', (index, user_id))
    await db.commit()

async def get_statistics(user_id):
  async with aiosqlite.connect(DB_NAME) as db:
    async with db.execute('SELECT total_played, total_right_answers, total_questions, last_game FROM quiz_state WHERE user_id = ?', (user_id, )) as cursor:
      results = await cursor.fetchone()
      if results is not None:
        return list(results)
      else:
        return [0, 0, 0, 0]

async def update_statistics(user_id, tp, tra, tq, lg):
  async with aiosqlite.connect(DB_NAME) as db:
    await db.execute('UPDATE quiz_state SET total_played = ?, total_right_answers = ?, total_questions = ?, last_game = ? \
                     WHERE user_id = ?', (tp, tra, tq, lg, user_id))
    await db.commit()