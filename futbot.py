from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext , CallbackQueryHandler
from datetime import time, datetime, timedelta
from pytz import timezone 

# VARIABLES GLOBALES
# Lista de administradores (reemplaza con los IDs de usuario de los administradores del grupo)
administradores = ['obarboza92']
lista_personas = []  # conjunto para almacenar las personas y evitar duplicados
usuarios_que_usaron_voy = set()
usuarios_que_usaron_no_voy = set()
TOKEN = '6604926746:AAHRGraw5JHQhh5cUzqJsrFKMlLJJdprp_I'
chat_id = '-1002047341203' # https://api.telegram.org/bot6604926746:AAHRGraw5JHQhh5cUzqJsrFKMlLJJdprp_I/getUpdates

#obtener chat id
def obtener_chat_id(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(f'El ID del chat es: {chat_id}')


# Mensajes automaticos
def enviar_recordatorio(context: CallbackContext):
    print("Dentro de enviar_recordatorio")
    try:
        chat_id = int(context.job.context)  # Asegúrate de que el chat_id sea un entero
        print(f"ID del chat: {chat_id}")

        # Verificar si hay espacios disponibles en la lista
        campos_disponibles = 10 - len(lista_personas)
        if campos_disponibles > 0:
            mensaje = f"¡FICHAS FICHAS!\n Apuntese en la mejenga con el comando /voy para agregar su nombre. \n Si quiere agregar a otra persona con /agregar + nombre \n Espacios disponibles: {campos_disponibles} \n Atte: Blatter"
            context.bot.send_message(chat_id=chat_id, text=mensaje)
        else:
            print("No hay espacios disponibles en la lista.")
    except Exception as e:
        print(f"Error al enviar el mensaje: {str(e)}")

#MANEJO DE BOTONES
def ayuda_interactiva(update: Update, context: CallbackContext) -> None:
    # Crear botones para cada comando
    buttons = [
        [InlineKeyboardButton("Start", callback_data='start')],
        [InlineKeyboardButton("Ayuda", callback_data='ayuda')],
        [InlineKeyboardButton("Administrar Grupo", callback_data='administrar_grupo')],
        # Agrega más botones según tus comandos
    ]

    # Crear la disposición de los botones
    reply_markup = InlineKeyboardMarkup(buttons)

    # Enviar mensaje con botones
    update.message.reply_text('Selecciona un comando:', reply_markup=reply_markup)

def button_callback(update: Update, context: CallbackContext) -> None:
    # Manejar la pulsación de un botón
    query = update.callback_query
    query.answer()

    # Puedes realizar acciones específicas según el botón presionado
    if query.data == 'start':
        query.message.reply_text('¡Comando Start!')
    elif query.data == 'ayuda':
        query.message.reply_text('¡Comando Ayuda!')
    elif query.data == 'administrar_grupo':
        query.message.reply_text('¡Comando Administrar Grupo!')
    # Agrega más casos según tus comandos


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('¡Hola! Soy tu bot de administración de partidos. Puedes usar /ayuda para ver los comandos disponibles.')

def ayuda(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Lista de comandos:\n'
                              '/ayuda - Muestra este mensaje de ayuda.\n'
                              '/agregar - Agrega un nombre a la lista.\n'
                              '/remover - Remueve un nombre de la lista.\n'
                              '/lista - Muestra la lista.\n'
                              '/voy - Agrega su nombre a la lista.\n'
                              '/no_voy - Elimina su nombre de la lista\n'
                              '/disponible - Muestra la cantidad de espacios disponibles\n'
                              '/ayuda_interactiva - Muestra botones con el menu de opciones')

def comando_desconocido(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Comando no reconocido. Utiliza /ayuda para ver la lista de comandos disponibles y metase un pellizco!!!.")

def disponible(update: Update, context: CallbackContext) -> None:
    campos_disponibles = 10 - len(lista_personas)
    update.message.reply_text(f'Espacios disponibles: {campos_disponibles}, Pongale!!!!')

def administrar_grupo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Verifica si el usuario es un administrador
    if user_id in administradores:
        # Lógica de administración del grupo aquí
        update.message.reply_text('¡Comando de administración ejecutado!')
    else:
        update.message.reply_text('Lo siento, no tienes permisos para ejecutar este comando.')

def agregar(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    nombre = context.args[0] if context.args else None

    campos_disponibles = 10 - len(lista_personas)

    if campos_disponibles > 0 and nombre is not None:
        lista_personas.append({'user_id': user_id, 'nombre': nombre})
        numero_persona = len(lista_personas)
        update.message.reply_text(f'{nombre} ha sido agregado a la lista como la persona número {numero_persona}. \n'
                                  f'Campos: {campos_disponibles}')
    elif campos_disponibles == 0:
        update.message.reply_text('La lista está llena. No se pueden agregar más personas.')
    else:
        update.message.reply_text('Por favor, proporciona un nombre al agregar a la lista.')

def voy(update: Update, context: CallbackContext) -> None:
    global usuarios_que_usaron_voy

    user_id = update.message.from_user.id
    nombre_usuario = update.message.from_user.first_name

    campos_disponibles = 10 - len(lista_personas)

    if user_id in usuarios_que_usaron_voy:
        update.message.reply_text('Ya te has agregado en la lista, no puedes hacerlo nuevamente, metase en la vara!!')
    else:
        if campos_disponibles > 0:
            lista_personas.append({'user_id': user_id, 'nombre': nombre_usuario})
            numero_persona = len(lista_personas)
            update.message.reply_text(f'{nombre_usuario} ha sido agregado a la lista como la persona número {numero_persona}. '
                                  f'Campos disponibles restantes: {campos_disponibles - 1}')
            usuarios_que_usaron_voy.add(user_id)
        elif campos_disponibles == 0:
            update.message.reply_text('La lista está llena. No se pueden agregar más personas.')

def no_voy(update: Update, context: CallbackContext) -> None:
    global usuarios_que_usaron_no_voy

    user_id = update.message.from_user.id
    nombre_usuario = update.message.from_user.first_name

    if user_id in usuarios_que_usaron_no_voy:
        update.message.reply_text('Ya te has eliminado de la lista, no puedes hacerlo nuevamente, metase en la vara!!')
    else:
        # Buscamos si la persona está en la lista
        persona_en_lista = next((persona for persona in lista_personas if persona['nombre'] == nombre_usuario), None)

        if persona_en_lista:
            # Removemos a la persona de la lista
            lista_personas.remove(persona_en_lista)

            update.message.reply_text(f'{nombre_usuario} ha sido removido de la lista, hueiso!')
            
            # Actualizamos la variable global
            usuarios_que_usaron_no_voy.add(user_id)
        else:
            update.message.reply_text('No estás en la lista, no te puedes remover')

def remover(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    argumento = context.args[0].lower() if context.args else None

    if argumento:
        for i, persona in enumerate(lista_personas):
            if (str(i + 1) == argumento) or (str(persona['user_id']) == argumento) or (persona['nombre'].lower() == argumento):
                del lista_personas[i]
                update.message.reply_text(f'{persona["nombre"]} ha sido removido de la lista.')
                return

        update.message.reply_text(f'No se encontró a {persona["nombre"]}.')
    else:
        update.message.reply_text('Por favor, proporciona un número, usuario o nombre para remover de la lista.')

def lista(update: Update, context: CallbackContext) -> None:
    campos_disponibles = 10 - len(lista_personas)
    lista_texto = ''

    for i in range(10):
        if i < len(lista_personas):
            persona = lista_personas[i]
            lista_texto += f'{i + 1}. {persona["nombre"]} - (Agregado por: {context.bot.get_chat_member(update.message.chat_id, persona["user_id"]).user.username})\n'
        else:
            lista_texto += f'{i + 1}. ---\n'

    mensaje_final = f'\n\nEspacios disponibles: {campos_disponibles}'

    update.message.reply_text(f'Lista de personas:\n{lista_texto}{mensaje_final}')


def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    jq = updater.job_queue

    # Define los comandos y su correspondiente función
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ayuda", ayuda))
    dp.add_handler(CommandHandler("administrar_grupo", administrar_grupo))
    dp.add_handler(CommandHandler("agregar", agregar))
    dp.add_handler(CommandHandler("voy", voy))
    dp.add_handler(CommandHandler("no_voy", no_voy))
    dp.add_handler(CommandHandler("remover", remover))
    dp.add_handler(CommandHandler("lista", lista))
    dp.add_handler(CommandHandler("disponible", disponible))
    dp.add_handler(CommandHandler("ayuda_interactiva", ayuda_interactiva))
    dp.add_handler(CommandHandler("obtener_chat_id", obtener_chat_id))
    dp.add_handler(MessageHandler(Filters.command & Filters.user(administradores), administrar_grupo))

    
    # Inicia el bot
    updater.start_polling()

    # Manejador para comandos no reconocidos
    dp.add_handler(MessageHandler(Filters.command, comando_desconocido))

    # Manejador para botones
    dp.add_handler(CallbackQueryHandler(button_callback))

    # Mensajes automaticos

    # Configuración de zona horaria (reemplaza 'nombre_de_tu_zona_horaria' con la zona horaria adecuada)
    tz = timezone('America/Chicago')
    
    # Obtener la hora actual en la zona horaria especificada
    now = datetime.now(tz)

    # Imprimir la hora actual en formato legible
    print(f'Hora actual en {tz.zone}: {now.strftime("%A, %B %d, %Y, %I:%M %p")}')


    # Configurar los tiempos para enviar el mensaje recordatorio
    horarios = [(8, 0), (15, 0), (19, 0)]

    for hora, minuto in horarios:
        # Crear un objeto datetime para la fecha y hora actual
        ahora = datetime.now(tz)

        # Crear un objeto datetime con la misma fecha, pero con la nueva hora y minuto
        hora_utc = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

        # Convertir la hora local a UTC
        hora_utc = hora_utc.astimezone(timezone('UTC')).time()

        # Configurar el trabajo diario
        jq.run_daily(enviar_recordatorio, time=hora_utc, days=(0, 1, 2, 3, 4, 5, 6), context=chat_id)

        print(f"Job programado para enviar el recordatorio diario a las {hora}:{minuto}.")

    # Ejecuta el bot hasta que presiones Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
