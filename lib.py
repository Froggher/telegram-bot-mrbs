import itertools
import re
from datetime import datetime
from datetime import timedelta
from typing import Any

import requests
from bs4 import BeautifulSoup
from telegram import *
from telegram.constants import ChatAction
from telegram.ext import *

import telegramcalendar

AFTER_START, RIC_AVANZATA, MES_DESCRIPTION, DATA_MENU, DATA1_CALENDARIO, QUERY_ESAME, DOPO_RICERCA, QUERY_TIPO_CORSO, QUERY_AULA, PROF_MESSAGE, PRE_RICERCA, LIMIT_EXCEED, DATA2_CALENDARIO = range(
	13)

SI, NO = range(2)

SHOW_MAX = 75

reply_keyboard = [
	['🗓 Cambia data', '🏢 Aule libere'],
	['🌀 Cancella parametri', '🔣 Altri Parametri'],
	['📌 Ricerca per oggi', '🔎 Ricerca'],
]

start_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Menu")

reply_keyboard66 = [
	['👤 Professori', '🔏 Esame'],
	['🚪 Scelta aule', '🎓 Corso di studi'],
	['🗒 Breve descrizione', '↩️ Menu'],
	['🟢 Parametri impostati', '🔎 Ricerca'],
]

adv_key = ReplyKeyboardMarkup(reply_keyboard66, one_time_keyboard=True, input_field_placeholder="Aggiungere filtri")

reply_keyboard1 = [
	['Oggi', 'Questa settimana'],
	['Da oggi a ...', 'Da ... a ...'],
]
data_key = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True, input_field_placeholder="Scegli data")

reply_keyboard2 = [
	['🔄 Cambia Parametri'],
	['♻️ Cancella parametri'],
	['🔙 Torna al menu'],
]
after_key = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True, resize_keyboard=True,
								input_field_placeholder="Risultati")

inline_keyboard = [

	[
		InlineKeyboardButton("Matematica I", callback_data='Matematica+I+Anno'),
		InlineKeyboardButton("Informatica I", callback_data='Informatica+I+Anno'),
	],
	[
		InlineKeyboardButton("Matematica II", callback_data='Matematica+II+Anno'),
		InlineKeyboardButton("Informatica II", callback_data='Informatica+II+Anno'),
	],
	[
		InlineKeyboardButton("Matematica III", callback_data='Matematica+III+Anno'),
		InlineKeyboardButton("Informatica III", callback_data='Informatica+III+Anno'),
	],
	[
		InlineKeyboardButton("Matematica Mag. I", callback_data='Matematica+Magistrale+I+Anno'),
		InlineKeyboardButton("Informatica Mag. I", callback_data='Informatica+Magistrale+I+Anno'),
	],
	[
		InlineKeyboardButton("Matematica Mag. II", callback_data='Matematica+Magistrale+II+Anno'),
		InlineKeyboardButton("Informatica Mag. II", callback_data='Informatica+Magistrale+II+Anno'),
	],
	[
		InlineKeyboardButton("Matematica lauree", callback_data='Matematica'),
		InlineKeyboardButton("Informatica lauree", callback_data='Informatica'),
	],
	[
		InlineKeyboardButton("Altro", callback_data='Altro'),
		InlineKeyboardButton("↩️ Indietro", callback_data='Indietro')
	],

]

studio_key = InlineKeyboardMarkup(inline_keyboard)

inline_keyboard2 = [

	[
		InlineKeyboardButton("✅ Sì", callback_data=str(SI)), InlineKeyboardButton("❌ No", callback_data=str(NO))
	]
]

si_no_key = InlineKeyboardMarkup(inline_keyboard2)

