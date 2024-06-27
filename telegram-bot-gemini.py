import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

TOKEN: Final = 'token'
BOT_USERNAME: Final = 'token_user'

Gemini_Key = "key"
genai.configure(api_key=Gemini_Key)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)

chat_session = model.start_chat(
    history=[
    ]
)

# Comandos
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Olá, como posso te ajudar?')

# Escopo
def handle_response(text: str) -> str:
    response = chat_session.send_message(text)
    return response.text

# Respostas que voltam para o usuário
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type  # Formato de grupo ou privado
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            await update.message.reply_text(response)
        else:
            return
    else:  # Chat privado
        response: str = handle_response(text)
        await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# função com comandos para iniciar o bot
def main():

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start_command))

    # messages
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # errors
    application.add_error_handler(error)

    print("Começando...")
    application.run_polling(poll_interval=3) 

# inicialização do bot
if __name__ == '__main__':
    main()
