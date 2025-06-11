import os
import json
import db_func as db
import main as m
from aiogram import types

cwd = os.getcwd()#+"\\TBOT\\"
with open(cwd+'quiz_data.json', 'r') as file:
  quiz = json.load(file)
quiz_data = quiz.get('quiz', [])

async def next_question(callback: types.CallbackQuery, current_question_index):
  await db.update_quiz_index(callback.from_user.id, current_question_index)
  if current_question_index < len(quiz_data):
    await get_question(callback.message, callback.from_user.id)
  else:
    await callback.message.answer("Это был последний вопрос. Квиз завершен!")

async def get_question(message, user_id):
  current_question_index = await db.get_quiz_index(user_id)
  correct_index = quiz_data[current_question_index]['correct_option']
  opts = quiz_data[current_question_index]['options']
  kb = m.generate_options_keyboard(opts, opts[correct_index])
  await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup = kb)
  stats = await db.get_statistics(user_id)
  total_questions = stats[2] + 1
  await db.update_statistics(user_id, stats[0], stats[1], total_questions, stats[3])

async def new_quiz(message):
  user_id = message.from_user.id
  await db.add_user(user_id)
  current_question_index = 0
  await db.update_quiz_index(user_id, current_question_index)
  await get_question(message, user_id)
  stats = await db.get_statistics(user_id)
  total_played = stats[0] + 1
  await db.update_statistics(user_id, total_played, stats[1], stats[2], 0)

def data():
  return quiz_data