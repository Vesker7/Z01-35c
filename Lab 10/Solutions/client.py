from tkinter import *
from tkinter import scrolledtext
import api.user.openapi_client as userClient
import api.message.openapi_client as messageClient
from api.user.openapi_client.rest import ApiException
import socketio

username = ""
sio = socketio.Client()


# --- SOCKETIO EVENTS --- #

@sio.event()
def loginSignal(data):
    if data["user"] == username:
        return
    refreshUserList()


@sio.event()
def everyone():
    try:
        selected = str(userList.get(ANCHOR)).split()[0]
    except:
        selected = None
    if selected and selected == "Global":
        getChat()


@sio.event()
def read(data):
    try:
        selected = str(userList.get(ANCHOR)).split()[0]
    except:
        selected = None

    if selected and data["sender"] == username and data["to"] == selected:
        getChat()
    elif data["to"] == username:
        refreshUserList()


@sio.event()
def message(data):
    try:
        selected = str(userList.get(ANCHOR)).split()[0]
    except:
        selected = None

    if selected and data["sender"] == selected and data["to"] == username:
        getChat()
    elif data["to"] == username:
        refreshUserList()


# --- API CLIENT FUNCTIONS --- #

# --- USER ACTIONS --- #

def login(user: str, password: str) -> bool:
    meta = {
        "method": "login",
        "args": {
            "username": user,
            "password": password
        }
    }

    # Enter a context with an instance of the API client
    with userClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = userClient.UsersApi(api_client)
        post_user_login = userClient.PostUserLogin(meta=meta)  # PostUserLogin | Log in user

        try:
            # Log in user
            api_response = api_instance.loginuser0(post_user_login).to_dict()
            # pprint(api_response)
            if api_response["meta"]["result"]["result"] == "failed":
                alertLabel.config(text="Błędny login i/lub hasło!")
                return False
            else:
                sio.connect("http://127.0.0.1:5000")
                return True
        except ApiException as e:
            print("Exception when calling UsersApi->loginuser0: %s\n" % e)
            return False


def register() -> bool:
    username_toRegister = usernameEntry.get()
    password = passwordEntry.get()

    meta = {
        "method": "register",
        "args": {
            "username": username_toRegister,
            "password": password
        }
    }

    with userClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = userClient.UsersApi(api_client)
        post_user_register = userClient.PostUserRegister(meta=meta)  # PostUserRegister | Register new user

        try:
            # Register new user
            api_response = api_instance.registernewuser0(post_user_register).to_dict()

            if api_response["meta"]["result"]["result"] == "failed":
                alertLabel.config(text="Rejestracja nie powiodła się! Podany login jest już zajęty.")
                return False
            else:
                alertLabel.config(text="Rejestracja udana! Teraz możesz się zalogować.")
                return True
        except ApiException as e:
            print("Exception when calling UsersApi->registernewuser0: %s\n" % e)
            alertLabel.config(text="Rejestracja nie powiodła się!")
            return False


def logout():
    if username == "":
        root.destroy()
        return

    meta = {
        "method": "logout",
        "args": {
            "username": username
        }
    }

    with userClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = userClient.UsersApi(api_client)
        post_user_logout = userClient.PostUserLogout(meta=meta)  # PostUserLogout | Log out user

        try:
            # Log out user
            sio.disconnect()
            api_instance.logoutuser0(post_user_logout)
        except ApiException as e:
            print("Exception when calling UsersApi->logoutuser0: %s\n" % e)

    root.destroy()


def refreshUserList():
    with userClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = userClient.UsersApi(api_client)

    try:
        # Return list of chat application users
        api_response = api_instance.returnlistofchatapplicationusers0().to_dict()

        userList.delete(0, "end")
        userList.insert("end", "Global chat")

        for user in api_response["meta"]["result"]["users"]:
            if user["username"] == username:
                continue
            else:
                userList.insert("end",
                                user["username"] + " (" + user["status"] + ") " + countUnreadMessages(user["username"]))

    except ApiException as e:
        print("Exception when calling UsersApi->returnlistofchatapplicationusers0: %s\n" % e)


# --- MESSAGE ACTIONS --- #

# --- SENDING MESSAGES --- #


def send():
    destination = str(userList.get(ANCHOR)).split()[0]

    if destination == "Global":
        broadcastMessage()
    else:
        sendMessage(destination)


def broadcastMessage():
    meta = {
        "method": "broadcastMessage",
        "args": {
            "sender": username,
            "text": messagebox.get("1.0", "end")
        }
    }
    messagebox.delete("1.0", "end")

    with messageClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = messageClient.MessagesApi(api_client)
        post_message_broadcast_message = messageClient.PostMessageBroadcastMessage(
            meta=meta)  # PostMessageBroadcastMessage | Sends message to all chat application users

        try:
            # Sends message to all chat application users
            api_instance.sendsmessagetoallchatapplicationusers0(post_message_broadcast_message)
        except ApiException as e:
            print("Exception when calling MessagesApi->sendsmessagetoallchatapplicationusers0: %s\n" % e)

    return


def sendMessage(to: str):
    meta = {
        "method": "sendMessage",
        "args": {
            "sender": username,
            "to": to,
            "text": messagebox.get("1.0", "end")
        }
    }
    messagebox.delete("1.0", "end")

    with messageClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = messageClient.MessagesApi(api_client)
        post_message_send_message = messageClient.PostMessageSendMessage(
            meta=meta)  # PostMessageSendMessage | Sends message to specific chat application user

        try:
            # Sends message to specific chat application users
            api_instance.sendsmessagetospecificchatapplicationusers0(post_message_send_message)
        except ApiException as e:
            print("Exception when calling MessagesApi->sendsmessagetospecificchatapplicationusers0: %s\n" % e)

        getChat()


