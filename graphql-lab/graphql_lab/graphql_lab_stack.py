from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_appsync as appsync,
)
from constructs import Construct

class GraphqlLabStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the DynamoDB table for messages
        messages_table = dynamodb.Table(
            self, "MessagesTable",
            partition_key=dynamodb.Attribute(
                name="conversationId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # For development only
        )

        # Create the AppSync API
        api = appsync.GraphqlApi(
            self, "ChatApi",
            name="chat-api",
            schema=appsync.SchemaFile.from_asset("graphql_lab/schema.graphql")
        )

        # Create the DynamoDB data source
        messages_ds = api.add_dynamo_db_data_source(
            "MessagesDataSource",
            table=messages_table
        )

        # Create resolvers
        messages_ds.create_resolver(
            "QueryGetConversation",
            type_name="Query",
            field_name="getConversation",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_query(
                key_condition_expression=appsync.KeyCondition.eq("conversationId", "conversationId")
            ),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )

        messages_ds.create_resolver(
            "QueryListConversations",
            type_name="Query",
            field_name="listConversations",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )

        messages_ds.create_resolver(
            "MutationSendMessage",
            type_name="Mutation",
            field_name="sendMessage",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                key=appsync.PrimaryKey.partition("conversationId").sort("id").auto(),
                values={
                    "content": appsync.Values.from_string("input.content"),
                    "sender": appsync.Values.from_string("input.sender"),
                    "timestamp": appsync.Values.from_string("$util.time.nowISO8601()")
                }
            ),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
