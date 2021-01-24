from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from safrs import SAFRSBase, SAFRSAPI, jsonapi_rpc
from datetime import datetime

database = SQLAlchemy()


class User(SAFRSBase, database.Model):
    """
        description: Chat application User model
    """

    __tablename__ = "Users"
    username = database.Column(database.String, primary_key=True)
    password = database.Column(database.String)
    status = database.Column(database.String, default="Offline")

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def login(cls, username, password):
        """
            description: Log in user
            summary: Log in user
            args:
                username: username
                password: password
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            result:
                                                type: string
        """

        user = database.session.query(User).filter_by(username=username).first()
        if user is None or password != user.password or username == "everyone":
            return {"result": "failed"}
        else:
            user.status = "Online"
            database.session.add(user)
            database.session.commit()
            socketio.emit("login")
            return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def logout(cls, username):
        """
            description: Log out user
            summary: Log out user
            args:
                username: username
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            result:
                                                type: string
        """

        user = database.session.query(User).filter_by(username=username).first()
        if user is None or user.status == "Offline" or username == "everyone":
            return {"result": "failed"}
        else:
            user.status = "Offline"
            database.session.add(user)
            database.session.commit()
            socketio.emit("login")
            return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def register(cls, username, password):
        """
            description: Register new user
            summary: Register new user
            args:
                username: username
                password: password
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            result:
                                                type: string
        """

        user = database.session.query(User).filter_by(username=username).first()
        if username == "everyone" or user is not None:
            return {"result": "failed"}

        user = User(username=username, password=password)

        database.session.commit()
        socketio.emit("login")
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def userList(cls):
        """
            description: Return list of chat application users
            summary: Return list of chat application users
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            users:
                                                type: array
                                                items:
                                                    type: object
                                                    properties:
                                                        username:
                                                            type: string
                                                        status:
                                                            type: string
        """

        result = {"users": []}
        for user in database.session.query(User).all():
            temp = {
                "username": user.username,
                "status": user.status
            }
            result["users"].append(temp)
        return result


class Message(SAFRSBase, database.Model):
    """
        description: Chat application Message model
    """

    __tablename__ = "Messages"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    sender = database.Column(database.String)
    to = database.Column(database.String)
    text = database.Column(database.String)
    sent = database.Column(database.String)
    read = database.Column(database.String, default="")

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def broadcastMessage(cls, sender, text):
        """
            description: Sends message to all chat application users
            summary: Sends message to all chat application users
            args:
                sender: sender
                text: text
        """
        sentDate = datetime.now().strftime("%d.%m.%y, %H:%M")
        message = Message(sender=sender, to="everyone", text=text, sent=sentDate)
        database.session.commit()
        socketio.emit("everyone")
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def sendMessage(cls, sender, to, text):
        """
            description: Sends message to specific chat application user
            summary: Sends message to specific chat application users
            args:
                sender: sender
                to: to
                text: text
        """
        sentDate = datetime.now().strftime("%d.%m.%y, %H:%M")
        message = Message(sender=sender, to=to, text=text, sent=sentDate)
        database.session.commit()
        socketio.emit("message", {"sender": sender, "to": to})
        return {"result": "success"}

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def getChat(cls, username, chat_with):
        """
            description: Gets all messages sender to an user from specific user
            summary: Gets all messages sender to an user from specific user
            args:
                username: username
                chat_with: chat_with
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    messages:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: integer
                                                sender:
                                                    type: string
                                                to:
                                                    type: string
                                                text:
                                                    type: string
                                                sent:
                                                    type: string
                                                read:
                                                    type: string
        """

        result = {"messages": []}

        def checkOneSideMsg(user1, user2):
            newMessageRead = False
            for message in database.session.query(Message).filter_by(sender=user1, to=user2).all():
                if message.read == "" and message.to == username:
                    read = datetime.now().strftime("%d.%m.%y, %H:%M")
                    message.read = read
                    newMessageRead = True
                else:
                    read = message.read

                tmp = {
                    "id": message.id,
                    "sender": message.sender,
                    "to": message.to,
                    "text": message.text,
                    "sent": message.sent,
                    "read": read
                }
                result["messages"].append(tmp)

            if newMessageRead:
                database.session.commit()
                socketio.emit("read", {"sender": chat_with, "to": username})

        checkOneSideMsg(username, chat_with)
        checkOneSideMsg(chat_with, username)

        result["messages"].sort(key=lambda message: message["id"])
        return result

    @classmethod
    @jsonapi_rpc(http_methods=['GET'])
    def getGlobalChat(cls):
        """
            description: Gets all global chat messages
            summary: Gets all global chat messages
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    messages:
                                        type: array
                                        items:
                                            type: object
                                            properties:
                                                id:
                                                    type: integer
                                                sender:
                                                    type: string
                                                to:
                                                    type: string
                                                text:
                                                    type: string
                                                sent:
                                                    type: string
                                                read:
                                                    type: string
        """

        result = {"messages": []}

        for message in database.session.query(Message).filter_by(to="everyone").order_by("id").all():
            tmp = {
                "id": message.id,
                "sender": message.sender,
                "to": message.to,
                "text": message.text,
                "sent": message.sent,
                "read": message.read
            }

            result["messages"].append(tmp)

        result["messages"].sort(key=lambda message: message["id"])
        return result

    @classmethod
    @jsonapi_rpc(http_methods=['POST'])
    def countUnreadMessages(cls, username, chat_with):
        """
            description: Returns count of unread messages from specific user
            summary: Returns count of unread messages from specific user
            args:
                username: username
                chat_with: chat_with
            responses:
                200:
                    description: OK
                    schema:
                        type: object
                        properties:
                            meta:
                                type: object
                                properties:
                                    result:
                                        type: object
                                        properties:
                                            result:
                                                type: string
        """

        unread = 0

        for message in database.session.query(Message).filter_by(sender=chat_with, to=username, read="").all():
            unread += 1

        return {"result": str(unread)}


def create_api(app, HOST="127.0.0.1", PORT=5000):
    api = SAFRSAPI(app, host=HOST, port=PORT, prefix="/api")
    api.expose_object(User)
    api.expose_object(Message)
    print("API Started: http://{}:{}/api".format(HOST, PORT))


def create_app(config_fileneme=None, HOST="localhost"):
    app = Flask("Chat application")
    app.secret_key = "QD3DV3OIS2TD4BH8AL5PI9IX3Q79SUH41GR0"
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///", DEBUG=True)
    database.init_app(app)
    with app.app_context():
        database.create_all()
        create_api(app)
    return app


application = create_app()


@application.route("/")
def showApi():
    return redirect("/api")


if __name__ == "__main__":
    socketio = SocketIO(application)
    socketio.run(application)
