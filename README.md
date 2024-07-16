# GesoChat 🦆💬

**A chat message using websocket with https protocol**

---

### Index:
<!--ts-->
   * [About the Project](#about-the-project)
   * [Technologies Used](#technologies-used)
   * [Functionalities](#functionalities)
   * [Research](#research)
<!--te-->

---

### About the Project:
GesoBank is a study on the development of a chat message, focusing on learning `security` methods for the job market.
The project is separated into two large parts: `Server` and `Client`

#### Server
- **Server**
- **cert.pem -** TLS certificate generated using OpenSSL
- **privkey.pem -** RSA private key generated using OpenSSL

#### Client
- **Client**

---

### Technologies Used:
- SocketIO
- Asyncio
- SSL
- Eventlet

**PIP installs:**
```
pip install python-socketio
pip install requests
pip install websocket-client
pip install aiohttp
pip install eventlet
pip install asyncio
```

---

### Functionalities:
```
Comandos:

/help
/listar
/criar NomeDaSala Senha123 Senha123
/entrar NomeDaSala Senha123
/exit

Comandos em Salas:
/leave
```

---

### Research:
- Https, TLS and SSL:
[HTTPS_e_Protocolo_TLS.pdf](https://github.com/user-attachments/files/15571861/HTTPS_e_Protocolo_TLS.pdf)

- Websockets and Webhooks:
[WebSockets_e_Webhooks.pdf](https://github.com/user-attachments/files/15571862/WebSockets_e_Webhooks.pdf)
