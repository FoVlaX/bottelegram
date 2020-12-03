import telepot
import time
from telepot.loop import MessageLoop
from imtosy import imtosy
from random import randint
import os
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup
import pickle
import threading

parametres = ReplyKeyboardMarkup(keyboard = [['параметры изображения']],resize_keyboard = True)
parametres_1 = ReplyKeyboardMarkup(keyboard = [['Изменить размер символа'],['Изменить размер изображения'],['Назад']],resize_keyboard = True)
symbol_syzes = ReplyKeyboardMarkup(keyboard = [['5','10','15'],['20','25','30'],['35','40','45'],['Назад']],resize_keyboard = True)
image_syzes = ReplyKeyboardMarkup(keyboard = [['1500','2000'],['2500','3000'],['3500','4000'],['Назад']],resize_keyboard = True)


symb_param = ['5','10','15','20','25','30','35','40','45']
img_param = ['1500','2000','2500','3000','3500','4000']


class ConvertThread(threading.Thread):
    def __init__(self, chat_id, msg):
        threading.Thread.__init__(self)
        self.chat_id = chat_id
        self.msg = msg
        self.deamon = True
    def run(self):
       
        chat_id = self.chat_id
        msg = self.msg

        print(chat_id,' send me foto, start converter') 
        count = randint(-10000,10000)
        bot.download_file(msg['photo'][-1]['file_id'], str(chat_id)+'/file'+str(count)+'.jpg')
        settings = {};
        with open(str(chat_id)+'/settins.pickle','rb') as f:
            settings = pickle.load(f)

        imtosy(str(chat_id)+'/file'+str(count)+'.jpg',settings['symbol_size'],settings['image_size'])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Получить оригинал', callback_data=str(chat_id)+'/file'+str(count)+'result.jpg')],[InlineKeyboardButton(text='Получить .txt файл', callback_data=str(chat_id)+'/file'+str(count)+'.txt')],[InlineKeyboardButton(text='Переконфертировать с текущими параметрами', callback_data="convert"+str(chat_id)+'/file'+str(count)+'.jpg')]])

        file_size = os.path.getsize(str(chat_id)+'/file'+str(count)+'result.jpg') 
        if file_size < 15*1024*1024:
            bot.sendPhoto(chat_id,open(str(chat_id)+'/file'+str(count)+'result.jpg', 'rb'),reply_markup = keyboard,caption = 'Вот твое фото. Размер символа '+str(settings['symbol_size'])+', изображения '+str(settings['image_size']))
        else:
            bot.sendDocument(chat_id,open(str(chat_id)+'/file'+str(count)+'result.jpg', 'rb'),reply_markup = keyboard,caption = 'Вот твое фото. Размер символа '+str(settings['symbol_size'])+', изображения '+str(settings['image_size']))
        print('end converter, send foto to',chat_id)      
    
