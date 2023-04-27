import csv
import datetime
import random
import telebot
import time
import os
from telebot import types

id_admin = 0 # your TG id
token = 'paste_your_token_here_or_fix_code_to_use_env_file'
csv_file = 'faq.csv'
show_meme = True

bot = telebot.TeleBot(token)


def send_meme(message):
    if show_meme:
        photo_url_array = [
            'https://cs8.pikabu.ru/post_img/big/2017/01/02/7/14833533391960248.jpg',
            'https://cs6.pikabu.ru/images/big_size_comm/2014-09_2/1410312896353.jpeg',
            'https://www.meme-arsenal.com/memes/7d0aad95d41b21936d96e7fae169d06f.jpg',
            'https://www.meme-arsenal.com/memes/b084afa2b8c082060b58360e309c11a5.jpg',
            'https://sun1-92.userapi.com/T0tzJNwsGaCEO_Mr2nnzT_VYFX57Bmrr3H5Hxw/_k5nGbolA90.jpg',
            'https://www.meme-arsenal.com/memes/3655dd01b154a793a95658dc387b0f1b.jpg',
            'https://www.meme-arsenal.com/memes/fec4d720b12bdc578dbb85f0da4559b1.jpg',
            'https://static.wikia.nocookie.net/anti-screamers/images/f/fa/%D0%97%D0%B0%D0%B3%D1%80%D1%83%D0%B6%D0%B5%D0%BD%D0%BE_%281%29.jpg/revision/latest/scale-to-width-down/300?cb=20200328151453&path-prefix=ru',
            'http://chance2.ru/photo/img/kot-v-naushnikakh-foto-1.jpg',
            'https://icdn.lenta.ru/images/2020/09/30/13/20200930130228617/wide_4_3_dea39f900590e21271e99c8e9f9530f5.jpg',
            'https://krasivosti.pro/uploads/posts/2021-04/1617944812_23-p-kot-s-mikrofonom-30.jpg'
        ]
        photo_url = random.choice(photo_url_array)
        bot.send_photo(message.chat.id, photo=photo_url)


def add_buttons_to_row(buttons_string):
    'Используется в read_from_file'
    buttons_row = buttons_string.split(',')
    # don't need it?
    for i, row in enumerate(buttons_row):
        if row == 'start':
            buttons_row[i] = '⬅️ В начало'

    return buttons_row


def read_from_file(message_text):
    # Return values
    answer_text = ''
    buttons = []

    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')

        # skipped first line
        skipped = False

        # reading a subset of buttons
        reading = False

        for row in reader:
            if not skipped:
                skipped = True
                continue

            button_text = row[0]
            if not reading:
                if (button_text != '' and message_text == button_text):
                    answer_text = row[1]
                    buttons.append(
                        add_buttons_to_row(row[2])
                    )
                    reading = True
            else:
                if (button_text == ''):
                    buttons.append(
                        add_buttons_to_row(row[2])
                    )
                else:
                    break

    return {
        'answer_text': answer_text,
        'buttons': buttons,
    }


def blet(message):
    photo = open('help.jpg', 'rb')
    bot.send_photo(message.chat.id, photo=photo, caption='Воспользуйся панелью навигации.')
    photo_url = 'https://memepedia.ru/wp-content/uploads/2017/06/%D0%BA%D0%B8%D0%B2%D0%B8-%D1%81-%D1%80%D1%83%D0%BA%D0%B0%D0%BC%D0%B8-%D0%BC%D0%B5%D0%BC.jpg'
    bot.send_photo(message.chat.id, photo=photo_url, caption='Я не такой умный.')


def get_user_name(user):
    'Получить имя'

    user_name = ''
    if user.first_name is not None:
        user_name = user.first_name

    if user.last_name is not None:
        if user_name == '':
            user_name = user.last_name
        else:
            user_name += ' ' + user.last_name

    if user_name != '':
        user_name += ' '

    user_name += '(' + str(user.id) + ')'

    if user.username is not None:
        user_name += ' ' + '@' + user.username
    # else:
    #     https://qna.habr.com/q/689311

    return user_name


