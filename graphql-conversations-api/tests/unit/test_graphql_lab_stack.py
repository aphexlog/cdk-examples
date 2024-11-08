import aws_cdk as core
import aws_cdk.assertions as assertions

from app.graphql_api_stack import GraphqlLabStack


# example tests. To run these tests, uncomment this file along with the example
# resource in graphql_lab/graphql_lab_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GraphqlLabStack(app, "graphql-lab")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
