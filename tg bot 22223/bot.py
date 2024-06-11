import random
import shutil
from pathlib import Path
import json
import sys
def get_config():
    a = open(os.path.dirname(os.path.abspath(__file__))+'/config.json', 'r',encoding='utf-8')
    readed= a.read()
    a.close()
    return json.loads(readed)
import os

import telebot
from telebot import types
bot = telebot.TeleBot(get_config()['TOKEN'])

import os
if not os.path.exists('shop'):
    os.makedirs('shop')
adding_tovar_in_category = {}
creating_new_tovar_info = {}
get_zakaz_info_with_tranzak_number = {}
last_creaded_invoice_TOVAR_AND_CATEGORY = {}
last_opened_tovar_to_rewrite_znach = {}
last_created_invoiceId_in_cryptobot = {}
last_opened_tovar_for_cryptobot = {}
import requests
class CryptoBotApi:
    def __init__(self, token):
        self.token = token
    def getCheks(self):
        r = requests.get('https://pay.crypt.bot/api/getInvoices', headers={'Crypto-Pay-API-Token':self.token},)
        only_with_paid_status = []
        for b in (r.json()['result']['items']):
            if b['status'] == 'paid':
                only_with_paid_status = only_with_paid_status + [b]

        return only_with_paid_status
    def createInvoice(self, sum: int, currency='UAH'):
        r = requests.get('https://pay.crypt.bot/api/createInvoice', headers={'Crypto-Pay-API-Token': self.token},
                         data={"currency_type": "fiat", "fiat": currency, "amount": str(sum),'expires_in': 5*60})
        result = r.json()['result']
        return result



crypto_session = CryptoBotApi(get_config()['cryptobot token'])
if not os.path.exists('descriptions'):
    os.makedirs('descriptions')

if not os.path.exists('last_paid_invoices_cryptobot.txt'):
    a = open('last_paid_invoices_cryptobot.txt', 'w+')
    a.close()


if not os.path.exists('users.txt'):
    a = open('users.txt', 'w+')
    a.close()
def vvel_discription_tovara(message):
    description = message.text
    if description == '/cancel':
        creating_new_tovar_info[message.from_user.id] = {}
        bot.send_message(message.chat.id, '⛔Отменено')
        return

    creating_new_tovar_info[message.from_user.id]['description'] = description
    price = creating_new_tovar_info[message.from_user.id]['price']
    tovar_name = creating_new_tovar_info[message.from_user.id]['name']

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('✅Да', callback_data='yes create tovar'), types.InlineKeyboardButton('⛔Нет', callback_data='no create tovar'))
    bot.send_message(message.chat.id, f'Название: {tovar_name}\n'
                                      f'Цена: {price}\n'
                                      f'Описание: \n{description}\n\n'
                                      f'Создать товар с такими данными? ', reply_markup=markup)

def vvel_price_tovara(message):
    price = message.text
    if price == '/cancel':
        creating_new_tovar_info[message.from_user.id] = {}
        bot.send_message(message.chat.id, '⛔Отменено')
        return
    try:
        price = int(price)
    except ValueError:
        s = bot.send_message(message.chat.id, '⛔Ошибка: не правильно введено число\nВведите цену товара...\n/cancel для отмены')
        bot.register_next_step_handler(s, vvel_price_tovara)
        return


    creating_new_tovar_info[message.from_user.id]['price'] = price

    s = bot.send_message(message.chat.id, 'Введите описание товара...\n/cancel для отмены')
    bot.register_next_step_handler(s, vvel_discription_tovara)


def vvel_name_tovara(message):
    tovar_name = message.text
    if tovar_name == '/cancel':
        bot.send_message(message.chat.id, '⛔Отменено')
        creating_new_tovar_info[message.from_user.id] = {}
        return

    creating_new_tovar_info[message.from_user.id]['name'] = tovar_name

    s = bot.send_message(message.chat.id, 'Введите цену товара...\n/cancel для отмены')
    bot.register_next_step_handler(s, vvel_price_tovara)




def vvel_name_to_new_category(message):
    category_name = message.text
    if category_name != '/cancel':
        if (os.path.exists(f'shop/{category_name}')) and (os.path.exists(f'descriptions/{category_name}')):
            bot.send_message(message.chat.id, '⛔Отменено: такая категория уже существует')
        else:
            os.makedirs(f'shop/{category_name}')
            os.makedirs(f'descriptions/{category_name}')
            bot.send_message(message.chat.id, '✅Успешно создана категория')

    else:
        bot.send_message(message.chat.id, '⛔отменено')


