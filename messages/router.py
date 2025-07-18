from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi import  Query
from typing import List, Optional
from messages.models import message

from database import db
from user.service import *
from secuirty import *
from utilities import *
from user.responses import *

messages_router = APIRouter(tags=["messages"])

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message:dict):
        for connection in self.active_connections:
            await connection.send_json(message)

websocket_manager = WebSocketManager()


@messages_router.websocket("/ws/chat")
async def chat_websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # For example: {"username": "Fedi", "message": "Hello world"}
            await websocket_manager.send_message(data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        await websocket_manager.send_message({"message": "A user has disconnected."})

from pymongo.collection import ReturnDocument


@messages_router.post("/messages")
async def send_message(message: message, token: dict = Depends(token_required)):
    """
    API endpoint for sending a message between users.

    Args:
        message (Message): Object containing message data.
        token (dict): Authenticated user info.

    Returns:
        dict: Result message.
    """
    msg_data = message.dict()
    msg_data["timestamp"] = datetime.utcnow()

    sender = token['id']
    receiver = msg_data["receiver"]
    content = msg_data["content"]
    message_id = ObjectId()
    # Prepare conversation message entry
    conversation_message = {
        "_id": message_id,
        
                    "sender": sender,
            "receiver": receiver,
        "message": content,
        "date": datetime.utcnow(),
        "seen": False
    }
    
    # Try to find existing conversation
    existing = db["messages"].find_one({
        "$or": [
            {"sender": sender, "receiver": receiver},
            {"sender": receiver, "receiver": sender}
        ]
    })

    if existing:
        # Update the existing conversation by appending new message
        updated = db["messages"].find_one_and_update(
            {"_id": existing["_id"]},
            {
                "$push": {"conversation": conversation_message},
                "$set": {"timestamp": datetime.utcnow(), "content": content}
            },
            return_document=ReturnDocument.AFTER
        )
        conversation_id = existing["_id"]
    else:
        # Create new conversation document
        new_convo = {
            "sender": sender,
            "receiver": receiver,
            "conversation": [conversation_message],
            "timestamp": datetime.utcnow()
        }
        result = db["messages"].insert_one(new_convo)
        conversation_id = result.inserted_id

    # Notify via websocket
    await websocket_manager.send_message({
        "message": content,
        "_id": str(conversation_id),
        "To": str(receiver),
        "date": str(datetime.utcnow())
    })

    return {"message": "Message sent successfully!"}




@messages_router.patch("/messages/{conversation_id}/{message_id}/seen")
async def mark_message_as_seen(
    conversation_id: str,
    message_id: str,
    token: dict = Depends(token_required)
):
    """
    Mark a specific message as seen within a conversation.
    """
    updated = db["messages"].update_one(
        {
            "_id": ObjectId(conversation_id),
            "conversation._id": ObjectId(message_id)
        },
        {
            "$set": {
                "conversation.$.seen": True
            }
        }
    )

    if updated.modified_count == 0:
        raise HTTPException(status_code=404, detail="Message or conversation not found")

    return {"message": "Message marked as seen"}



@messages_router.get("/messages/conversations")
async def get_user_conversations(token: dict = Depends(token_required)):
    current_user_id = token.get("id")

    # Récupérer les messages
    conversations = list(db["messages"].find({
        "$or": [
            {"sender": current_user_id},
            {"receiver": current_user_id}
        ]
    }))

    user_ids = set()
    for convo in conversations:
        user_ids.add(ObjectId(convo["sender"]))
        user_ids.add(ObjectId(convo["receiver"]))

    # Récupérer les utilisateurs et convertir ObjectId en str
    users_cursor = db["users"].find({"_id": {"$in": list(user_ids)}})
    users = [{**user, "_id": str(user["_id"])} for user in users_cursor]
    user_map = {user["_id"]: user for user in users}

    enriched_conversations = []
    for convo in conversations:
        convo["_id"] = str(convo["_id"])
        convo["timestamp"] = convo["timestamp"].isoformat() if isinstance(convo["timestamp"], datetime) else str(convo["timestamp"])

        # convertir ObjectId vers str si ce n'est pas déjà
        convo["sender"] = str(convo["sender"])
        convo["receiver"] = str(convo["receiver"])

        convo["sender_data"] = user_map.get(convo["sender"])
        convo["receiver_data"] = user_map.get(convo["receiver"])

        for msg in convo.get("conversation", []):
            msg["_id"] = str(msg["_id"])
            msg["date"] = msg["date"].isoformat() if isinstance(msg["date"], datetime) else str(msg["date"])

        enriched_conversations.append(convo)

    return {"conversations": enriched_conversations}

