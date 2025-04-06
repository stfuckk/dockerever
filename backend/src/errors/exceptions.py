from src import schemas
from typing import Dict, Any, Optional
from fastapi import HTTPException


class MessagesGroup:
    def __init__(self, messages: Dict):
        self.messages = messages

    @staticmethod
    def loadJson(file_path: str) -> Any:
        import json

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def getMessage(self, messageCode: str) -> Dict:
        keys = messageCode.split(".")
        message = self.messages

        for key in keys:
            if isinstance(message, dict) and key in message:
                message = message[key]
            else:
                return {"ruText": f"??{messageCode}??", "enText": f"??{messageCode}??", "httpStatus": 500}

        if isinstance(message, dict):
            return {
                "ruText": message.get("ruText", f"??{messageCode}??"),
                "enText": message.get("enText", f"??{messageCode}??"),
                "httpStatus": message.get("httpStatus", 500),
            }


class CoreException(HTTPException):
    def __init__(self, messageCode: str, data: Optional[dict] = None):
        error = messagesGroup.getMessage(messageCode)

        core_message = schemas.CoreMessage(
            code=messageCode,
            ruText=error["ruText"],
            enText=error["enText"],
            httpStatus=error["httpStatus"] if error["httpStatus"] else 500,
            data=data,
        )

        # Подставляем HTTP-статус в ответ
        super().__init__(status_code=core_message.httpStatus, detail=core_message.model_dump())


messagesGroup = MessagesGroup(MessagesGroup.loadJson("src/errors/errors.json"))
