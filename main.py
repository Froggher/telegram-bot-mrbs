import logging

from lib import *
from not_security import get_token

# Fare un controllo per non prendere le date indietro

# Enable logging
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Start the conversation and ask user for input."""

	await update.message.reply_text(
		"Ciao " + update.message.from_user.name + " selezionare una delle seguenti opzioni",
		reply_markup=start_key
	)
	# Tenere i default dei risultati del tempo
	context.user_data['T1'] = datetime.now()
	context.user_data['T2'] = datetime.now()
	context.user_data['CORSO'] = ""
	context.user_data["ESAME"] = ""
	context.user_data["AULA"] = ""
	context.user_data["DESCRIZIONE"] = ""
	context.user_data["PROF"] = []

	context.chat_data['grouped_events'] = []

	corso = "Default"
	aula = "Tutte"
	esame = "No"
	descrizione = "Assente"
	# Vengono salvate le date di oggi come default
	data_iniziale = context.user_data['T1'].strftime("%d/%m/%Y")
	data_finale = context.user_data['T2'].strftime("%d/%m/%Y")

	await update.message.reply_text("I dati iniziali sono: \n\nData iniziale: " + data_iniziale +
									"\nData finale: " + data_finale + "\nTipo corso selezionato: " + corso + "\nAula selezionata: " + aula + "\nMostrare solo esami: " + esame + "\nDescrizione breve: " + descrizione)
	await update.message.reply_text(
		"N.B. se ci sono troppi dati il bot non riuscirá a rispondere❌.\nIn caso diminuire l'arco temporale di ricerca")

	return AFTER_START


async def mostra_corso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("Effettuare una scelta tra i seguenti corsi di studio", reply_markup=studio_key)
	return QUERY_TIPO_CORSO


async def mem_corso_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	# https://stackoverflow.com/questions/3965104/not-none-test-in-python
	# https://www.edureka.co/blog/key-error-in-python/
	query = update.callback_query
	await query.answer()
	querydata = query.data

	if querydata == "Indietro":
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Altri parametri", reply_markup=adv_key)
		return RIC_AVANZATA

	context.user_data["CORSO"] = querydata

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Scelta memorizzata")
	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Altri parametri", reply_markup=adv_key)

	return RIC_AVANZATA


async def aula(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("Effettuare una scelta tra le seguenti aule", reply_markup=aule_key)
	return QUERY_AULA


async def mem_aula(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	querydata = query.data

	if querydata == "Indietro":
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Altri parametri", reply_markup=adv_key)
		return RIC_AVANZATA

	context.user_data["AULA"] = querydata

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Scelta memorizzata")
	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Altri parametri", reply_markup=adv_key)

	return RIC_AVANZATA


async def aule_libere(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	user_data = context.user_data
	category1 = user_data['T1']
	category2 = user_data['T2']
	# Mostra che il bot che sta scrivendo
	context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

	todays_events = event_query(category1, category2, only_aula=True)
	await update.message.reply_text(
		"Sono state trovate " + str(len(todays_events)) + " aule libere" + "".join("\n🗓 " + x for x in todays_events),
		reply_markup=start_key)

	return AFTER_START


async def esame(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text(
		"Mostrare soltanto esami?",
		reply_markup=si_no_key
	)
	return QUERY_ESAME


async def mem_esame(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	querydata = query.data
	# Il campo non utilizzato è stato comunque qui lasciato
	if querydata == "Indietro":
		context.bot.send_message(chat_id=update.callback_query.from_user.id,
								 text="Altri parametri", reply_markup=adv_key)
		return RIC_AVANZATA

	context.user_data["ESAME"] = int(querydata)

	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Scelta memorizzata")
	context.bot.send_message(chat_id=update.callback_query.from_user.id,
							 text="Altri parametri", reply_markup=adv_key)

	return RIC_AVANZATA


async def visualizza_parametri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	corso = context.user_data['CORSO']
	esame = context.user_data["ESAME"]
	aula = context.user_data["AULA"]
	descrizione = context.user_data['DESCRIZIONE']
	prof = context.user_data['PROF']

	data_iniziale = context.user_data['T1'].strftime("%d/%m/%Y")
	data_finale = context.user_data['T2'].strftime("%d/%m/%Y")

	if context.user_data['CORSO'] == "":
		corso = "Default"

	if context.user_data['AULA'] == "":
		aula = "Tutte"

	if context.user_data['ESAME'] == "" or context.user_data['ESAME'] == NO:
		esame = "No"

	if context.user_data['ESAME'] == SI:
		esame = "Si"

	if context.user_data['DESCRIZIONE'] == "":
		descrizione = "Assente"

	if context.user_data['PROF'] == []:
		prof = "Tutti"

	else:
		prof = ", ".join(prof)

	await update.message.reply_text(
		"Sono stati selezionati i seguenti filtri di ricerca\n\nData iniziale: " + data_iniziale +
		"\nData finale: " + data_finale + "\nTipo corso selezionato: " + corso + "\nAula selezionata: " + aula + "\nMostrare solo esami: " + esame +
		"\nDescrizione breve: " + descrizione + "\nProfessori selezionati: " + prof)

	await update.message.reply_text("Confermare per la ricerca?", reply_markup=ric_key)

	return PRE_RICERCA


async def cancella_parametri(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	context.user_data['T1'] = datetime.now()
	context.user_data['T2'] = datetime.now()
	context.user_data['CORSO'] = ""
	context.user_data["ESAME"] = ""
	context.user_data["AULA"] = ""
	context.user_data['DESCRIZIONE'] = ""
	context.user_data['PROF'] = []

	await update.message.reply_text("I parametri sono stati reimpostati ai valori di default")

	corso = "Default"
	aula = "Tutte"
	esame = "No"
	descrizione = "Assente"
	prof = "Tutti"

	data_iniziale = context.user_data['T1'].strftime("%d/%m/%Y")
	data_finale = context.user_data['T2'].strftime("%d/%m/%Y")

	await update.message.reply_text(
		"Sono stati selezionati i seguenti filtri di ricerca\n\nData iniziale: " + data_iniziale +
		"\nData finale: " + data_finale + "\nTipo corso selezionato: " + corso + "\nAula selezionata: " + aula + "\nMostrare solo esami: " + esame +
		"\nDescrizione breve: " + descrizione + "\nProfessori selezionati: " + prof)

	await update.message.reply_text("Menu principale", reply_markup=start_key)

	return AFTER_START


async def quit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	await update.message.reply_text("Il bot viene disattivato, arrivederci", reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END


def main() -> None:
	"""Start the bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(get_token()).build()

	# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
	conv_handler = ConversationHandler(per_message=False,
									   entry_points=[
										   CommandHandler('start', start),
									   ],

									   states={
										   AFTER_START: [
											   MessageHandler(filters.Regex('Cambia data$'), data_menu),
											   MessageHandler(filters.Regex('Ricerca$'), stampa_risultato_text),
											   MessageHandler(filters.Regex('Altri Parametri$'), ric_avanzata),
											   MessageHandler(filters.Regex('Cancella parametri$'), cancella_parametri),
											   MessageHandler(filters.Regex('Aule libere$'), aule_libere),
											   MessageHandler(filters.Regex('Ricerca per oggi$'),
															  stampa_risultato_text),
										   ],

										   RIC_AVANZATA: [
											   MessageHandler(filters.Regex('Professori$'), pre_find_professor),
											   MessageHandler(filters.Regex('Esame$'), esame),
											   MessageHandler(filters.Regex('Scelta aule$'), aula),
											   MessageHandler(filters.Regex('Corso di studi$'), mostra_corso),
											   MessageHandler(filters.Regex('Menu$'), menu_text),
											   MessageHandler(filters.Regex('Ricerca$'), stampa_risultato_text),
											   MessageHandler(filters.Regex('Breve descrizione$'), breve_descrizione),
											   MessageHandler(filters.Regex('Parametri impostati$'),
															  visualizza_parametri),
										   ],

										   DATA_MENU: [
											   MessageHandler(filters.Regex('Oggi$'), mem_settimana),
											   MessageHandler(filters.Regex('Questa settimana$'), mem_settimana),
											   MessageHandler(filters.Regex('Da oggi a \.\.\.$'), crea_calendario),
											   MessageHandler(filters.Regex('Da \.\.\. a \.\.\.$'), crea_calendario),
											   MessageHandler(filters.Regex('Torna al menu$'), menu_text),
										   ],

										   PROF_MESSAGE: [
											   MessageHandler(filters.ALL, start_find_prof),
										   ],

										   QUERY_TIPO_CORSO: [
											   CallbackQueryHandler(mem_corso_query),
										   ],

										   QUERY_ESAME: [
											   CallbackQueryHandler(mem_esame, pattern='' + str(SI) + '$'),
											   CallbackQueryHandler(mem_esame, pattern='' + str(NO) + '$'),
										   ],

										   QUERY_AULA: [
											   CallbackQueryHandler(mem_aula),
										   ],

										   MES_DESCRIPTION: [
											   MessageHandler(filters.ALL, mem_descrizione),
										   ],

										   DATA1_CALENDARIO: [
											   CallbackQueryHandler(calendario_data1),

										   ],
										   DATA2_CALENDARIO: [
											   CallbackQueryHandler(calendario_data2),
										   ],

										   PRE_RICERCA: [
											   CallbackQueryHandler(stampa_risultato_inline,
																	pattern='' + str(SI) + '$'),
											   CallbackQueryHandler(menu_inline, pattern='' + str(NO) + '$'),
										   ],

										   DOPO_RICERCA: [
											   CallbackQueryHandler(button),
											   MessageHandler(filters.Regex('Cancella parametri$'), cancella_parametri),
											   MessageHandler(filters.Regex('Cambia Parametri$'), ric_avanzata),
											   MessageHandler(filters.Regex('Torna al menu$'), menu_text),
										   ],

									   },
									   fallbacks=[MessageHandler(filters.Regex('Reset$'), start),
												  CommandHandler('quit', quit_command), ],
									   )

	application.add_handler(conv_handler)

	# Run the bot until the user presses Ctrl-C
	application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
	main()
