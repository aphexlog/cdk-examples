from aws_cdk import RemovalPolicy, Stack
from aws_cdk.aws_appsync import (
    CfnGraphQLSchema,
    CfnGraphQLApi,
    CfnApiKey,
    CfnDataSource,
    CfnResolver
)
from aws_cdk.aws_dynamodb import (
    Table,
    Attribute,
    AttributeType,
    StreamViewType,
    BillingMode
)
from aws_cdk.aws_iam import (
    Role,
    ServicePrincipal,
    ManagedPolicy
)
from constructs import Construct


class GraphqlLabStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the DynamoDB table for messages
        messages_table = Table(
            self,
            "MessagesTable",
            partition_key=Attribute(
                name="conversationId",
                type=AttributeType.STRING
            ),
            sort_key=Attribute(
                name="id",
                type=AttributeType.STRING
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_IMAGE,
            removal_policy=RemovalPolicy.DESTROY  # For development only
        )

        # Create the AppSync API
        chat_api = CfnGraphQLApi(
            self,
            'ChatApi',
            name='chat-api',
            authentication_type='API_KEY'
        )

        # Create API Key
        CfnApiKey(
            self,
            'ChatApiKey',
            api_id=chat_api.attr_api_id
        )

        # Define schema
        api_schema = CfnGraphQLSchema(
            self,
            'ChatSchema',
            api_id=chat_api.attr_api_id,
            definition="""\
                type Message {
                    id: ID!
                    conversationId: String!
                    content: String!
                    sender: String!
                    timestamp: String!
                }
                type Query {
                    getConversation(conversationId: String!): [Message]
                    listConversations: [Message]
                }
                input SendMessageInput {
                    conversationId: String!
                    content: String!
                    sender: String!
                }
                type Mutation {
                    sendMessage(input: SendMessageInput!): Message
                }
                type Schema {
                    query: Query
                    mutation: Mutation
                }"""
        )

        # Create IAM role for DynamoDB access
        dynamodb_role = Role(
            self,
            'ChatDynamoDBRole',
            assumed_by=ServicePrincipal('appsync.amazonaws.com')
        )

        dynamodb_role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess')
        )

        # Create DynamoDB data source
        messages_ds = CfnDataSource(
            self,
            'MessagesDataSource',
            api_id=chat_api.attr_api_id,
            name='MessagesDynamoDataSource',
            type='AMAZON_DYNAMODB',
            dynamo_db_config=CfnDataSource.DynamoDBConfigProperty(
                table_name=messages_table.table_name,
                aws_region=self.region
            ),
            service_role_arn=dynamodb_role.role_arn
        )

        # Create resolvers
        get_conversation_resolver = CfnResolver(
            self,
            'GetConversationQueryResolver',
            api_id=chat_api.attr_api_id,
            type_name='Query',
            field_name='getConversation',
            data_source_name=messages_ds.name,
            request_mapping_template="""\
            {
                "version": "2017-02-28",
                "operation": "Query",
                "query": {
                    "expression": "conversationId = :conversationId",
                    "expressionValues": {
                        ":conversationId": $util.dynamodb.toDynamoDBJson($ctx.args.conversationId)
                    }
                }
            }""",
            response_mapping_template="$util.toJson($ctx.result.items)"
        )
        get_conversation_resolver.add_depends_on(api_schema)

        list_conversations_resolver = CfnResolver(
            self,
            'ListConversationsQueryResolver',
            api_id=chat_api.attr_api_id,
            type_name='Query',
            field_name='listConversations',
            data_source_name=messages_ds.name,
            request_mapping_template="""\
            {
                "version": "2017-02-28",
                "operation": "Scan"
            }""",
            response_mapping_template="$util.toJson($ctx.result.items)"
        )
        list_conversations_resolver.add_depends_on(api_schema)

        send_message_resolver = CfnResolver(
            self,
            'SendMessageMutationResolver',
            api_id=chat_api.attr_api_id,
            type_name='Mutation',
            field_name='sendMessage',
            data_source_name=messages_ds.name,
            request_mapping_template="""\
            {
                "version": "2017-02-28",
                "operation": "PutItem",
                "key": {
                    "conversationId": $util.dynamodb.toDynamoDBJson($ctx.args.input.conversationId),
                    "id": $util.dynamodb.toDynamoDBJson($util.autoId())
                },
                "attributeValues": {
                    "content": $util.dynamodb.toDynamoDBJson($ctx.args.input.content),
                    "sender": $util.dynamodb.toDynamoDBJson($ctx.args.input.sender),
                    "timestamp": $util.dynamodb.toDynamoDBJson($util.time.nowISO8601())
                }
            }""",
            response_mapping_template="$util.toJson($ctx.result)"
        )
        send_message_resolver.add_depends_on(api_schema)