inline_keyboard3 = [

	[
		InlineKeyboardButton("A0", callback_data='A0'), InlineKeyboardButton("A2", callback_data='A2'),
		InlineKeyboardButton("A3", callback_data='A3'),
	],

	[
		InlineKeyboardButton("Aula C3", callback_data='Aula+C3'),
		InlineKeyboardButton("Aula Dott. V Piano - P1", callback_data='Aula+Dott.+V+Piano+-+P1'),
		InlineKeyboardButton("Aula Dott. V Piano - P2", callback_data='Aula+Dott.+V+Piano+-+P2'),
	],

	[
		InlineKeyboardButton("Aula Dott. V Piano - P3", callback_data='Aula Dott. V Piano - P3'),
		InlineKeyboardButton("Aula Gialla", callback_data='Aula+Gialla'),
		InlineKeyboardButton("Aula S - P1", callback_data='Aula+S+-+P1'),
	],

	[
		InlineKeyboardButton("Aula S - P2", callback_data='Aula+S+-+P2'),
		InlineKeyboardButton("Aula Verde", callback_data='Aula+Verde'), InlineKeyboardButton("B1", callback_data='B1'),
	],

	[
		InlineKeyboardButton("B3", callback_data='B3'), InlineKeyboardButton("C2", callback_data='C2'),
		InlineKeyboardButton("I1", callback_data='I1'),
	],

	[
		InlineKeyboardButton("I2", callback_data='I2'), InlineKeyboardButton("NB19", callback_data='NB19'),
		InlineKeyboardButton("NB20", callback_data='NB20'),
	],

	[
		InlineKeyboardButton("Portatile 4", callback_data='Portatile+4'),
		InlineKeyboardButton("Portatile 5", callback_data='Portatile+5'),
		InlineKeyboardButton("Portatile 6", callback_data='Portatile+6'),
	],

	[
		InlineKeyboardButton("Proiettore 4", callback_data='Proiettore+4'),
		InlineKeyboardButton("Sala Riunioni", callback_data='Sala+Riunioni'),
		InlineKeyboardButton("Indietro", callback_data='Indietro'),
	],

]

aule_key = InlineKeyboardMarkup(inline_keyboard3)

inline_keyboard4 = [

	[
		InlineKeyboardButton("🔎 Ricerca", callback_data=str(SI))
	],

	[
		InlineKeyboardButton("↩️ Indietro", callback_data=str(NO))
	],

]

ric_key = InlineKeyboardMarkup(inline_keyboard4)


async def stampa_risultato_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	user_data = context.user_data

	data1 = user_data['T1']
	data2 = user_data['T2']

	corso = user_data["CORSO"]
	aula = user_data["AULA"]
	descrizione = user_data["DESCRIZIONE"]
	esame = user_data["ESAME"]
	prof = user_data['PROF']

	events = []

	context.bot.sendChatAction(chat_id=update.callback_query.from_user.id, action=ChatAction.TYPING)

	events.append(event_query(
		data1, data2, match_tipocorso=corso, esame=esame, roommatch=aula, namematch=descrizione,
		match_organizzatore=prof))

	flattened_events = list(itertools.chain.from_iterable(events))

	if len(flattened_events) == 0:
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Non sono state trovate prenotazioni.\nRiprovare la ricerca cambiando e/o aggiungendo parametri",
								 reply_markup=after_key)
		return DOPO_RICERCA

	if len(flattened_events) > SHOW_MAX:
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Il numero massimo di prenotazioni viusalizzabili è stato raggiunto")
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Ritorno al menu", reply_markup=start_key)

		return AFTER_START

	context.chat_data['grouped_events'], lenght_key = group_events_by(flattened_events)

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Sono state trovate " + str(
								 len(flattened_events)) + " prenotazioni per i parametri impostati.",
							 reply_markup=after_key)

	for lol in range(lenght_key):
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text=event_visualizer_simple(context, lol - 1))

	return DOPO_RICERCA


