from aws_cdk import Stack
from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import aws_apigateway

from constructs import Construct


class ApiGatewayPocStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_function = aws_lambda.Function(
            scope=self,
            id="poc-lambda-function",
            function_name="poc-lambda-function",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("lambda_function")
        )

        default_integration = aws_apigateway.LambdaIntegration(
            handler=lambda_function,
            allow_test_invoke=True,
            proxy=True
        )

        self.api_gateway = aws_apigateway.RestApi(
            scope=self,
            id="poc-api-gateway",
            rest_api_name="poc-api-gateway",
            api_key_source_type=aws_apigateway.ApiKeySourceType.HEADER,
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            deploy_options=aws_apigateway.StageOptions(stage_name="v0"),
            default_integration=default_integration,
            disable_execute_api_endpoint=True,
        )

        lambda_function.add_permission(
            id="API invoke permission",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.api_gateway.arn_for_execute_api()
        )
