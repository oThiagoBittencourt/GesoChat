import socketio
import ssl
import eventlet
import eventlet.wsgi

# Criando uma instância do servidor Socket.IO
sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Lista para armazenar os clientes conectados
clients = {} # [sid] = nickname
rooms = {} # [nome] = {"password": "123", "Users": ["nickname", "nickname", "nickname"], "Admins": ["nickname", "nickname"]}

# Função para lidar com a conexão de um cliente
@sio.event
def connect(sid, environ):
    print('Cliente conectado:', sid)
    clients[sid] = None

@sio.event
def message(sid, data):
    if data['message'] == '/leave':
        sio.emit('message', {'server': f'--- {clients[sid]} leave the room!'}, room=data['room'], skip_sid=sid)
        leave_room_custom(sid, data['room'], clients[sid])
    else:
        sio.emit('message', {'username': clients[sid], 'message': data['message']}, room=data['room'], skip_sid=sid)

# Função para lidar com a  de udesconexãom cliente
@sio.event
def disconnect(sid):
    print('Cliente desconectado:', sid)
    del clients[sid]

@sio.event
def check_nickname(sid, data):
    nickname = data['nickname']
    if nickname in clients.values():
        response = {'status': 'unavailable'}
    else:
        clients[sid] = nickname
        response = {'status': 'available'}
    
    sio.emit('check_nickname_response', response, to=sid)
    
############################################################################################################
@sio.event
def create_room(sid, data):
    room = data['room']
    if rooms.get(room) is not None:
        sio.emit('create_room_data', 'Room already exists.', to=sid)
    else:
        if data['password'] == data['password_conf']:
            sio.enter_room(sid, room)
            rooms[room] = {'Admins': [data['nickname']], 'password' : data['password'], 'Users' : [data['nickname']]} 
            sio.emit('create_room_request', {'nickname' : data['nickname'], 'room' : room}, to=sid)
        else:
            sio.emit('create_room_data', 'Invalid password.', to=sid)
    
@sio.event
def enter_room(sid, data):
    room = data['room']
    if room in rooms:
        if data['password'] == rooms[room]['password']:
            sio.enter_room(sid, room)
            rooms[room]['Users'].append(data['nickname'])
            sio.emit('message', {'server': f'--- {clients[sid]} enter the room!'}, room=data['room'], skip_sid=sid)
            sio.emit('enter_room_request', {'nickname' : data['nickname'], 'room' : room}, to=sid)
        else:
            sio.emit('enter_room_data',{'response' : '400', 'message' : 'The password you entered is invalid.'}, to=sid)
    else:
        sio.emit('enter_room_data', {'response' : '400', 'message' : 'Room does not exist.'}, to=sid)

def leave_room_custom(sid, room, nickname):
    sio.leave_room(sid, room)
    if room in rooms and nickname in rooms[room]['Users']:
        rooms[room]['Users'].remove(nickname)
        if not rooms[room]['Users']:
            del rooms[room]
        sio.emit('leave_room_request', {'nickname': nickname}, room=sid)

############################################################################################################
def list_rooms(sid):
    response = {}
    for room in rooms:
        response[room] = 'PRIVATE' if rooms[room]['password'] != None else 'PUBLIC'
    sio.emit('list_rooms', response, to=sid)

############################################################################################################
@sio.event
def check_command(sid, data):
    if data.startswith('/criar'):
        sio.emit('create_room_data', data, to=sid)
    elif data.startswith('/entrar'):
        sio.emit('enter_room_data', data, to=sid)
    elif data == '/listar':
        list_rooms(sid)
    else:
        sio.emit('command_not_found', 'Command Not Found!', to=sid)
  
############################################################################################################
# Inicializando o servidor na porta 5000
if __name__ == '__main__':
    # Caminhos para os arquivos de certificado SSL
    certfile = 'Server/SSL-CERT/cert.pem'
    keyfile = 'Server/SSL-CERT/privkey.pem'

    # Criar contexto SSL
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    # Inicializando o servidor WSGI com suporte a HTTPS
    listener = eventlet.wrap_ssl(eventlet.listen(('0.0.0.0', 5000)),
                                 certfile=certfile,
                                 keyfile=keyfile,
                                 server_side=True)

    print('Servidor WebSocket iniciado com HTTPS...')
    eventlet.wsgi.server(listener, app)