async def stampa_risultato_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	user_data = context.user_data

	category1 = user_data['T1']
	category2 = user_data['T2']

	corso = user_data["CORSO"]
	aula = user_data["AULA"]
	esame = user_data["ESAME"]
	descrizione = user_data["DESCRIZIONE"]
	prof = user_data['PROF']

	events = []

	context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

	if update.message.text == '📌 Ricerca per oggi':
		events.append(event_query(datetime.now(), datetime.now()))
		flattened_events = list(itertools.chain.from_iterable(events))
		context.chat_data['grouped_events'], key = group_events_by(flattened_events)

		if len(flattened_events) == 0:
			await update.message.reply_text("Nessuna prenotazione per oggi", reply_markup=after_key)
			return DOPO_RICERCA

		await update.message.reply_text("Sono state trovate " + str(
			len(flattened_events)) + " prenotazioni per i parametri impostati.\nUsa le frecce per cambiare aula e quella centrale per visualizzare i dettagli della prenotazione.",
								  reply_markup=after_key)
		await update.message.reply_text(event_visualizer(0, context),
								  reply_markup={True: None, False: create_button(0, context)}[
									  len(context.chat_data['grouped_events']['uniquekeys'][0]) < 2])
		return DOPO_RICERCA

	events.append(event_query(
		category1, category2, match_tipocorso=corso, esame=esame, roommatch=aula, namematch=descrizione,
		match_organizzatore=prof))

	flattened_events = list(itertools.chain.from_iterable(events))

	if len(flattened_events) == 0:
		await update.message.reply_text(
			"Non sono state trovate prenotazioni.\nRiprovare la ricerca cambiando e/o aggiungendo parametri",
			reply_markup=after_key)
		return DOPO_RICERCA

	if len(flattened_events) > SHOW_MAX:
		await update.message.reply_text("Il numero massimo di prenotazioni viusalizzabili è stato raggiunto")
		await update.message.reply_text("Ritorno al menu", reply_markup=start_key)

		return AFTER_START

	context.chat_data['grouped_events'], lenght_key = group_events_by(flattened_events)

	await update.message.reply_text(
		"Sono state trovate " + str(len(flattened_events)) + " prenotazioni per i parametri impostati.",
		reply_markup=after_key)

	for lol in range(lenght_key):
		await update.message.reply_text(event_visualizer(context=context, index=lol - 1, detailed=False))

	return DOPO_RICERCA


def prettify_event(event: dict) -> str:
	return "________________\n📆 " + event["Evento"] + "\n👤 " + event["Docente"] + "\n🕰 " + \
		re.findall('\d+:\d+', event["Ora Inizio"])[0] + " / " + event["Ora Fine"]


# return re.sub('(Aule\ \-\ )|(Stanze\ \-\ )', '', event["Sala"]) + "\n📆 " + event["Evento"] + "\n👤 " + event["Docente"] + "\n🕰 " + re.findall('\d+:\d+', event["Ora Inizio"])[0] + " - " + re.findall('\d+:\d+', event["Ora Fine"])[0]#    return re.sub('(Aule\ \-\ )|(Stanze\ \-\ )', '', event["Sala"]) + "\n📆 " + event["Evento"] + "\n👤 " + event["Docente"] + "\n🕰 " + re.findall('\d+:\d+', event["Ora Inizio"])[0] + " - " + re.findall('\d+:\d+', event["Ora Fine"])[0]

def prettify_event_detailed(event: dict) -> str:
	return "\n".join(
		["________________", "📆 " + event["Evento"], "🗒 " + event["Descrizione"], "🔖 " + event["Tipo di prenotazione"],
		 "✔️ " + event["Stato dell'approvazione"], "🚪 " + event["Sala"], "⏰ " + event["Ora Inizio"],
		 "⏱ " + event["Durata"], "⌛️ " + event["Ora Fine"], "📇 " + event["Creato da"], "✏️ " + event["Modificato da"],
		 "📜 " + event["Ultima Modifica"], "👤 " + event["Docente"], "🔏 " + event["E' un esame?"],
		 "🎓 " + event["Corso di Studi"],
		 "🔁 " + event["Tipo ripetizione"]

		 ])


def group_events_by(event_list: list, grouping="Sala") -> tuple[dict[str, list[Any] | list[list[Any]]], int]:
	groups = []
	uniquekeys = []
	# print(event_list)
	data = sorted(event_list, key=lambda x: x[grouping])

	for key, group in itertools.groupby(data, lambda x: x[grouping]):
		groups.append(list(group))  # Store group iterator as a list
		uniquekeys.append(key)

	return {'uniquekeys': uniquekeys, 'groups': groups}, len(uniquekeys)


def event_visualizer(index: int, context: CallbackContext, detailed=False) -> str:
	prettified_events = []
	for i in range(len(context.chat_data['grouped_events']['groups'][index])):
		prettified_events.append(
			{True: prettify_event_detailed(context.chat_data['grouped_events']['groups'][index][i]),
			 False: prettify_event(context.chat_data['grouped_events']['groups'][index][i])}[detailed])

	return context.chat_data['grouped_events']['uniquekeys'][index] + "\n" + "\n".join(
		x for x in prettified_events)  # prettify_event(context.chat_data['grouped_events']['groups'][index][0])


