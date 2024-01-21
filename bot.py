import os
from dotenv import load_dotenv
import telebot
from telebot import types
import django
django.setup()
from django.core.exceptions import AppRegistryNotReady 
from user.models import User, Order, Food
from django.shortcuts import get_object_or_404

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}
shopping_cart = {}

admin_id = "5867186069"


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        user_id = str(message.from_user.id)
        user_exists = User.objects.all()
        user_all = [str(i.user_id) for i in user_exists]
        if user_id not in user_all:
            new_user = User(user_id=user_id, first_name=message.from_user.first_name, last_name=message.from_user.last_name)
            new_user.save()

            # Inline keyboard yaratish
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(" 🛒 Buyurtma berish", callback_data='order'),
            types.InlineKeyboardButton(" 🛍 Mening buyrutmalarim", callback_data='my_orders'),
            types.InlineKeyboardButton(" 🗑 Savatcha", callback_data='cart'),
            types.InlineKeyboardButton(" 📞 Support", callback_data='support'),
        ]
        keyboard.add(*buttons)
        bot.send_message(user_id, "Assalomu alaykum! Tanlang:", reply_markup=keyboard)
    except AppRegistryNotReady:
        pass

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    user_id = call.from_user.id

    if call.data == 'order':
        if str(user_id) not in shopping_cart:
            bot.send_message(user_id, "Ismingizni kirting: ")
            bot.register_next_step_handler(call.message, get_user_info)
        else:
            menu_keyboard = types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            foods = Food.objects.all()

            for i in foods:
                buttons.append(types.InlineKeyboardButton(text=i.name, callback_data=f"food_{i.id}"))
                if len(buttons) % 2 == 0:  # Qatorga tugmalar chiqarish uchun
                    menu_keyboard.add(*buttons)
                    buttons = []
            menu_keyboard.add(*buttons)
            menu_keyboard.add(types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'))
            menu_keyboard.add(types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqaga"))
            bot.send_message(user_id, "Tanlang", reply_markup=menu_keyboard)


    elif call.data == 'my_orders':
        userid = str(call.from_user.id)
        user = User.objects.get(user_id=userid)
        menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton('⬅️ Orqaga', callback_data="orqaga"),
        ]
        menu_keyboard.add(*buttons)
        try:
            order = Order.objects.filter(user_id=user)
            b = "Buyurtmalar: \n"
            if order.exists():
                for order in order:
                    b += f"{order.description} \n \n"
                bot.send_message(userid, b, reply_markup=menu_keyboard)

            else:
                bot.send_message(userid, "Buyurtmalar mavjud emas!")
                
        except:
            bot.send_message(user_id, "Buyurtmalar mavjud emas!")
       
    elif call.data == 'cart':

        user_id = str(call.from_user.id)
        if user_id in shopping_cart:
            a = 'Foydalanuvchi buyurmasi:\n'
            b = 0
            for i in shopping_cart[user_id]["food"]:
                foodd = i["food_id"]
                quantity = i["quantity"]
                food = Food.objects.get(id=foodd)
                a += f"{food.name} X {quantity}  {food.price * int(quantity)} so'm\n"
                b += food.price * int(quantity) 
            a += f"Ummumiy suma: {b} so'm"

            menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton('⬅️ Orqaga', callback_data="orqaga"),
                types.InlineKeyboardButton(" 📩 Buyurtma berish", callback_data=f'byurtma_{user_id}'),
            ]
            menu_keyboard.add(*buttons)

            bot.send_message(user_id, a, reply_markup=menu_keyboard)
        else:
            menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton('⬅️ Orqaga', callback_data="orqaga"),
            ]
            menu_keyboard.add(*buttons)
            bot.send_message(user_id, "Savad bo'sh 😟", reply_markup=menu_keyboard)
        

    elif call.data.startswith("byurtma_"):
        user_i = call.data.split('_')[1]
        user = get_object_or_404(User, user_id=user_i)
        a = 'Foydalnuvhi buyurmasi:\n'
        b = 0
        for i in shopping_cart[user_i]["food"]:
            foodd = i["food_id"]
            quantity = i["quantity"]
            food = Food.objects.get(id=foodd)
            a += f"{food.name} X {quantity}\n"
            b += food.price * int(quantity)
        a += f"Ummumiy suma: {b}"

        order = Order.objects.create(
            user_id=user,
            name=user_data[int(user_i)]['name'],
            description=a,
            phone_number=user_data[int(user_i)]['phone'],
            total_price=b
        )
        order.save()

        menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton('⬅️ Orqaga', callback_data="orqaga"),
        ]
        menu_keyboard.add(*buttons)
        m_keyboard = types.InlineKeyboardMarkup(row_width=1)
        button = [
            types.InlineKeyboardButton('Byurtmani qabul qilish', callback_data=f"qabul_{user_i}"),
        ]
        m_keyboard.add(*button)
        a += f"\nFoydalanuvchi: {user_data[int(user_i)]['name']} \n Telefon raqami: {user_data[int(user_i)]['phone']}"
        bot.send_message(user_i, "Byurtangiz Ko'ribchiqilmoqda!", reply_markup=menu_keyboard)
        bot.send_message(admin_id, a, reply_markup=m_keyboard)




    elif call.data == 'support':
        menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
        menu_keyboard.add(types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqaga"))
        bot.send_message(user_id, "Aloqa uchun telefon raqami: 📞 +998330232002:", reply_markup=menu_keyboard)

    elif call.data.startswith('food_'):
        food_id = call.data.split('_')[1]
        food = Food.objects.get(id=food_id)
        current_quantity = 1
        # Rasm yuborish uchun ketmaket tugmalarni yaratish
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [
            types.InlineKeyboardButton('-', callback_data=f"dummy_callback_data"),
            types.InlineKeyboardButton('1', callback_data=f"dummy_callback_data"),  
            types.InlineKeyboardButton('+', callback_data=f"change_quantity_{food.id}_plus_{current_quantity}"),
            types.InlineKeyboardButton("🗑 Savatga 📥", callback_data=f"savad_{user_id}_{food.id}_{current_quantity}"),
            types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'),
            types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqa"),
        ]
        markup.add(*buttons)

        # Rasmni yuborish va tugmani biriktirish
        bot.send_photo(user_id, photo=food.image, caption=f"Tanlangan taom: {food.name}\nTavsifi: {food.description}\nNarxi: {food.price} so'm", reply_markup=markup)
        
    elif call.data.startswith('change_quantity'):
        # Tugmani bosganda sonni o'zgartirish
        food_id, operation, current_quantity = call.data.split('_')[2:]
        food = Food.objects.get(id=food_id)
        current_quantity = int(current_quantity)

        if operation == 'plus':
            current_quantity += 1
        elif operation == 'minus' and current_quantity > 1:    
            current_quantity -= 1 

        if current_quantity == 1:
            markup = types.InlineKeyboardMarkup(row_width=3)
            buttons = [
                types.InlineKeyboardButton('-', callback_data=f"dummy_callback_data"),
                types.InlineKeyboardButton(str(current_quantity), callback_data='dummy_callback_data'),
                types.InlineKeyboardButton('+', callback_data=f"change_quantity_{food.id}_plus_{current_quantity}"),
                types.InlineKeyboardButton("🗑 Savatga 📥", callback_data=f"savad_{user_id}_{food.id}_{current_quantity}"),
                types.InlineKeyboardButton(" 🗑 Savatcha", callback_data='cart'),
                types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqa"),
            ]
            markup.add(*buttons)

            new_caption = f"Tanlangan taom: {food.name}\nTavsifi: {food.description}\nNarxi: {food.price} so'm"
        else:
            markup = types.InlineKeyboardMarkup(row_width=3)
            buttons = [
                types.InlineKeyboardButton('-', callback_data=f"change_quantity_{food.id}_minus_{current_quantity}"),
                types.InlineKeyboardButton(str(current_quantity), callback_data='dummy_callback_data'),
                types.InlineKeyboardButton('+', callback_data=f"change_quantity_{food.id}_plus_{current_quantity}"),
                types.InlineKeyboardButton("🗑 Savatga 📥", callback_data=f"savad_{user_id}_{food.id}_{current_quantity}"),
                types.InlineKeyboardButton(" 🗑 Savatcha", callback_data='cart'),
                types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqa"),
            ]
            markup.add(*buttons)

            new_caption = f"Tanlangan taom: {food.name}\nTavsifi: {food.description}\nNarxi: {food.price} so'm"
        
        current_caption = call.message.caption
        current_markup = call.message.reply_markup

        if current_caption != new_caption or current_markup is None or current_markup != markup:
            bot.edit_message_caption(
                caption=new_caption,
                chat_id=user_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            bot.send_photo(user_id, photo=food.image, caption=new_caption, reply_markup=markup)

    elif call.data == 'orqaga':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(" 🛒 Buyurtma berish", callback_data='order'),
            types.InlineKeyboardButton(" 🛍 Mening buyrutmalarim", callback_data='my_orders'),
            types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'),
            types.InlineKeyboardButton(" 📞 Support", callback_data='support'),
        ]
        keyboard.add(*buttons)
        bot.send_message(user_id, "Tanlang:", reply_markup=keyboard)

    elif call.data == 'orqa':
        menu_keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        foods = Food.objects.all()

        for i in foods:
            buttons.append(types.InlineKeyboardButton(text=i.name, callback_data=f"food_{i.id}"))
            if len(buttons) % 2 == 0:  # Qatorga tugmalar chiqarish uchun
                menu_keyboard.add(*buttons)
                buttons = []
        menu_keyboard.add(types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'))
        menu_keyboard.add(types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqaga"))

        bot.send_message(user_id, "Tanlang", reply_markup=menu_keyboard)

    elif call.data.startswith('savad'):
        user_id, food_id, current_quantity = call.data.split('_')[1:]

        current_quantity = int(current_quantity)

        if user_id not in shopping_cart:
            shopping_cart[user_id] = {"food": []}

        shopping_cart[user_id]["food"].append({"food_id": food_id, "quantity": current_quantity})
        
        menu_keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        foods = Food.objects.all()

        for i in foods:
            buttons.append(types.InlineKeyboardButton(text=i.name, callback_data=f"food_{i.id}"))
            if len(buttons) % 2 == 0:  # Qatorga tugmalar chiqarish uchun
                menu_keyboard.add(*buttons)
                buttons = []
        menu_keyboard.add(*buttons)
        menu_keyboard.add(types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'))
        menu_keyboard.add(types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqaga"))

        bot.send_message(user_id, "Tanlang", reply_markup=menu_keyboard)

    elif call.data.startswith('qabul_'):
        user_idd = call.data.split('_')[1]
        bot.send_message(user_idd, "Byurtma qabul qilindi!")

        a = 'Foydalanuvchi buyurmasi:\n'
        b = 0
        for i in shopping_cart[user_idd]["food"]:
            foodd = i["food_id"]
            quantity = i["quantity"]
            food = Food.objects.get(id=foodd)
            a += f"{food.name} X {quantity}\n"
            b += food.price * int(quantity)
        a += f"Ummumiy suma: {b}"
        m_keyboard = types.InlineKeyboardMarkup(row_width=1)
        button = [
            types.InlineKeyboardButton('Tayyor', callback_data=f"tayor_{user_idd}"),
        ]
        m_keyboard.add(*button)
        a += f"\n Foydalanuvchi: {user_data[int(user_idd)]['name']} \n Telefon raqami: {user_data[int(user_idd)]['phone']}"

        try:
            
            bot.edit_message_caption(
                caption=a,
                chat_id=admin_id,
                message_id=call.message.message_id,
                reply_markup=m_keyboard
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "there is no caption in the message to edit" in str(e):
               
                bot.edit_message_text(
                    text=a,
                    chat_id=admin_id,
                    message_id=call.message.message_id,
                    reply_markup=m_keyboard
                )
        del shopping_cart[str(user_idd)]

    elif call.data.startswith('tayor_'):
        user_idd = call.data.split('_')[1]
        bot.send_message(user_idd, "Byurtmangiz Tayyor!")

    else:
        # Qo'shimcha malumotlar chiqarish
        pass


def get_user_info(message):
    user_id = message.from_user.id
    user_data[user_id] = {'name': message.text}

    bot.send_message(user_id, "Telefon raqamingizni yuboring:")
    bot.register_next_step_handler(message, get_user_phone)

def get_user_phone(message):
    user_id = message.from_user.id

   
    if user_id in user_data and 'name' in user_data[user_id]:
        user_data[user_id]['phone'] = message.text

        menu_keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        foods = Food.objects.all()

        for i in foods:
            buttons.append(types.InlineKeyboardButton(text=i.name, callback_data=f"food_{i.id}"))
            if len(buttons) % 2 == 0:  # Qatorga tugmalar chiqarish uchun
                menu_keyboard.add(*buttons)
                buttons = []
        menu_keyboard.add(*buttons)
        menu_keyboard.add(types.InlineKeyboardButton(' 🗑 Savatcha', callback_data='cart'))
        menu_keyboard.add(types.InlineKeyboardButton('⬅️ orqaga', callback_data="orqaga"))

        bot.send_message(user_id, "Tanlang", reply_markup=menu_keyboard)
    else:
        bot.send_message(user_id, "Iltimos, ismingizni kiritib o'ting.")
        bot.register_next_step_handler(message, get_user_info)

bot.polling()