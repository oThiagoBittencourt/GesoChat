import asyncio
import socketio
from Miscellaneous import ascii_logo

nickname = ""
room = None
responseEvent = asyncio.Event()
localEvent = asyncio.Event()

# Configurar o cliente Socket.IO com a verificação do certificado SSL desativada
sio = socketio.AsyncClient(ssl_verify=False)

async def overwrite_line(text):
    # Move o cursor para cima, limpa a linha e imprime o novo texto
    print(f"\n\033[F\033[K{text}", end="", flush=True)
    print(f"\n{nickname}: ", end='')

# Função de evento de conexão bem-sucedida
@sio.event
async def connect():
    print('Conectado ao servidor WebSocket')
    await request_nickname()

# Função para lidar com uma mensagem recebida do servidor
@sio.event
async def message(data):
    if 'server' in data:
       await overwrite_line(f"{data['server']}")
    else:
        await overwrite_line(f"{data['username']}: {data['message']}")

# Função para lidar com a desconexão do servidor
@sio.event
async def disconnect():
    print('Desconectado do servidor WebSocket')

@sio.on('check_nickname_response')
async def on_check_nickname_response(data):
    if data['status'] == 'available':
        asyncio.create_task(requests())
    else:
        print("\nNickname já está em uso. Tente novamente.")
        await request_nickname()

async def request_nickname():
    global nickname
    nickname = await asyncio.to_thread(input, "\nNickname: ")
    await sio.emit('check_nickname', {'nickname': nickname})

############################################################################################################
@sio.on('create_room_data')
async def create_room_data(data):
    list_data = data.split(' ')
    if len(list_data) == 4:
        await sio.emit('create_room', {'nickname': nickname, 'room' : list_data[1], 'password' : list_data[2], 'password_conf' : list_data[3]})
    elif len(list_data) == 2:
        await sio.emit('create_room', {'nickname': nickname, 'room' : list_data[1], 'password' : None, 'password_conf' : None})
    else:
        print(f'{data}\n')
        responseEvent.set()

@sio.on('create_room_request')
async def create_room_request(data):
    global room
    room = data['room']
    print(f'\n{data['nickname']} joined the room.\n')
    print('--- Type /leave do leave the room! ---\n')
    responseEvent.set()

############################################################################################################
@sio.on('enter_room_data')
async def enter_room_data(data):
    if not isinstance(data, dict):
        list_data = data.split(' ')
    
        if len(list_data) == 3:
            await sio.emit('enter_room', {'nickname': nickname, 'room' : list_data[1], 'password' : list_data[2]})
        elif len(list_data) == 2:
            await sio.emit('enter_room', {'nickname': nickname, 'room' : list_data[1], 'password' : None})
        else:
            print(f'Command invalid!\n')
            responseEvent.set()
    else:
        print(f'{data['message']}\n')
        responseEvent.set()

@sio.on('enter_room_request')
async def enter_room_request(data):
    global room
    room = data['room']
    print(f'\n{data['nickname']} joined the room.\n')
    print('--- Type /leave do leave the room! ---\n')
    responseEvent.set()

@sio.on('leave_room_request')
async def leave_room_request(data):
    global room
    room = None
    print(f'{data['nickname']} leave the room.\n')
    responseEvent.set()

############################################################################################################
@sio.on('list_rooms')
async def list_rooms(data):
    print("\n--- SALAS ---")
    for room, status in data.items():
        print(f"{room} ({status})")
    print("-------------\n")
    responseEvent.set()

############################################################################################################
async def help():
    print("\n--- COMANDOS ---")
    print("/criar NomeDaSala Senha Senha\n/entrar NomeDaSala Senha\n/listar\n/help\n/exit")
    print("----------------\n")
    localEvent.set()

############################################################################################################
@sio.on('command_not_found')
async def command_not_found(data):
    print(f'{data}\n')
    responseEvent.set()

async def requests():
    global nickname
    global room

    ascii_logo.print_logo()

    print(f'Welcome to GesoChat, {nickname}!')
    
    await help()
    
    while True:

        if room is None:
            msg = await asyncio.to_thread(input, f"{nickname}: ")
            if msg.lower() == '/exit':
                await sio.disconnect()
                break
            elif msg.lower() == '/help':
                await help()
                await localEvent.wait()
                continue
            await sio.emit('check_command', msg)
            await responseEvent.wait()
            responseEvent.clear() # Se a mensagem nn for um comando, nn tem um set disso em lugar nenhum
            localEvent.clear()
        else:
            msg = await asyncio.to_thread(input, f"{nickname}: ")
            if msg.lower() == '/exit':
                await sio.emit('message', {'message' : '/leave', 'room' : room})
                await sio.disconnect()
                break
            elif msg.lower() == '/leave':
                await sio.emit('message', {'message' : msg, 'room' : room})
                await responseEvent.wait()
                responseEvent.clear()
                continue
            await sio.emit('message', {'message' : msg, 'room' : room})
        responseEvent.clear()

############################################################################################################
# Função principal para conectar ao servidor WebSocket e enviar mensagens
async def main():
    await sio.connect('https://localhost:5000')
    await sio.wait()

# Executar a função principal em um loop de evento assíncrono
asyncio.run(main())