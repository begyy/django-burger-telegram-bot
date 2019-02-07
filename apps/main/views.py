from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from apps.product.models import Product
from apps.order.models import Order,OrderProduct
from apps.category.models import SubCategory,Category
from apps.telegram_users.models import Telegram
import telebot
from telebot.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton,InlineKeyboardButton,\
    InlineKeyboardMarkup,InlineQueryResultArticle,InputTextMessageContent,InlineQueryResultPhoto

from time import time
bot = telebot.TeleBot('621225718:AAGLhFWrQ_tG7gQZrlyIhAzRpkP0kEf9vBE')
channel_id = -1001405694895


@csrf_exempt
def update_bot(request):
    if request.method == 'POST':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return HttpResponse('OK')


def products(request,pk):
    product = Product.objects.get(id=pk)
    context = {"name":product.name,"price":product.price,"description":product.description,"photo":product.photo_url}
    return render (request,'products.html',context=context)


class Controler:
    def __init__(self,telegram_id=None,first_name=None,last_name=None,username=None,phone=None,text=None,product_id=None,secret_key=None,message_id=None,
                 order_product_id=None,latitude=None,longitude=None, channel_id=None):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.text = text
        self.product_id = product_id
        self.secret_key = secret_key
        self.message_id = message_id
        self.order_product_id =order_product_id
        self.latitude = latitude
        self.longitude = longitude
        self.channel_id = channel_id

    def start(self):
        self.signup()
        print(self.telegram_id)
        bot.send_message(self.telegram_id,'Привет',reply_markup=self.category())

    def signup(self):
        user,create = Telegram.objects.get_or_create(telegram_id=self.telegram_id)
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.username = self.username
        user.step = 1
        user.save()

    def category(self):
        array = []
        key = ReplyKeyboardMarkup(True,False,row_width=2)
        category = Category.objects.all()
        for i in category:
            array.append(KeyboardButton(i.title))
        order = KeyboardButton('Мой закази')
        feedback = KeyboardButton('Оставит отзыв')
        key.add(order, feedback)
        key.add(*array)
        return key

    def subcategory(self):
        array = []
        key = ReplyKeyboardMarkup(True,False,row_width=2)
        subcategory = SubCategory.objects.filter(category__title=self.text)
        for i in subcategory:
            array.append(KeyboardButton(i.name))
        back = KeyboardButton('⬅️назад')
        key.add(back)
        key.add(*array)
        return key

    def send_channel_order(self):
        inline,text = self.order_product_key()
        order = Order.objects.get(user__telegram_id=self.telegram_id,status='new')
        order.status = 'processing'
        order.save()
        key = InlineKeyboardMarkup()
        checkout = InlineKeyboardButton(text='✅ Оформить',callback_data='checkout_id'+str(order.pk))
        cancel = InlineKeyboardButton(text='❌ Отменить',callback_data='cancel_id'+str(order.pk))
        status = InlineKeyboardButton(text="Статус: "+order.status, callback_data='status')
        key.add(checkout,cancel)
        key.add(status)
        text += '\n'+ '📞Номер: '+order.phone
        bot.send_message(channel_id,text,parse_mode='HTML',reply_markup=key)


    def product(self):
        inline = InlineKeyboardMarkup()
        get = Product.objects.get(category__name=self.text)
        secret_key = '1'+'%'+str(get.price)+'%'+str(get.pk)  #quantity and price and product_id
        plus = InlineKeyboardButton(text='➕',callback_data='+'+secret_key)
        minus = InlineKeyboardButton(text='➖',callback_data='-'+secret_key)
        buy = InlineKeyboardButton(text="добовит 🛒",callback_data='buy'+secret_key)
        quantity = InlineKeyboardButton(text='1',callback_data='*'+secret_key)
        total = InlineKeyboardButton(text=str(get.price)+" сум",callback_data='total')
        inline.add(plus,quantity,minus)
        inline.add(total)
        inline.add(buy)
        bot.send_photo(self.telegram_id,get.photo_url,get.description,reply_markup=inline)


    def check_subcategory(self):

        get = SubCategory.objects.filter(category__title=self.text)
        if not get:
            return False
        else:
            return True

    def check_product(self):
        try:
            get = Product.objects.get(category__name=self.text)
            return True
        except Product.DoesNotExist:
            return False

    def plus_quantity_product(self):
        inline = InlineKeyboardMarkup()
        text = self.secret_key.split('%') #quantity and price and product_id
        get = Product.objects.get(pk=int(text[2]))
        quantity_plus = int(text[0]) + 1
        total_price = quantity_plus * get.price
        secret_key = str(quantity_plus)+'%'+str(get.price)+'%'+str(get.pk)
        plus = InlineKeyboardButton(text='➕', callback_data='+' + secret_key)
        minus = InlineKeyboardButton(text='➖', callback_data='-' + secret_key)
        buy = InlineKeyboardButton(text='добовит 🛒', callback_data='buy' + secret_key)
        quantity = InlineKeyboardButton(text=str(quantity_plus), callback_data='*' + secret_key)
        total = InlineKeyboardButton(text=str(total_price) + ' сум', callback_data='total')
        inline.add(plus, quantity, minus)
        inline.add(total)
        inline.add(buy)
        bot.edit_message_reply_markup(self.telegram_id,self.message_id,reply_markup=inline)



    def minus_quantity_product(self):
        inline = InlineKeyboardMarkup()
        text = self.secret_key.split('%') #quantity and price and product_id
        if int(text[0]) == 1:
            return False
        else:
            get = Product.objects.get(pk=int(text[2]))
            quantity_plus = int(text[0]) - 1
            total_price = quantity_plus * get.price
            secret_key = str(quantity_plus)+'%'+str(get.price)+'%'+str(get.pk)
            plus = InlineKeyboardButton(text='➕', callback_data='+' + secret_key)
            minus = InlineKeyboardButton(text='➖', callback_data='-' + secret_key)
            buy = InlineKeyboardButton(text='добовит 🛒', callback_data='buy' + secret_key)
            quantity = InlineKeyboardButton(text=str(quantity_plus), callback_data='*' + secret_key)
            total = InlineKeyboardButton(text=str(total_price)+ ' сум', callback_data='total')
            inline.add(plus, quantity, minus)
            inline.add(total)
            inline.add(buy)
            bot.edit_message_reply_markup(self.telegram_id, self.message_id, reply_markup=inline)

    def buy_product(self):
        text = self.secret_key.split('%')
        create = OrderProduct.objects.create(order=self.new_order(),quantity=int(text[0]),product=self.get_product(int(text[2])))

    def new_order(self):
        get,create = Order.objects.get_or_create(user=self.user(),status='new')
        return get

    def get_product(self,id=None):
        return Product.objects.get(pk=id)

    def success_order(self):
        key =InlineKeyboardMarkup()
        yes = InlineKeyboardButton(text='✅',callback_data='yes')
        no = InlineKeyboardButton(text='❌',callback_data='no')
        order = Order.objects.get(user__telegram_id=self.telegram_id,status='new')
        inline,text = self.order_product_key()
        text+= '\n' + '\n'+'<b>' +'📞 номер : ' + order.phone + '\n' + '📍 адрес: '+'Прикреплено' +'\n'+ '\n'+'Вы поддерживайте ваш заказ?' +'</b>'
        key.add(no,yes)
        bot.send_message(self.telegram_id,text,reply_markup=key,parse_mode='HTML')

    def validation_number(self):
        if len(self.text) == 10:
            code = ['99','94','93','92','90','98','97','71','72']
            text = self.text.split()
            if text[0] in code:
                try:
                    int(text[1])
                    return True
                except:
                    return False
        else:
            return False


    def order_product_key(self):
        total_price = 0
        text = '------------------------------' +'\n'
        inline = InlineKeyboardMarkup()
        order_product = OrderProduct.objects.filter(order=self.new_order())
        clear = InlineKeyboardButton(text='Очистить ♻️',callback_data='clear')
        inline.add(clear)
        for i in order_product:
            total_price+=i.product.price *i.quantity
            total = i.product.price * i.quantity
            text += '<b>'+ str(i.product.name)+' '+str(i.product.price) + '  x' + str(i.quantity)+ ' ='+str(total)+ '</b>' + "\n"
        text+='\n' + '------------------------------'
        text += '\n' + '<b>' + 'Jami: ' + str(total_price)+' сум'+ '</b>'
        order = InlineKeyboardButton(text='✅Оформит заказ',callback_data='order')
        inline.add(order)

        return inline,text

    def order_product(self):
        get= Telegram.objects.get(telegram_id=self.telegram_id)
        get.step = 9
        get.save()
        inline,text = self.order_product_key()
        key = ReplyKeyboardMarkup(True, False)
        key.add(KeyboardButton('Главный меню'))
        bot.send_message(self.telegram_id,'Корзина 🛒',reply_markup=key)
        bot.send_message(self.telegram_id,text,reply_markup=inline,parse_mode='HTML')


    def user(self):
        return Telegram.objects.get(telegram_id=self.telegram_id)

    def home_page(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        get.step = 1
        get.save()
        bot.send_message(self.telegram_id,'Главный меню ',reply_markup=self.category())

    def order_delete(self):
        self.new_order().delete()

    def cancel_order(self):
        get = Order.objects.get(pk=int(self.order_product_id))
        get.status = 'cancel'
        get.save()
        bot.send_message(get.user.telegram_id,'Ваш заказ отменен :(')

    def finished_order(self):
        get = Order.objects.get(pk=int(self.order_product_id))
        get.stats = 'finished'
        get.save()
        bot.send_message(get.user.telegram_id,'📌 Ваш заказ почти готов скора будет к вам доставлена')

    def checkout(self):
        get = OrderProduct.objects.filter(order=self.new_order())
        if not get:
            bot.answer_callback_query(self.message_id,text='Ваш корзина пустой')
        else:
            user = Telegram.objects.get(telegram_id=self.telegram_id)
            if user.step == 9:
                user.step = 5
                user.save()
                self.contact()


    def contact(self):
        text = 'Пожалуста отравите  контакт или  напишите номер.  пример :99 8158172 ‼️'
        key = ReplyKeyboardMarkup(True,False)
        key.add(KeyboardButton('Отправить контакт 📲',request_contact=True))
        key.add(KeyboardButton('⬅️назад '))
        bot.send_message(self.telegram_id,text,reply_markup=key)

    def location(self):
        text = 'Отправьте локация или напишите сами. пример :    Яшнобод Кадишва 6 дом'
        key = ReplyKeyboardMarkup(True,False)
        key.add(KeyboardButton('📍 Отправить локация',request_location=True))
        key.add(KeyboardButton('⬅️назад '))
        bot.send_message(self.telegram_id,text,reply_markup=key)

    def save_contact(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        if get.step == 5:
            order = Order.objects.get(user__telegram_id=self.telegram_id,status='new')
            order.phone = self.phone
            order.save()
            bot.send_message(self.telegram_id,'✅ Ваш номер успешно сохранено')
            get.step =6
            get.save()
            self.location()

    def save_location(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        if get.step == 6:
            order = Order.objects.get(user__telegram_id=self.telegram_id,status='new')
            order.latitude = self.latitude
            order.longitude = self.longitude
            order.address = None
            order.save()
            bot.send_message(self.telegram_id,'✅ Ваш локация успешно сохранено ',reply_markup=ReplyKeyboardRemove())
            get.step = 7
            get.save()
            self.success_order()

    def save_reply_message_id(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        get.step = 20
        get.text = self.text
        get.save()

    def order_update_status(self, status, order_id):
        order = Order.objects.get(pk=int(order_id))
        order.status = status
        order.save()
        key = InlineKeyboardMarkup()
        checkout = InlineKeyboardButton(text='✅ Оформить', callback_data='checkout_id' + str(order.pk))
        cancel = InlineKeyboardButton(text='❌ отменить', callback_data='cancel_id' + str(order.pk))
        status_btn = InlineKeyboardButton(text="Статус: " + order.status, callback_data='status')
        key.add(checkout, cancel)
        key.add(status_btn)
        bot.edit_message_reply_markup(self.channel_id, self.message_id, reply_markup=key)

    def leave_feedback(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        get.step = 8
        get.save()
        key = ReplyKeyboardMarkup(True, False)
        key.row("⬅️назад")
        bot.send_message(self.telegram_id, 'Пожалуйста напишите что нибудь отзыв! 💬', reply_markup=key)

    def send_leave_feedback(self):
        reply_key = 'reply'+str(self.telegram_id) +'%' + str(self.message_id)
        key = InlineKeyboardMarkup()
        reply = InlineKeyboardButton(text='Ответить ',callback_data=str(reply_key))
        self.text += '\n' + 'telegram_id: ' +str(self.telegram_id)
        key.add(reply)
        bot.send_message(channel_id,self.text,reply_markup=key)
        bot.send_message(self.telegram_id,'Ваш отзыв успешно отправлено ☑️', reply_markup=self.category())

    def send_replay_message(self):
        bot.send_message(self.telegram_id, 'Напишите ответ что нибудь 💬')

    def send_admin_send_reply_message(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        text = get.text.split('%')
        bot.send_message(int(text[0]),reply_to_message_id=int(text[1]),text=self.text)
        bot.send_message(self.telegram_id,'Ваше сообщение отправлено ✅')
        get.step = 1
        get.text = None
        get.save()

    def main(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        if get.step == 1:
            if self.check_subcategory():
                get.step = 2
                get.text = self.text
                get.save()
                bot.send_message(self.telegram_id,self.text,reply_markup=self.subcategory())
        elif get.step == 2:
            if self.check_product():
                get.text = self.text
                get.save()
                self.product()
        elif get.step == 5:
            if self.validation_number():
                self.phone = self.text
                self.save_contact()
                get.step = 6
                get.save()
            else:
                text = '‼️ Вы неправильно отправили номер пример :99 8158172'
                bot.send_message(self.telegram_id,text)
        elif get.step == 6:
            order = Order.objects.get(user__telegram_id=self.telegram_id,status='new')
            order.address = self.text
            order.latitude = None
            order.longitude = None
            order.save()
            inline,text = self.order_product_key()
            bot.send_message(self.telegram_id,'Ваш адрес успешно сохранено',reply_markup=ReplyKeyboardRemove())
            text+='\n' + '\n'+'<b>' +'📞 номер : ' + order.phone + '\n' + '📍 адрес: '+self.text +'\n'+ '\n'+'Вы поддерживайте ваш заказ?' +'</b>'
            key = InlineKeyboardMarkup()
            yes = InlineKeyboardButton(text='✅', callback_data='yes')
            no = InlineKeyboardButton(text='❌', callback_data='no')
            key.add(no,yes)
            bot.send_message(self.telegram_id,text,reply_markup=key,parse_mode='HTML')
            get.step = 7
            get.save()
        elif get.step == 8:
            self.send_leave_feedback()
            get.step =1
            get.save()
        elif get.step == 20:
            self.send_admin_send_reply_message()



    def back_step(self):
        get = Telegram.objects.get(telegram_id=self.telegram_id)
        if get.step == 6:
            self.contact()
            get.step =5
            get.save()
        elif get.step == 5:
            inline,text = self.order_product_key()
            get.step = 9
            get.save()
            key = ReplyKeyboardMarkup(True,False)
            key.add(KeyboardButton('Главный меню'))
            bot.send_message(self.telegram_id,'Корзина 🛒',reply_markup=key)
            bot.send_message(self.telegram_id,text,reply_markup=inline,parse_mode='HTML')
        elif get.step == 2:
            get.step = 1
            get.save()
            bot.send_message(self.telegram_id,'Главный меню',reply_markup=self.category())
        elif get.step == 8:
            get.step = 1
            get.save()
            bot.send_message(self.telegram_id,'Главный меню',reply_markup=self.category())




@bot.message_handler(commands=['start'])
def start(message):
    print(message.chat.id)
    Controler(telegram_id=message.chat.id,
              username=message.from_user.username,first_name=message.from_user.first_name,last_name=message.from_user.last_name).start()

@bot.message_handler(content_types='text')
def send_message(message):
    print(message.chat.id)
    if message.text == '⬅️назад':
        Controler(telegram_id=message.chat.id).back_step()
    elif message.text == 'Мой закази':
        Controler(telegram_id=message.chat.id).order_product()
    elif message.text == 'Главный меню':
        Controler(telegram_id=message.chat.id).home_page()
    elif message.text == 'Оставит отзыв':
        Controler(telegram_id=message.chat.id).leave_feedback()
    else:
        Controler(telegram_id=message.chat.id,text=message.text,message_id=message.message_id).main()

@bot.message_handler(content_types='contact')
def user_send_contact(message):
    Controler(telegram_id=message.chat.id,phone=message.contact.phone_number).save_contact()

@bot.message_handler(content_types='location')
def user_send_location(message):
    Controler(telegram_id=message.chat.id,latitude=message.location.latitude,longitude=message.location.longitude).save_location()

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data.startswith('+') == True:
        get = Telegram.objects.get(telegram_id=c.message.chat.id)
        if get.step == 2:
            text = c.data.split('+')
            Controler(telegram_id=c.message.chat.id,secret_key=text[1],message_id=c.message.message_id).plus_quantity_product()
        else:
            bot.delete_message(c.message.chat.id,c.message.message_id)
    elif c.data.startswith('-') == True:
        get = Telegram.objects.get(telegram_id=c.message.chat.id)
        if get.step == 2:
            text = c.data.split('-')
            Controler(telegram_id=c.message.chat.id, secret_key=text[1],message_id=c.message.message_id).minus_quantity_product()
        else:
            bot.delete_message(c.message.chat.id,c.message.message_id)
    elif c.data.startswith('buy') == True:
        get = Telegram.objects.get(telegram_id=c.message.chat.id)
        if get.step == 2:
            text = c.data.split('buy')
            Controler(telegram_id=c.message.chat.id, secret_key=text[1]).buy_product()
            bot.answer_callback_query(callback_query_id=c.id, text="Добавлено ")
        else:
            bot.delete_message(c.message.chat.id,c.message.message_id)

    elif c.data.startswith('order') == True:
        print('asd')
        if Telegram.objects.get(telegram_id=c.message.chat.id).step == 9:
            print('qwe')
            Controler(telegram_id=c.message.chat.id,message_id=c.id).checkout()
        else:
            bot.delete_message(c.message.chat.id, c.message.message_id)

    elif c.data.startswith('clear') == True:
        if Telegram.objects.get(telegram_id=c.message.chat.id).step == 9:
            Controler(telegram_id=c.message.chat.id).order_delete()
            bot.delete_message(c.message.chat.id,c.message.message_id)
            bot.answer_callback_query(callback_query_id=c.id,text='Очищена')
        else:
            bot.delete_message(c.message.chat.id,c.message.message_id)
    elif c.data.startswith('yes') == True:
        Controler(telegram_id=c.message.chat.id).send_channel_order()
        bot.delete_message(c.message.chat.id,c.message.message_id)
        bot.answer_callback_query(callback_query_id=c.id,text='Ваш заказ успешно оформлен ждите администратор вам напишет')
        Controler(telegram_id=c.message.chat.id).home_page()
    elif c.data.startswith('checkout_id') == True:
        text =c.data.split('checkout_id')
        Controler(order_product_id=text[1]).finished_order()
        bot.answer_callback_query(callback_query_id=c.id,text='Заказ оформлен')
        Controler(telegram_id=c.from_user.id,message_id=c.message.message_id, channel_id=c.message.chat.id
                  ).order_update_status('finished', text[1])
    elif c.data.startswith('cancel_id') == True:
        text = c.data.split('cancel_id')
        Controler(order_product_id=text[1]).cancel_order()
        bot.answer_callback_query(callback_query_id=c.id,text='Заказ отменон ')
        Controler(telegram_id=c.from_user.id, message_id=c.message.message_id, channel_id=c.message.chat.id
                  ).order_update_status('cancel', text[1])
    elif c.data.startswith('reply') == True:
        text = c.data.split('reply')
        Controler(telegram_id=c.from_user.id,text=text[1]).save_reply_message_id()
        bot.answer_callback_query(callback_query_id=c.id,text='отправьте ответ через бот')
    elif c.data.startswith('no') == True:
        bot.delete_message(c.message.chat.id,c.message.message_id)
        bot.answer_callback_query(callback_query_id=c.id,text='Ваш заказ отменен')
        Controler(telegram_id=c.message.chat.id).home_page()




@bot.inline_handler(lambda query: query.query)
def inline_search(inline_query):
    key = InlineKeyboardMarkup()
    channel = InlineKeyboardButton('Перейти бот', url='http://t.me/burgertestbegybot')
    key.add(channel)
    products_array = []
    products = Product.objects.all()
    for all in products:
        inline = InlineQueryResultPhoto(all.pk, all.name, InputTextMessageContent(all.name),reply_markup=key)
        products_array.append(inline)
    bot.answer_inline_query(inline_query.id, products_array)
