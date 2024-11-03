from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_appsync as appsync,
)
from constructs import Construct

class GraphqlLabStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the DynamoDB table
        items_table = dynamodb.Table(
            self, "ItemsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # For development only
        )

        # Create the AppSync API
        api = appsync.GraphqlApi(
            self, "ItemsApi",
            name="items-api",
            schema=appsync.SchemaFile.from_asset("graphql_lab/schema.graphql")
        )

        # Create the DynamoDB data source
        items_ds = api.add_dynamo_db_data_source(
            "ItemsDataSource",
            table=items_table
        )

        # Create resolvers
        items_ds.create_resolver(
            "QueryGetItems",
            type_name="Query",
            field_name="getItems",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )

        items_ds.create_resolver(
            "MutationAddItem",
            type_name="Mutation",
            field_name="addItem",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                key=appsync.PrimaryKey.partition("id").auto(),
                values=appsync.Values.projecting("input")
            ),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
