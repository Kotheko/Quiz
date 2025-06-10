import asyncio
import logging
import db_func as db
import quiz as q
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F

logging.basicConfig(level = logging.INFO)
API_TOKEN = '7285655136:AAH-6qsBN5tolTmjTG1tcBcwIp2URg87fEQ'
bot = Bot(token = API_TOKEN)
dp = Dispatcher()

def generate_options_keyboard(answer_options, right_answer):
  builder = InlineKeyboardBuilder()
  for i in range(len(answer_options)):
    builder.add(types.InlineKeyboardButton(
      text = answer_options[i],
      callback_data = str(i) + "#$" + ("right_answer" if answer_options[i] == right_answer else "wrong_answer"))
    )
  builder.adjust(1)
  return builder.as_markup()

@dp.callback_query(F.data.split('#')[1].startswith("$"))
async def show_answer(callback: types.CallbackQuery):
  await callback.bot.edit_message_reply_markup(
    chat_id = callback.from_user.id,
    message_id = callback.message.message_id,
    reply_markup = None
  )
  current_question_index = await db.get_quiz_index(callback.from_user.id)
  answer = q.data()[current_question_index]['options'][int(callback.data.split('#')[0])]
  await callback.message.answer("Ваш ответ: " + answer)
  await asyncio.sleep(2)
  result = callback.data.split('#$')[1]
  if result == "right_answer":
    await right_answer(callback)
  elif result == "wrong_answer":
    await wrong_answer(callback)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
  await callback.message.answer("Верно!")
  current_question_index = await db.get_quiz_index(callback.from_user.id)
  current_question_index += 1
  stats = await db.get_statistics(callback.from_user.id)
  total_right_answers = stats[1] + 1
  last_game = stats[3] + 1
  await db.update_statistics(callback.from_user.id, stats[0], total_right_answers, stats[2], last_game)
  await asyncio.sleep(1)
  await q.next_question(callback, current_question_index)

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
  current_question_index = await db.get_quiz_index(callback.from_user.id)
  correct_option = q.data()[current_question_index]['correct_option']
  await callback.message.answer(f"Неправильно. Правильный ответ: {q.data()[current_question_index]['options'][correct_option]}")
  current_question_index += 1
  await asyncio.sleep(2)
  await q.next_question(callback, current_question_index)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  builder = ReplyKeyboardBuilder()
  builder.add(types.KeyboardButton(text = "Начать игру"))
  await message.answer("Добро пожаловать в квиз!", reply_markup = builder.as_markup(resize_keyboard = True))

@dp.message(Command("stat"))
async def cmd_statistics(message: types.Message):
  stats = await db.get_statistics(message.from_user.id)
  await message.answer(f"Сыграно игр: {stats[0]}")
  await message.answer(f"Всего правильных ответов: {stats[1]} из {stats[2]}")
  await message.answer(f"Последняя игра: {stats[3]} из {len(q.data())}")

@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
  await message.answer(f"Давайте начнем квиз!")
  await q.new_quiz(message)

async def main():
  await db.create_table()
  await dp.start_polling(bot)

if __name__ == "__main__":
  asyncio.run(main())