# --- CHAT PRINTING --- #


def getChat(*args):
    selected = str(userList.get(ANCHOR)).split()[0]
    chatWindow.delete("1.0", "end")
    if selected == "Global":
        printGlobalChat()
    else:
        printUserChat(selected)


def printGlobalChat():
    with messageClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = messageClient.MessagesApi(api_client)

    try:
        # Gets all global chat messages
        api_response = api_instance.getsallglobalchatmessages0().to_dict()

        for message in api_response["meta"]["result"]["messages"]:
            if message["sender"] == username:
                chatWindow.insert("end", 4 * "\t" + "Napisałeś/łaś:\n" + 4 * "\t" + message[
                    "text"] + "\n" + 4 * "\t" + "Wysłano: " + message["sent"] + "\n\n")
            else:
                chatWindow.insert("end", message["sender"] + " napisał:\n" + message["text"] + "\nWysłano: " +
                                  message["sent"] + "\n\n")
        chatWindow.yview("end")

    except ApiException as e:
        print("Exception when calling MessagesApi->getsallglobalchatmessages0: %s\n" % e)


def printUserChat(chat_with: str):
    meta = {
        "method": "getChat",
        "args": {
            "username": username,
            "chat_with": chat_with
        }
    }

    with messageClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = messageClient.MessagesApi(api_client)
        post_message_get_chat = messageClient.PostMessageGetChat(
            meta=meta)  # PostMessageGetChat | Gets all messages sender to an user from specific user

        try:
            # Gets all messages sender to an user from specific user
            api_response = api_instance.getsallmessagessendertoanuserfromspecificuser0(post_message_get_chat).to_dict()

            for message in api_response["meta"]["result"]["messages"]:
                if message["sender"] == username:
                    if message["read"] == "":
                        readStatus = "Nie odczytano"
                    else:
                        readStatus = "Odczytano: " + message["read"]

                    chatWindow.insert("end", 4 * "\t" + "Napisałeś/łaś:\n" + 4 * "\t" +
                                      message["text"] + "\n" + 4 * "\t" + readStatus + "\n\n")
                else:
                    chatWindow.insert("end",
                                      message["sender"] + " napisał:\n" + message["text"] + "\nWysłano: " +
                                      message["sent"] + "\n\n")
            chatWindow.yview("end")

        except ApiException as e:
            print("Exception when calling MessagesApi->getsallmessagessendertoanuserfromspecificuser0: %s\n" % e)


# --- UTILITY FUNCTIONS --- #


def countUnreadMessages(chat_with: str) -> str:
    meta = {
        "method": "countUnreadMessages",
        "args": {
            "username": username,
            "chat_with": chat_with
        }
    }

    with messageClient.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = messageClient.MessagesApi(api_client)
        post_message_count_unread_messages = messageClient.PostMessageCountUnreadMessages(
            meta=meta)  # PostMessageCountUnreadMessages | Returns count of unread messages from specific user

        try:
            # Returns count of unread messages from specific user
            api_response = api_instance.returnscountofunreadmessagesfromspecificuser0(
                post_message_count_unread_messages).to_dict()
        except ApiException as e:
            print("Exception when calling MessagesApi->returnscountofunreadmessagesfromspecificuser0: %s\n" % e)

    return api_response["meta"]["result"]["result"]


# --- GUI DRAWING FUNCTIONS --- #


def showLoginWindow(windowRoot: Tk):
    global alertLabel
    global usernameEntry
    global passwordEntry
    alertLabel = Label(windowRoot)

    usernameLabel = Label(windowRoot, text="Login:")
    usernameEntry = Entry(windowRoot, textvariable=username)

    password = StringVar()
    passwordLabel = Label(windowRoot, text="Hasło:")
    passwordEntry = Entry(windowRoot, textvariable=password, show="•")

    alertLabel.pack()
    usernameLabel.pack()
    usernameEntry.pack()
    passwordLabel.pack()
    passwordEntry.pack()

    Button(windowRoot, text="Zaloguj", command=lambda: loginValidation(root)).pack()
    Button(windowRoot, text="Zarejestruj", command=register).pack()


def loginValidation(windowRoot: Tk):
    global username
    username = usernameEntry.get()
    password = passwordEntry.get()

    if login(username, password):
        for widget in windowRoot.winfo_children():
            widget.destroy()

        usernameLabel = Label(windowRoot, text="Zalogowano jako: " + username)
        usernameLabel.pack()

        global userList
        userList = Listbox(windowRoot, width=35)
        userList.pack(side=LEFT, fill=BOTH)
        userListScrollbar = Scrollbar(windowRoot)
        userListScrollbar.pack(side=LEFT, fill=BOTH)
        userList.config(yscrollcommand=userListScrollbar.set)
        userListScrollbar.config(command=userList.yview())
        userList.bind("<<ListboxSelect>>", getChat)

        global chatWindow
        chatWindow = scrolledtext.ScrolledText(windowRoot, width=60, height=20)
        chatWindow.place(x=250, y=20)

        global messagebox
        messagebox = Text(windowRoot, width=50, height=7)
        messagebox.place(x=250, y=350)

        sendButton = Button(text="Wyślij", command=send, width=11, height=7, bg="#91bbff")
        sendButton.place(x=660, y=350)

        refreshUserList()


if __name__ == "__main__":
    root = Tk()
    root.geometry("750x470")
    root.configure()
    root.title("Chat application")
    root.protocol("WM_DELETE_WINDOW", logout)
    showLoginWindow(root)
    root.mainloop()