def vvel_card(message):
    card = message.text
    if card == '/cancel':
        bot.send_message(message.chat.id, '⛔Отменено: ввод карты')
        return
    else:
        config = get_config()
        config['card'] = card
        config = str(config).replace("'", '"')
        config = config.replace(',', ',\n')
        a = open(os.path.dirname(os.path.abspath(__file__))+'/config.json', 'w', encoding='utf-8')
        a.write(str(config))
        a.close()
        bot.send_message(message.chat.id, '✅Успешно: обновлена карта')

def get_users():
    a = open('users.txt', 'r')
    readed = a.read()
    a.close()

    return readed.split('\n')


def vvel_text_for_rassilka(message):
    text = message.text
    if text == '/cancel':
        bot.send_message(message.chat.id, '⛔Отменено: рассылка')
        return
    else:
        all_users = get_users()
        sended = 0
        sended_in_chats = []
        for chat_id in all_users:
            try:
                if chat_id not in sended_in_chats:
                    bot.send_message(chat_id=chat_id, text=text)
                    sended +=1
                    sended_in_chats+=[chat_id]
                else:
                    ...
            except:
                ...

        bot.send_message(message.chat.id, f'Успешно отправлено в {sended} чатов')


@bot.message_handler(content_types=['text'])
def text(message):
    if str(message.from_user.id) not in get_users():
        a = open('users.txt', 'a')
        a.write(str(message.from_user.id)+'\n')
        a.close()
    if message.text == '/start':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🛍 Магазин 🛍 ', callback_data='shop'), types.InlineKeyboardButton("⭐️ Инструкция ⭐️", url='https://telegra.ph/Instrukciya-pokupki-04-11'))
        markup.add(types.InlineKeyboardButton('🤷🏻‍♂️ Помощь 🤷🏻‍♂️', url='https://t.me/'+get_config()['admin username']))
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        if last_name == None:
            last_name = ''
        else:
            last_name = ' '+last_name
        bot.send_message(message.chat.id,  f'👋🏼 Здравствуйте, {first_name}{last_name}, я телеграмм бот созданный для продаж в сфере виртуальной реальности. \n⬇️ Выбирите ниже нужную категорию ⬇️', reply_markup=markup)

    elif message.text == '/admin':
        if message.from_user.id in get_config()['admin']:
            bot.send_message(message.chat.id,
                             '/create_category - создать категорию\n'
                             '/new_tovar - создать товар\n\n'
                             '/delete_category - удалить категорию\n'
                             '/delete_tovar - удалить товар\n'
                             '/add_tovar - Добавить содержимое товара\n\n'
                             '/card - Новая карта\n'
                             '/Rassylka - Рассылка')
    elif message.text == '/Rassylka':
        if message.from_user.id in get_config()['admin']:
            s = bot.send_message(message.chat.id, 'Введите текст рассылки\n<b>Подтверждения не будет, пишите с первого раза правильно</b>\n/cancel для отмены', parse_mode='html')
            bot.register_next_step_handler(s, vvel_text_for_rassilka)



    elif message.text == '/create_category':
        if message.from_user.id in get_config()['admin']:
            s = bot.send_message(message.chat.id, 'Введите имя категории. /cancel для отмены')
            bot.register_next_step_handler(s, vvel_name_to_new_category)

    elif message.text == '/delete_category':
        if message.from_user.id in get_config()['admin']:
            markup = types.InlineKeyboardMarkup()
            a = -1
            for category in os.listdir('shop'):
                a += 1
                markup.add(types.InlineKeyboardButton(text=category, callback_data='deleteca1tegory_' + str(a)))

            bot.send_message(message.chat.id, 'Выберите категорию для удаления', reply_markup=markup)
    elif message.text == '/add_tovar':
        if message.from_user.id in get_config()['admin']:
            markup = types.InlineKeyboardMarkup()
            a = -1
            for category in os.listdir('shop'):
                a += 1
                markup.add(types.InlineKeyboardButton(text=category, callback_data='addtovardannie1_' + str(a)))

            bot.send_message(message.chat.id, 'Выберите категорию для добавления товара', reply_markup=markup)
    elif message.text == '/delete_tovar':
        if message.from_user.id in get_config()['admin']:
            markup = types.InlineKeyboardMarkup()
            a = -1
            for category in os.listdir('shop'):
                a += 1
                markup.add(types.InlineKeyboardButton(text=category, callback_data='deletetovar1_' + str(a)))

            bot.send_message(message.chat.id, 'Выберите категорию для удаления товара', reply_markup=markup)


    elif message.text == '/new_tovar':
        if message.from_user.id in get_config()['admin']:
            markup = types.InlineKeyboardMarkup()
            a = -1
            for category in os.listdir('shop'):
                a+=1
                markup.add(types.InlineKeyboardButton(text=category, callback_data='new_to1var_'+str(a)))


            bot.send_message(message.chat.id, 'Выберите категорию куда добавлять товар', reply_markup=markup)


    elif message.text == '/card':
        if message.from_user.id in get_config()['admin']:
            s = bot.send_message(message.chat.id, 'Введите номер карты для оплаты...\n/cancel для отмены')
            bot.register_next_step_handler(s, vvel_card)