def handle(msg):
    try:
        
        global img_param
        global symb_param
        
        content_type, chat_type, chat_id = telepot.glance(msg)
        try:
            os.mkdir(str(chat_id))
        except:
            pass


        
        if not os.path.exists(str(chat_id)+'/settins.pickle'):
            with open(str(chat_id)+'/settins.pickle','wb') as f:
                settings = {'symbol_size': 30, 'image_size': 3000 , 'menu_place':'image_param'}
                pickle.dump(settings, f)
                bot.sendMessage(chat_id,text = 'для редактирования параметров нажмите на кнопку',reply_markup = parametres)

        if content_type == 'text':
            settings = {}
            with open(str(chat_id)+'/settins.pickle','rb') as f:
                settings = pickle.load(f)
            menu_place = settings['menu_place']
            if menu_place == 'image_param':
                if msg['text'] == 'параметры изображения':
                    menu_place = 'choose_param'
                    bot.sendMessage(chat_id,text = 'Что изменяем?',reply_markup = parametres_1)
                else:
                    bot.sendMessage(chat_id,text = 'Отправте фото для обработки или напишите "параметры изображения" для редактирования параметров',reply_markup = parametres)
            if menu_place == 'choose_param':
                val = False
                if msg['text'] == 'Изменить размер символа':
                    menu_place = 'choose_symbol'
                    bot.sendMessage(chat_id,text = 'Задайте размер:',reply_markup = symbol_syzes)
                    val = True
                if msg['text'] == 'Изменить размер изображения':
                    menu_place = 'choose_image'
                    bot.sendMessage(chat_id,text = 'Задайте размер:',reply_markup = image_syzes)
                    val = True
                if msg['text'] == 'Назад':
                    menu_place = 'image_param'
                    bot.sendMessage(chat_id,text = 'Назад:',reply_markup = parametres)
                    val = True

                if not val:
                    bot.sendMessage(chat_id,text = 'Отправте фото для обработки или напишите одну из команд "Изменить размер символа", "Изменить размер изображения","Назад"',reply_markup = parametres_1)
                
            if menu_place == 'choose_symbol':
                if msg['text'] == 'Назад':
                    menu_place = 'choose_param'
                    bot.sendMessage(chat_id,text = 'Назад:',reply_markup = parametres_1)
                else:
                    if msg['text'] in symb_param:
                        settings['symbol_size']=int(msg['text'])
                        menu_place = 'choose_param'
                        bot.sendMessage(chat_id,text = 'Данные успешно обновлены:',reply_markup = parametres_1)
                    else:
                        bot.sendMessage(chat_id,text = 'Отправте фото для обработки или напишите один из размеров ' + str(symb_param),reply_markup = symbol_syzes)
                        
            if menu_place == 'choose_image':
                if msg['text'] == 'Назад':
                    menu_place = 'choose_param'
                    bot.sendMessage(chat_id,text = 'Назад:',reply_markup = parametres_1)
                else:
                    if msg['text'] in img_param:
                        settings['image_size']=int(msg['text'])
                        menu_place = 'choose_param'
                        bot.sendMessage(chat_id,text = 'Данные успешно обновлены:',reply_markup = parametres_1)
                    else:
                        bot.sendMessage(chat_id,text = 'Отправте фото для обработки или напишите один из размеров ' + str(img_param),reply_markup = image_syzes)
            settings['menu_place'] = menu_place
            with open(str(chat_id)+'/settins.pickle','wb') as f:
                pickle.dump(settings, f)    

            
        
        if content_type == 'photo':
            thread = ConvertThread(chat_id, msg)
            thread.start()
            
            
    except Exception as e:
        print(e)
        time.sleep(10)
        print('system will be reloaded')
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if "convert" in query_data:
        query_data =  query_data.replace('convert','')
        settings = {}
        with open(str(from_id)+'/settins.pickle','rb') as f:
            settings = pickle.load(f)

        imtosy(query_data,settings['symbol_size'],settings['image_size'])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Получить оригинал', callback_data=query_data.replace('.jpg','')+'result.jpg')],[InlineKeyboardButton(text='Получить .txt файл', callback_data=query_data.replace('.jpg','')+'.txt')],[InlineKeyboardButton(text='Переконфертировать с текущими параметрами', callback_data="convert"+query_data)]])

        file_size = os.path.getsize(query_data.replace('.jpg','')+'result.jpg') 
        if file_size < 15*1024*1024:
            bot.sendPhoto(from_id,open(query_data.replace('.jpg','')+'result.jpg', 'rb'),reply_markup = keyboard,caption = 'Вот твое фото. Размер символа '+str(settings['symbol_size'])+', изображения '+str(settings['image_size']))
        else:
            bot.sendDocument(from_id,open(query_data.replace('.jpg','')+'result.jpg', 'rb'),reply_markup = keyboard,caption = 'Вот твое фото. Размер символа '+str(settings['symbol_size'])+', изображения '+str(settings['image_size']))
        print(from_id,' send me foto')
    else:
        bot.sendDocument(from_id,open(query_data, 'rb'))


bot = telepot.Bot('985081018:AAHm2N1iQjUasHXsIVGv1AUL8aLrl-MpNd4')

MessageLoop(bot, {'chat':handle, 'callback_query':on_callback_query}).run_as_thread()



while 1:
    time.sleep(4);