def event_visualizer_simple(context: CallbackContext, lenght: int) -> str:
	prettified_events = []
	for i in range(len(context.chat_data['grouped_events']['groups'][lenght])):
		prettified_events.append(prettify_event(context.chat_data['grouped_events']['groups'][lenght][i]))

	return context.chat_data['grouped_events']['uniquekeys'][lenght] + "\n" + "\n".join(
		x for x in prettified_events)  # prettify_event(context.chat_data['grouped_events']['groups'][max_index][0])


def create_button(index: int, context: CallbackContext):
	max_index = len(context.chat_data['grouped_events']['uniquekeys'])
	prev_index = {True: max_index - 1, False: index - 1}[(index - 1) < 0]
	next_index = {True: 0, False: index + 1}[(index + 1) > (max_index - 1)]

	keyboard = [
		[
			InlineKeyboardButton("◀️", callback_data=";".join(["PREVIOUS", str(prev_index)])),
			InlineKeyboardButton("⤵️", callback_data=";".join(["PRINT_MSG", str(index)])),
			InlineKeyboardButton("▶️", callback_data=";".join(["NEXT", str(next_index)]))
		]
	]
	return InlineKeyboardMarkup(keyboard)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Parses the CallbackQuery and updates the message text."""
	# CallbackQueries need to be answered, even if no notification to the user is needed
	# Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
	query = update.callback_query
	await query.answer()
	context.user_data['inline_button'] = query.data

	action, index = update.callback_query.data.split(";")

	if action == "PREVIOUS":
		await update.callback_query.edit_message_text(text=event_visualizer(int(index), context),
												reply_markup=create_button(int(index), context))
	elif action == "PRINT_MSG":
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text=event_visualizer(int(index), context, True))
	elif action == "NEXT":
		await update.callback_query.edit_message_text(text=event_visualizer(int(index), context),
												reply_markup=create_button(int(index), context))

	return DOPO_RICERCA


async def crea_calendario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("Inserire data: ",
							  reply_markup=telegramcalendar.create_calendar())
	context.user_data['typecal'] = update.message.text
	return DATA1_CALENDARIO


async def calendario_data1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	selected, date = telegramcalendar.process_calendar_selection(update, context)
	if selected:
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Data impostata %s" % (date.strftime("%d/%m/%Y")),
								 reply_markup=ReplyKeyboardRemove())

	# Se il giorno non viene selezionato la funzione si ripete
	elif date == None:
		return DATA1_CALENDARIO

	user_data = context.user_data
	category = user_data['typecal']

	if date != None:
		# viene memorizzato il valore della prima data, utile per anche per il calendario con doppia data
		t1 = date.strftime("%d/%m/%Y")
		context.user_data['cal1'] = t1

	# Se il calendario è singolo viene salvata subito la data
	if category == "Da oggi a ...":
		if date != None:
			b = date.strftime("%d/%m/%Y")

			t1 = b.rsplit("/")
			context.user_data['T1'] = datetime.now()
			context.user_data['T2'] = datetime(int(t1[2]), int(t1[1]), int(t1[0]))
			context.bot.send_message(chat_id=update.callback_query.from_user.id,
									 text="Preferenza data memorizzata", reply_markup=start_key)
		return AFTER_START

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Inserire seconda data:", reply_markup=telegramcalendar.create_calendar())

	# Se il calendario ha data doppia, viene creato un secondo calendario
	return DATA2_CALENDARIO


async def calendario_data2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	user_data = context.user_data
	a1 = user_data['cal1']

	selected, date = telegramcalendar.process_calendar_selection(update, context)
	if selected:
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Data finale %s" % (date.strftime("%d/%m/%Y")),
								 reply_markup=ReplyKeyboardRemove())

	elif date == None:
		return DATA2_CALENDARIO

	b1 = date.strftime("%d/%m/%Y")

	b = b1.rsplit("/")
	a = a1.rsplit("/")

	user_data['T1'] = datetime(int(a[2]), int(a[1]), int(a[0]))
	user_data['T2'] = datetime(int(b[2]), int(b[1]), int(b[0]))

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Preferenza data memorizzata", reply_markup=start_key)

	return AFTER_START


async def mem_settimana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	if update.message.text == "Oggi":
		context.user_data['T1'] = datetime.now()
		context.user_data['T2'] = datetime.now()


	elif update.message.text == "Questa settimana":
		context.user_data['T1'] = datetime.now()
		context.user_data['T2'] = datetime.now() + timedelta(weeks=1)

	await update.message.reply_text("Preferenza data memorizzata", reply_markup=start_key)

	return AFTER_START


# Questa funzione, dato un url valido, cerca gli id delle prenotazioni e li mette in una lista che andrà a returnare
def find_event_id(url: str) -> list:
	"""
    - from_day
    - areamatch è una delle due seguenti stringhe: "Aule" o "Stanze"
    - roommatch è una delle seguenti stringhe: "A0", "A2", "A3", "Aula C3", "Aula Dott. V Piano - P1", "Aula Dott. V Piano - P2", "Aula Dott. V Piano - P3", "Aula Gialla", "Aula S - P1", "Aula S - P2", "Aula Verde", "B1", "B3", "C2", "I1", "I2", "NB19", "NB20", "Portatile 4", "Portatile 5", "Portatile 6", "Proiettore 4", "Sala Riunioni"
    - typematch può essere rispettivamente una delle seguenti 2 stringhe: "E" o "I"
    - match_organizzatore è il nome di un professore del tipo Nome%20Cognome
    """
	r = requests.get(url)
	# viene trovato il singolo id della prenotazione
	id_list = []
	counter = 0
	for i in re.findall('view_entry\.php\?id=\d+', r.text):

		# numero massimo di risultati mostrato
		if counter > SHOW_MAX:
			return id_list

		id_list.append(re.findall('.*?([0-9]+)$', i)[0])
		counter = counter + 1
	return id_list


# Questa funzione trova e mette in un dizionario tutti i dettagli di una prenotazione in base all’id ricevuto
def event_details(id: str):
	url = 'https://servizi.dmi.unipg.it/mrbs/view_entry.php?id=' + id
	result = requests.get(url)
	soup = BeautifulSoup(result.content, "html.parser")

	previous_string_is_key = False
	list = ["ID", id, "Evento", soup.h3.text[1:]]
	for string in soup.find(id='entry').stripped_strings:
		string_ends_with_dot = string[-1] == ":"
		if previous_string_is_key:
			if string_ends_with_dot:
				previous_string_is_key = True
				list.append("")
			else:
				previous_string_is_key = False
		else:
			if string_ends_with_dot:
				previous_string_is_key = True

		list.append({True: string[:-1], False: string}[string_ends_with_dot])
	iterabile = iter(list)

	return dict(zip(iterabile, iterabile))


# Questa funzione invece diciamo che è il cardine di tutto: per prima cosa costruisce l’url che verrà usato per fare la query al database delle prenotazioni, come vedi gli argomenti sono tutti omissibili, ovvero che se provi a chiamare la funzione senza parametri questa ti restituisce una lista di dizionari degli eventi dal giorno corrente al giorno corrente per tutte le aule e i professori
def event_query(a_date, b_date, areamatch="", roommatch="", typematch1="", typematch2="", namematch="", descrmatch="",
				creatormatch="", match_private="0", match_confirmed="2", match_approved="2", match_organizzatore=None,
				match_tipocorso="", esame="", only_aula=False):
	if match_organizzatore is None:
		match_organizzatore = []
	from_day = str(a_date.day)
	from_month = str(a_date.month)
	from_year = str(a_date.year)

	to_day = str(b_date.day)
	to_month = str(b_date.month)
	to_year = str(b_date.year)

	if esame != "":
		if esame == SI:
			esame = "&match_esame=1"
		elif esame == NO:
			esame = "&match_esame=0"

	"""
    Creates the dictionary that contains the query's result. The structure of the dictionary is:
        'key' = event's unique identifier,
        'value' = dictionary of the event's details
    """
	mrbs = 'https://servizi.dmi.unipg.it/mrbs/report.php?from_day=' + from_day + '&from_month=' + from_month + '&from_year=' + from_year + '&to_day=' + to_day + '&to_month=' + to_month + '&to_year=' + to_year + '&areamatch=' + areamatch + '&roommatch=' + roommatch + \
		   {True: '&typematch%5B%5D=E', False: ''}[typematch1 == "E"] + {True: '&typematch%5B%5D=I', False: ''}[
			   typematch2 == "I"] + '&namematch=' + namematch + '&descrmatch=' + descrmatch + '&creatormatch=' + creatormatch + '&match_private=' + match_private + '&match_confirmed=' + match_confirmed + '&match_approved=' + match_approved + '&match_organizzatore=' + esame + '&match_tipocorso=' + match_tipocorso + '&output=0&output_format=0&sortby=r&sumby=d&phase=2&datatable=1&ajax=1&phase=2'
	event_list = []
	temp_list = []
	aula_list = []
	# aggiunge ad una lista vuota a ogni evento id
	counter = 0
	for id in find_event_id(mrbs):
		event = event_details(id)
		event["Sala"] = re.sub("(Aule - )|(Stanze - )", "", event["Sala"])

		if match_organizzatore != []:
			if (event["Docente"] in match_organizzatore):
				event_list.append(event)
		else:
			event_list.append(event)

		aula_list.append(event["Sala"])

		counter = counter + 1

	if only_aula == True:
		li1 = ["A0", "A2", "A3", "Aula C3", "Aula Dott. V Piano - P1", "Aula Dott. V Piano - P2",
			   "Aula Dott. V Piano - P3",
			   "Aula Gialla", "Aula S - P1", "Aula S - P2", "Aula Verde", "B1", "B3", "C2",
			   "I1", "I2", "NB19", "NB20", "Portatile 4", "Portatile 5", "Portatile 6",
			   "Proiettore 4", "Sala Riunioni"]
		return Diff(li1, aula_list)

	return event_list


def Diff(li1, li2):
	# https://www.geeksforgeeks.org/sets-in-python/
	return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


def get_professors():
	result = requests.get("https://servizi.dmi.unipg.it/mrbs/report.php")
	soup = BeautifulSoup(result.content, 'html.parser')

	professors = []
	for option in soup.find(id='match_organizzatore_options').find_all('option'):
		professors.append(option.text)

	return professors


def find_professor(searched_professor=""):
	professors_list = get_professors()
	found_professors = []
	for p in professors_list:
		if p.casefold().find(searched_professor.casefold()) != -1:
			found_professors.append(p)
	return found_professors


async def start_find_prof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	if int(len(update.message.text)) < 3:
		await update.message.reply_text("Errore inserire minimo 3 caratteri", reply_markup=adv_key)
		return PROF_MESSAGE

	context.user_data['PROF'] = []
	stringa = update.message.text

	if update.message.text == "/clear":
		await update.message.reply_text("Ho reimpostato il filtro dei docenti", reply_markup=adv_key)
		return RIC_AVANZATA

	profs = find_professor(update.message.text)
	msg = ""

	if len(profs) > 0:
		for p in profs:
			context.user_data['PROF'].append(p)
		msg = ":\n" + "\n".join(x for x in profs)

	prof = find_professor(stringa)
	await update.message.reply_text(
		"Ho trovato " + str(len(prof)) + " professori che contengono \"" + stringa + "\":\n" + "\n".join(
			x for x in prof), reply_markup=adv_key)

	return RIC_AVANZATA


async def pre_find_professor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Digita il nome del docente che stai cercando.\nSe vuoi rimuovere i docenti impostati basta inviare /clear")
	return PROF_MESSAGE


async def ric_avanzata(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Immettere i seguenti filtri",
		reply_markup=adv_key
	)

	return RIC_AVANZATA


async def data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Selezionare una delle seguenti date",
		reply_markup=data_key
	)

	return DATA_MENU


async def menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Menu principale",
		reply_markup=start_key
	)

	return AFTER_START


async def menu_inline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Menu principale",
							 reply_markup=start_key
							 )

	return AFTER_START


async def breve_descrizione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("Inviare un messaggio contenente una breve descrizione")
	return MES_DESCRIPTION


async def mem_descrizione(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	context.user_data["DESCRIZIONE"] = update.message.text
	await update.message.reply_text("Scelta memorizzata")
	await update.message.reply_text("Altri parametri", reply_markup=adv_key)

	return RIC_AVANZATA
