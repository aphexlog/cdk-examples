import boto3
from typing import List, Dict, Any

class MessageQuerier:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all messages for a specific conversation
        """
        response = self.table.query(
            KeyConditionExpression='conversationId = :cid',
            ExpressionAttributeValues={
                ':cid': conversation_id
            }
        )
        return response.get('Items', [])

    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all messages across all conversations
        """
        response = self.table.scan()
        return response.get('Items', [])