def handle_avaya(message):
    message_chat_id = str(message.chat.id)
    timestamp = time.time()
    check_time = 46800 # 13 hours
    already_acquire = False
    avaya_return = False

    # Opening the file in read mode
    file = open('avaya.txt', 'r')
    replacement = ''

    for line in file:
        line = line.strip() # Remove '\n'
        values = line.split(',')
        changes = line

        # Check if Avaya is given
        if len(values) > 1:
            if values[1] == message_chat_id:
                # This user already have it
                avaya_return = values[0]
                already_acquire = True
                break

            # Check if old
            if timestamp - float(values[2]) > check_time:
                # Give Avaya to user
                if not avaya_return:
                    avaya_return = values[0]
                    changes = values[0] + ',' + message_chat_id + ',' + str(timestamp)
                else:
                    changes = values[0]
        elif not avaya_return:
            # Give Avaya to user
            avaya_return = values[0]
            changes = values[0] + ',' + message_chat_id + ',' + str(timestamp)

        replacement = replacement + changes + "\n"
    file.close()

    # Opening the file in write mode
    if avaya_return and not already_acquire:
        fout = open("avaya.txt", "w")
        fout.write(replacement)
        fout.close()

    user_name = get_user_name(message.chat)
    if already_acquire:
        answer = 'На текущую смену тебе была выдана Avaya: ' + avaya_return + \
            '. Если номер был запрошен ошибочно, воспользуйся кнопкой "Вернуть номер Avaya"'
        bot.send_message(id_admin, user_name + ' пытался забрать себе авайку ' +
                         avaya_return + ' которую уже получал')
    elif avaya_return:
        answer = 'Твой номер Avaya на текущую смену: ' + avaya_return
        bot.send_message(id_admin, user_name + ' только что получил авайку ' +
                         avaya_return)
    else:
        answer = 'Все номера Avaya заняты, обратитесь к РРП в группу "УР_Омск"'
        bot.send_message(id_admin, 'Сань, ты там как, нормально?')
        bot.send_message(id_admin, 'Все авайки забиты')
        bot.send_message(id_admin, 'им не нормально')

    return answer


def free_avaya(message):
    message_chat_id = False
    avaya_to_search = False

    if message.text and message.text.isnumeric() and message.chat.id == id_admin:
        avaya_to_search = message.text
    else:
        message_chat_id = str(message.chat.id)
    avaya_return = False

    # Opening the file in read mode
    file = open('avaya.txt', 'r')
    replacement = ''

    for line in file:
        line = line.strip() # Remove '\n'
        values = line.split(',')

        # Check if Avaya is given
        if len(values) > 1:
            if message_chat_id and values[1] == message_chat_id:
                avaya_return = line = values[0]
            elif avaya_to_search and values[0] == avaya_to_search:
                avaya_return = line = values[0]
                bot.send_message(values[1], 'Ваша AVAYA ' + avaya_return + ' была освобождена администратором')

        replacement = replacement + line + "\n"
    file.close()

    user_name = get_user_name(message.chat)
    if avaya_return:
        # Opening the file in write mode
        fout = open("avaya.txt", "w")
        fout.write(replacement)
        fout.close()
        answer = 'Твой номер Avaya ' + avaya_return + ' был возвращён.'
        bot.send_message(id_admin, user_name + ' освободил авайку ' +
                         avaya_return)
    else:
        answer = 'Тебе нечего возвращать.'
        bot.send_message(id_admin, user_name + ' просто так тыкал в кнопку "освободить авайку"')
    return answer


