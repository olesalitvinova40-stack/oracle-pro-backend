import os
import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, PreCheckoutQuery, LabeledPrice
from openai import AsyncOpenAI

# 1. ТОЧНАЯ НАСТРОЙКА ДАННЫХ ПРОЕКТА
API_TOKEN = os.getenv("BOT_TOKEN", ""
WEBAPP_URL = 'https://tiiny.site'

# Считываем ключ OpenAI из настроек сервера в целях безопасности
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PREMIUM_PRICE_STARS = 15 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

EXPERT_SYSTEM_PROMPT = (
    "Вы — легендарный потомственный эзотерик, практикующий рунолог, таролог и юнгианский "
    "психотерапевт с 30-летним международным стажем. Ваша цель — давать глубокие, точные, "
    "духовные и терапевтические толкования. Говорите на языке архетипов, раскрывайте кармические уроки, "
    "и давайте мудрые психологические советы. Оформляйте ответ структурировано, используя разметку Markdown."
)

async def on_startup(bot: Bot):
    bot_user = await bot.get_me()
    logging.info(f"Бот @{bot_user.username} успешно запущен в облаке!")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="🔮 Войти в Супер-Хаб Oracle Pro", web_app=WebAppInfo(url=WEBAPP_URL))]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(
        f"Приветствую вас в сакральном пространстве, {message.from_user.first_name}.\n\n"
        "**Oracle Pro** — это премиальный эзотерический хаб, где технологии ИИ "
        "объединены с вековой мудростью Таро и Скандинавских Рун.\n\n"
        "Нажмите кнопку ниже, чтобы запустить Оракул.",
        reply_markup=keyboard, parse_mode="Markdown"
    )

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        payload = json.loads(raw_data)
        invoice_payload = json.dumps(payload)
        prices = [LabeledPrice(label="XTR", amount=PREMIUM_PRICE_STARS)]
        await message.answer_invoice(
            title="Премиальное ИИ-толкование",
            description="Развернутый метафизический анализ вашей ситуации от мастера с 30-летним стажем.",
            prices=prices, provider_token="", currency="XTR", payload=invoice_payload
        )
    except Exception as e:
        await message.answer("Пространство перегружено. Пожалуйста, повторите запрос в приложении.")

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    await message.answer("✨ Настраиваю ментальную связь, ИИ генерирует ваш разбор (10-15 секунд)...")
    try:
        payload = json.loads(message.successful_payment.invoice_payload)
        tool = payload.get('tool')
        elements = payload.get('elements', [])
        category = payload.get('category', 'Общий срез судьбы')
        
        user_prompt = f"Тема: {category}. Инструмент: {tool}. Выпавшие элементы: {elements}. Дай глубокий разбор."
        response = await ai_client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "system", "content": EXPERT_SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
        )
        await message.answer(response.choices.message.content, parse_mode="Markdown")
    except Exception as e:
        await message.answer("Произошел временный разрыв связи с ИИ. Ваши Звезды сохранены.")

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
