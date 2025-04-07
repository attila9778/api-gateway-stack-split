import aws_cdk as core
import aws_cdk.assertions as assertions

from api_gateway_poc.apigw_stack import ApiGatewayPocStack

# example tests. To run these tests, uncomment this file along with the example
# resource in api_gateway_poc/api_gateway_poc_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ApiGatewayPocStack(app, "api-gateway-poc")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
