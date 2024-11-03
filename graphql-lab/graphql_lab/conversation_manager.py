import boto3
import uuid
from datetime import datetime
from typing import Dict, Any, List

class ConversationManager:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def create_conversation(self, initial_message: str, sender: str) -> Dict[str, Any]:
        """
        Create a new conversation with an initial message
        """
        conversation_id = str(uuid.uuid4())
        message = {
            'conversationId': conversation_id,
            'id': str(uuid.uuid4()),
            'content': initial_message,
            'sender': sender,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=message)
        return message

    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete all messages in a conversation
        """
        # Query all messages in the conversation
        response = self.table.query(
            KeyConditionExpression='conversationId = :cid',
            ExpressionAttributeValues={
                ':cid': conversation_id
            }
        )
        
        # Delete each message
        with self.table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(
                    Key={
                        'conversationId': item['conversationId'],
                        'id': item['id']
                    }
                )