def vvel_znach_tovarov_to_rewrite(message):
    tovari = message.text
    if tovari == '/cancel':
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message.message_id-1)
        bot.send_message(message.chat.id, '⛔Отменено: Переписать значение товара')
        markup = types.InlineKeyboardMarkup()
        a = -1
        for category in os.listdir('shop'):
            a += 1
            markup.add(types.InlineKeyboardButton(text=category, callback_data='addtovardannie1_' + str(a)))

        bot.send_message(message.chat.id, 'Выберите категорию для добавления товара', reply_markup=markup)
        return
    path_to_tovar = last_opened_tovar_to_rewrite_znach[message.from_user.id]
    a = open('shop/'+path_to_tovar, 'w', encoding='utf-8')
    a.write(tovari)
    a.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.send_message(message.chat.id, '✅Успешно обновлен список выдачи товара.')



@bot.callback_query_handler(func=lambda callback:True)
def callback(message):
    if message.data == 'shop':
        markup = types.InlineKeyboardMarkup()
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[i] = a
        for category_pathname in os.listdir('shop'):
            if '.' not in category_pathname:
                markup.add(types.InlineKeyboardButton(text=category_pathname, callback_data='category_'+str(categoryes[category_pathname])))
        markup.add(types.InlineKeyboardButton(text='◀️Назад', callback_data='main_menu'))
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,text='<b>🛍️ Магазин 🛍️</b>\n\n<i>👇🏼 Выберите категорию товара:</i>', reply_markup=markup, parse_mode='html')

    elif message.data == 'main_menu':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🛍 Магазин 🛍 ', callback_data='shop'), types.InlineKeyboardButton("⭐️ Инструкция ⭐️", url='https://telegra.ph/Instrukciya-pokupki-04-11'))
        markup.add(types.InlineKeyboardButton('🤷🏻‍♂️ Помощь 🤷🏻‍♂️', url='https://t.me/'+get_config()['admin username']))

        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        if last_name == None:
            last_name = ''
        else:
            last_name = ' '+last_name
        bot.edit_message_text(chat_id=message.message.chat.id,  text=f'🫱🏼‍🫲🏻 Здравствуйте, {first_name}, я телеграмм бот созданный для продаж в сфере виртуальной реальности.\n⬇️ Выбирите ниже нужную функцию ⬇️ ', reply_markup=markup, message_id=message.message.message_id)


    elif message.data == '/add_tovar_text':
        bot.delete_message(message.message.chat.id, message.message.message_id)

    elif 'addtovardannie1_' in message.data:
        category_index = str(message.data).replace('addtovardannie1_', '')
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]
        markup = types.InlineKeyboardMarkup()

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[i.replace('.txt', '')] = a


        for tovar_filename in os.listdir(f'shop/{category_name}'):
            if '.txt' in tovar_filename:
                tovar_filename = tovar_filename.replace('.txt', '')
                markup.add(types.InlineKeyboardButton(text=tovar_filename.split('_')[0], callback_data=f'addingtovardannie2_{category_index}_{tovari_in_category[tovar_filename]}'))

        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, 'Выберите товар для добавления данных на продажу', reply_markup=markup)

    elif 'addingtovardannie2_' in message.data:
        p = str(message.data).split('_')
        category_index = p[1]
        tovar_index = p[2]

        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[a] = i.replace('.txt', '')

        tovar_filename= tovari_in_category[int(tovar_index)]
        tovar_name = tovar_filename.split('_')[0]

        a = open(f'shop/{category_name}/{tovar_filename}.txt', 'r', encoding='utf-8')
        readed_tovari = a.read()
        a.close()
        last_opened_tovar_to_rewrite_znach[message.from_user.id] = str(category_name)+'/'+str(tovar_filename)+'.txt'
        bot.delete_message(message.message.chat.id, message.message.message_id)
        s = bot.send_message(message.message.chat.id, f'Выбранная категория: {category_name}\n'
                                                  f'Выбранный товар: {tovar_name}\n'
                                                  f'\n'
                                                  f'Данные товара сейчас:\n'
                                                  f'<code>{readed_tovari}</code>'
                                                  f'\n\n'
                                                  f'Введите товары\n'
                                                  f'На одной строке один товар\n'
                                                  f'Если в товаре есть переход на новую строку, Лучше обозначьте через точку.\n'
                                                  f'\n'
                                                  f'Введенное вами, перезапишет значение товара. Скопируйте выше старые торвары, к ним добавьте новые, пришлите мне.'
                                                  f'\n/cancel для отмены', parse_mode='html')

        bot.register_next_step_handler(s, vvel_znach_tovarov_to_rewrite)




    elif 'category_' in message.data:
        category_index = int(str(message.data).replace('category_', ''))
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[category_index]
        markup = types.InlineKeyboardMarkup()

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[i.replace('.txt', '')] = a


        for tovar_filename in os.listdir(f'shop/{category_name}'):
            if '.txt' in tovar_filename:
                tovar_filename = tovar_filename.replace('.txt', '')
                markup.add(types.InlineKeyboardButton(text=tovar_filename.split('_')[0], callback_data=f'tovar_{category_index}_{tovari_in_category[tovar_filename]}'))
        markup.add(types.InlineKeyboardButton(text='◀️Назад', callback_data='shop'))
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=f'Выбранная категория: <code>{category_name}</code>', parse_mode='html', reply_markup=markup)

    elif 'deleteca1tegory_' in message.data:
        category_index = str(message.data).replace('deleteca1tegory_', '')
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        shutil.rmtree(f'shop/{category_name}')

        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, f'Категория <code>{category_name}</code> успешно удалена', parse_mode='html')

    elif 'deletetovar1_' in message.data:
        category_index = str(message.data).replace('deletetovar1_', '')
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]



        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[i] = a
        markup = types.InlineKeyboardMarkup()
        for tovar_filename in os.listdir('shop/'+category_name):
            tovar_name = tovar_filename.replace(".txt", "").split('_')[0]
            markup.add(types.InlineKeyboardButton(text=tovar_name, callback_data=f'deltovar1_{category_index}_{tovari_in_category[tovar_filename]}'))
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, 'Выберите товар для удаления', reply_markup=markup)

    elif 'deltovar1_' in message.data:
        p = str(message.data).split('_')
        category_index = p[1]
        tovar_index = p[2]

        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a + 1
            tovari_in_category[a] = i

        tovar_name = tovari_in_category[int(tovar_index)]

        os.remove(f'shop/{category_name}/{tovar_name}')

        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, 'Успешно удалено')

    elif 'tovar_' in message.data:
        p = str(message.data).split('_')
        category_index = p[1]
        tovar_index = p[2]

        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[a] = i.replace('.txt', '')

        tovar_filename= tovari_in_category[int(tovar_index)]
        tovar_name = tovar_filename.split('_')[0]
        tovar_price = tovar_filename.split('_')[1]

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('💳 Картой 💳', callback_data='paycard_'+str(category_index)+'_'+str(tovar_index)))
        markup.add(types.InlineKeyboardButton('⭐️ Крипта ⭐️', callback_data='paycrypto_'+str(category_index)+'_'+str(tovar_index)))
        markup.add(types.InlineKeyboardButton('◀️ Назад', callback_data='category_'+str(category_index)))
        bot.edit_message_text(message_id=message.message.message_id, chat_id=message.message.chat.id, text=f'<b>Выбранный товар</b>: {tovar_name}\n'
                                                                                                           f'<b>Цена</b>: {tovar_price} UAH\n'
                                                                                                           f'\n<b>Выберите способ оплаты:</b>', reply_markup=markup, parse_mode='html')

    elif 'paycrypto_' in message.data:
        p = message.data.split('_')
        category_index = p[1]
        tovar_index = p[2]

        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[a] = i.replace('.txt', '')

        tovar_filename= tovari_in_category[int(tovar_index)]
        tovar_name = tovar_filename.split('_')[0]
        tovar_price = tovar_filename.split('_')[1]
        last_opened_tovar_for_cryptobot[message.from_user.id] = f'shop/{category_name}/{tovar_filename}.txt'
        json_of_payment = crypto_session.createInvoice(int(tovar_price))
        pay_url = json_of_payment['pay_url']
        invoiceId = json_of_payment['invoice_id']

        last_created_invoiceId_in_cryptobot[message.from_user.id] = invoiceId
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='💳Оплатить', url=pay_url))
        markup.add(types.InlineKeyboardButton(text='♻️ Проверить оплату', callback_data='checkpay_cryptobot'))
        markup.add(types.InlineKeyboardButton(text='◀️ Назад', callback_data='tovar_'+str(category_index)+'_'+str(tovar_index)))
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text='Выбранный метод оплаты: Crypto bot\n'
                                                                                                           f'Товар: {tovar_name}\n'
                                                                                                           f'Сумма к оплате: {tovar_price}\n', reply_markup=markup
                              )
    elif message.data == 'checkpay_cryptobot':
        last_creaded_invoice = last_created_invoiceId_in_cryptobot[message.from_user.id]

        paid = False

        last_checks = crypto_session.getCheks()
        a = open('last_paid_invoices_cryptobot.txt', 'r')
        readed = a.read()
        a.close()

        paid_invoices_last = readed.split('\n')



        for json_of_check in last_checks:
            if str(json_of_check['invoice_id'] )== str(last_creaded_invoice):
                if str(last_creaded_invoice) not in paid_invoices_last:
                    a = open('last_paid_invoices_cryptobot.txt', 'a')
                    a.write(str(last_creaded_invoice)+'\n')
                    a.close()

                    paid = True

        if not paid:
            bot.answer_callback_query(message.id, '⛔Оплата не найдена')
        else:
            path_to_tovar = last_opened_tovar_for_cryptobot[message.from_user.id]

            a = open(path_to_tovar, 'r', encoding='utf-8')
            readed = a.read()
            a.close()


            list_tovarov1 = readed.split('\n')
            list_tovarov2 = []

            for b in list_tovarov1:
                if b != '':
                    list_tovarov2 += [b]

            if len(list_tovarov2) == 0:
                bot.send_message(chat_id=get_config()['admin'],
                                 text=f'Товар: {path_to_tovar.split("/")[-1].split("_")[0]}\nНаличие: 0\nПополните товар!')
                random_tovar = 'Нет в наличии'
            else:
                random_tovar = random.choice(list_tovarov2)
                list_tovarov2.remove(random_tovar)

            a = open(path_to_tovar, 'w', encoding='utf-8')
            a.write('\n'.join(list_tovarov2))
            a.close()

            os.remove(path_to_tovar)
            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=f'✅Оплата найдена\nТовар:\n<code>{random_tovar}</code>', parse_mode='html')
            if random_tovar == 'Нет в наличии':
                markup_for_pokypatel = types.InlineKeyboardMarkup()
                markup_for_pokypatel.add(types.InlineKeyboardButton(text='🏠 Главная 🏠', callback_data='main_menu'))
                bot.send_message(chat_id=message.message.chat.id,
                                 text='Если оплата прошла и товар вы не получили, перейдите на «главную» ——> «помощь» ❗️',
                                 reply_markup=markup_for_pokypatel)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('🏠 Главная 🏠', callback_data='main_menu'))
                bot.send_message(chat_id=message.message.chat.id, text='↩️ Прейти на главную:', reply_markup=markup)








    elif 'paycard_' in message.data:
        p = str(message.data).split('_')
        category_index = p[1]
        tovar_index = p[2]

        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]

        tovari_in_category = {}
        a = -1
        for i in os.listdir(f'shop/{category_name}'):
            a = a+1
            tovari_in_category[a] = i.replace('.txt', '')

        tovar_filename= tovari_in_category[int(tovar_index)]
        tovar_name = tovar_filename.split('_')[0]
        tovar_price = tovar_filename.split('_')[1]
        a = open(f'descriptions/{(category_name)}/{(tovar_filename)}.txt', 'r', encoding='utf-8')
        description = a.read()
        a.close()
        tranzak_number = ''
        for i in range(10):
            tranzak_number += str(random.randint(0, 9))

        markup = types.InlineKeyboardMarkup()

        get_zakaz_info_with_tranzak_number[tranzak_number] = {'tovar':tovar_filename, 'category':category_name, 'sum':str(tovar_price), 'coment':f'Оплата №{tranzak_number}', 'id':message.from_user.id, 'message_id':message.message.message_id}
        last_creaded_invoice_TOVAR_AND_CATEGORY[message.from_user.id] = {'tovar':tovar_filename, 'category':category_name, 'sum':str(tovar_price), 'coment':f'Оплата №{tranzak_number}'}
        markup.add(types.InlineKeyboardButton(text='♻️ Проверить оплату', callback_data='checkpay'))
        markup.add(types.InlineKeyboardButton(text='◀️Назад', callback_data='tovar_'+str(category_index)+'_'+str(tovar_index)))


        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                              text=f'<b>Выбранная категория:</b> {category_name}\n'
                                   f'<b>Выбранный товар:</b> {tovar_name}\n'
                                   f'<b>Цена:</b> {tovar_price} UAH\n'
                                   f'<b>Описание товара:</b>\n{description}\n'
                                   f'\n'
                                   f'Реквизиты для перевода: <code>{get_config()["card"]}</code>\n'
                                   f'Сумма для перевода: <code>{tovar_price}</code>\n'
                                   f'Комментарий для перевода: <code>Оплата №{tranzak_number}</code>\n'
                                   f'Оплатите, а затем нажмите на <b>♻️ Проверить оплату</b>\n'
                                   f'\n'
                                   f'❗️Оплатите в течении 15 минут, иначе счет будет не активен❗️', reply_markup=  markup, parse_mode='html')


    elif message.data == 'checkpay':
        last_opened_tovar_json = last_creaded_invoice_TOVAR_AND_CATEGORY[message.from_user.id]
        tovar = last_opened_tovar_json['tovar']
        category = last_opened_tovar_json['category']
        summ = last_opened_tovar_json['sum']
        coment = last_opened_tovar_json['coment']
        tranzak_number = coment.replace('Оплата №', '')

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('✅ Да',  callback_data=f'yes,oplata_{tranzak_number}'),
                   types.InlineKeyboardButton('⛔ Нет', callback_data=f'no,oplata_{tranzak_number}'))
        for admin_vhat_id in get_config()['admin']:
            bot.send_message(chat_id=get_config()['admin'], text='<b>Проверка оплаты</b>\n'
                                                             f'От: @{str(message.from_user.username)}\n'
                                                             f'Товар: {tovar.split("_")[0]}\n'
                                                             f'Сумма: {summ}₴\n'
                                                             f'Комментарий: {coment}', reply_markup=markup, parse_mode='html')


        bot.send_message(message.message.chat.id, '✅Запрос отправлен администратору на проверку. Ожидайте')





    elif 'yes,oplata_' in message.data:
        tranzak_number = str(message.data).replace('yes,oplata_', '')
        if tranzak_number not in get_zakaz_info_with_tranzak_number:
            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                  text=f'⛔Заказ №{tranzak_number} не найден.\nВозможно кто то из админов уже отметил его.')
            return
        info_about_zakaz = get_zakaz_info_with_tranzak_number[tranzak_number]
        get_zakaz_info_with_tranzak_number.pop(tranzak_number)

        tovar_filename = info_about_zakaz['tovar']
        category = info_about_zakaz['category']
        chat_id = info_about_zakaz['id']



        a = open(f'shop/{category}/{tovar_filename}.txt', 'r', encoding='utf-8')
        readed = a.read()
        a.close()

        all_tovari = readed.split('\n')

        all_tovari2 = []
        for tovaar_in_all_tovari in all_tovari:
            if tovaar_in_all_tovari != '':
                all_tovari2 = all_tovari2 + [tovaar_in_all_tovari]

        if len(all_tovari2) == 0:
            bot.send_message(chat_id=get_config()['admin'], text=f'Товар: {tovar_filename}\nНаличие: 0\nПополните товар!')
            random_tovar = 'Нет в наличии'
        else:
            random_tovar = random.choice(all_tovari2)
            all_tovari2.remove(random_tovar)

        a = open(f'shop/{category}/{tovar_filename}.txt', 'w', encoding='utf-8')
        a.close()

        a = open(f'shop/{category}/{tovar_filename}.txt', 'a', encoding='utf-8')
        for tovar_to_wtite in all_tovari2:
            a.write(tovar_to_wtite+'\n')
        a.close()
        os.remove(f'shop/{category}/{tovar_filename}.txt')

        bot.delete_message(chat_id=chat_id, message_id=info_about_zakaz['message_id'])
        bot.send_message(chat_id=chat_id, text=f'✅Оплата найдена.\nТовар: {tovar_filename.split("_")[0]}\n\n<code>{random_tovar}</code>', parse_mode='html')
        if random_tovar == 'Нет в наличии':
            markup_for_pokypatel = types.InlineKeyboardMarkup()
            markup_for_pokypatel.add(types.InlineKeyboardButton(text='🏠 Главная 🏠', callback_data='main_menu'))
            bot.send_message(chat_id=chat_id, text='Если оплата прошла и товар вы не получили, перейдите на «главную» ——> «помощь» ❗️', reply_markup=markup_for_pokypatel)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🏠 Главная 🏠', callback_data='main_menu'))
            bot.send_message(chat_id=chat_id, text='↩️ Прейти на главную:', reply_markup=markup)
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id, text=f'Заказ №{tranzak_number}\nСтатус: ✅Оплачен.')






    elif 'no,oplata_' in message.data:
        tranzak_number = str(message.data).replace('no,oplata_', '')
        if tranzak_number not in get_zakaz_info_with_tranzak_number:
            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                  text=f'⛔Заказ №{tranzak_number} не найден.\nВозможно кто то из админов уже отметил его.')
            return

        info_about_zakaz = get_zakaz_info_with_tranzak_number[tranzak_number]
        get_zakaz_info_with_tranzak_number.pop(tranzak_number)

        tovar_filename = info_about_zakaz['tovar']
        category = info_about_zakaz['category']
        chat_id = info_about_zakaz['id']

        bot.send_message(chat_id=chat_id, text=f'⛔Оплата не найдена.\nТовар: {tovar_filename.split("_")[0]}')
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                              text=f'Заказ №{tranzak_number}\nСтатус: ⛔Не оплачен.')






    elif 'new_to1var_' in message.data:
        category_index = str(message.data).replace('new_to1var_', '')
        categoryes = {}
        a = -1
        for i in os.listdir('shop'):
            a += 1
            categoryes[a] = i

        category_name = categoryes[int(category_index)]
        adding_tovar_in_category[message.from_user.id] = category_name
        creating_new_tovar_info[message.from_user.id] = {}
        bot.delete_message(message.message.chat.id, message.message.message_id)
        s = bot.send_message(message.message.chat.id, 'Введите название товара...\n/cancel для отмены')
        bot.register_next_step_handler(s, vvel_name_tovara)

    elif message.data == 'yes create tovar':
        description = creating_new_tovar_info[message.from_user.id]['description']
        price = creating_new_tovar_info[message.from_user.id]['price']
        tovar_name = creating_new_tovar_info[message.from_user.id]['name']
        category = adding_tovar_in_category[message.from_user.id]

        a = open('shop/'+category+'/'+tovar_name+'_'+str(price)+'.txt', 'w+')
        a.close()

        a = open(f'descriptions/{category}/{tovar_name}_{price}.txt', 'w+', encoding='utf-8')
        a.write(description)
        a.close()
        creating_new_tovar_info[message.from_user.id] = {}
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, '✅Успешно создан товар')

    elif message.data == 'no create tovar':
        creating_new_tovar_info[message.from_user.id] = {}
        bot.delete_message(message.message.chat.id, message.message.message_id)
        bot.send_message(message.message.chat.id, '⛔Отменено: создание товара')




while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)