import boto3
import uuid
from datetime import datetime
from typing import Dict, Any

class MessageSender:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def send_message(self, conversation_id: str, content: str, sender: str) -> Dict[str, Any]:
        """
        Add a new message to a conversation
        """
        message = {
            'conversationId': conversation_id,
            'id': str(uuid.uuid4()),
            'content': content,
            'sender': sender,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=message)
        return message
