from aws_cdk import Stack
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import aws_apigateway

from constructs import Construct

import os


class ApiGatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_function = aws_lambda.Function(
            scope=self,
            id="poc-lambda-function",
            function_name="poc-lambda-function",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(os.path.join(os.getcwd(), "lambda"))
        )

        default_integration = aws_apigateway.LambdaIntegration(
            handler=lambda_function,
            allow_test_invoke=True,
            proxy=True
        )

        rest_api = aws_apigateway.RestApi(
            scope=self,
            id="poc-api-gateway",
            rest_api_name="poc-api-gateway",
            api_key_source_type=aws_apigateway.ApiKeySourceType.HEADER,
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            deploy_options=aws_apigateway.StageOptions(stage_name="v1"),
            default_integration=default_integration,
            # disable_execute_api_endpoint=True,
        )

        lambda_function.add_permission(
            id="API invoke permission",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=rest_api.arn_for_execute_api()
        )

        # resource_root = rest_api.root.add_resource("test")
        # resource_root.add_method(
        #     http_method='GET',
        #     authorization_type=aws_apigateway.AuthorizationType.IAM
        # )

        # until 123 we are good, at 124 limit is exceeded
        for n in range(2):
            resource_root = rest_api.root.add_resource(f"test_{n}")
            resource_root.add_method(
                http_method='GET',
                authorization_type=aws_apigateway.AuthorizationType.IAM,
            )