def clear_avaya_list(message):
    if message.chat.id == id_admin:

        # Opening the file in read mode
        file = open('avaya.txt', 'r')
        replacement = ''
        check_time = 46800  # 13 hours
        timestamp = time.time()

        for line in file:
            line = line.strip()  # Remove '\n'
            values = line.split(',')

            # Check if Avaya is given
            if len(values) > 1:
                if float(values[2]) < float(timestamp) - check_time:
                    line = values[0]
            replacement = replacement + line + "\n"
        file.close()

        fout = open("avaya.txt", "w")
        fout.write(replacement)
        fout.close()


def get_avaya_list(message):
    clear_avaya_list(message)
    taken_avaya = []
    free_avaya = []

    # Opening the file in read mode
    file = open('avaya.txt', 'r')

    i = 0
    for line in file:
        line = line.strip()  # Remove '\n'
        values = line.split(',')

        # Check if Avaya is given
        if len(values) > 1:
            user = bot.get_chat_member(int(values[1]), int(values[1]))
            user_name = get_user_name(user.user)
            date = datetime.datetime.fromtimestamp(float(values[2])).strftime('%d.%m %H:%M')
            avaya = values[0]
            taken_avaya.append(avaya + ' занята пользователем ' + user_name + ' ' + date)
        else:
            if i < 4:
                values[0] += ' - '
                i = i + 1
            else:
                values[0] += '\n'
                i = 0
            free_avaya.append(values[0])

    file.close()

    free_avaya_text = '`' + ''.join(free_avaya) + '\nСвободных AVAYA: ' + str(len(free_avaya)) + '`'
    if free_avaya_text:
        bot.send_message(message.chat.id, free_avaya_text, parse_mode="markdown")

    taken_avaya_text = '\n'.join(taken_avaya) + '\nЗанятых AVAYA: ' + str(len(taken_avaya))
    if len(taken_avaya_text) > 4096:
        message_1 = taken_avaya_text[0:4096]
        message_2 = taken_avaya_text[4096:len(taken_avaya_text)]
        bot.send_message(
            message.chat.id, message_1
        )
        bot.send_message(
            message.chat.id, message_2
        )
    else:
        bot.send_message(
            message.chat.id, taken_avaya_text
        )


def response_from_file(messages):
    button_back = types.KeyboardButton('⬅️ В начало')
    button_avaya_free = types.KeyboardButton('Вернуть номер Avaya')
    button_avaya_list = types.KeyboardButton('📑 Список Avaya')
    answer = False

    now = datetime.datetime.now(datetime.timezone.utc)
    start_hour = 6 - 6
    end_hour = 21 - 6

    for message in messages:
        # bot.delete_message(message.chat.id, message.id)
        markup = types.ReplyKeyboardMarkup()
        if message.text.isnumeric() and message.chat.id == id_admin:
            free_avaya(message)
        if message.text == '⬅️ В начало' or message.text == '/start':
            message.text = 'start'

        if message.text == '📑 Список Avaya' and message.chat.id == id_admin:
            get_avaya_list(message)
            answer = 'Получай'
        elif message.text == 'Подтвердить':
            if now.hour >= start_hour and now.hour < end_hour or show_meme:
                answer = handle_avaya(message)
            else:
                answer = 'Коллега, выдача Avaya производится с 6:00 до 21:00'
            markup.row(button_back)
        elif message.text == 'Вернуть номер Avaya':
            answer = free_avaya(message)
            markup.row(button_back)
        else:
            output = read_from_file(message.text)
            if output['answer_text'] == '':
                blet(message)
            else:
                answer = output['answer_text']
                for button_row in output['buttons']:
                    row = [types.KeyboardButton(x) for x in button_row]
                    markup.add(*row)

            if message.text == 'start':
                send_meme(message)
                bot.send_message(message.chat.id, 'Если тебя нужно разлогинить, сразу пиши в "УР_Омск"')
                markup.row(button_avaya_free)
                if (message.chat.id == id_admin):
                    markup.row(button_avaya_list)
            else:
                markup.row(button_back)

        if answer:
            bot.send_message(
                message.chat.id, answer, reply_markup=markup
            )


bot.set_update_listener(response_from_file)
bot.infinity_polling()
