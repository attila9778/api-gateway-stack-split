from aws_cdk import Stack
from aws_cdk import CfnOutput

from aws_cdk import aws_iam
from aws_cdk import aws_lambda
from aws_cdk import aws_apigateway

from constructs import Construct

import os

from typing import List

from api_gateway_poc.nested.apigw_nested_stack import ApiGatewayNestedStack
from api_gateway_poc.nested.apigw_deploy_stack import ApiGatewayDeployStack
from api_gateway_poc.nested.lambda_integration import LambdaIntegration


class ApiGatewayNestedRootStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_function = self._create_lambda_function()

        # Note: in order to prevent exceeding generated policy size for Lambda policies
        # we need to create a custom integration class that will not add permissions to
        # the Lambda function
        default_integration = self._create_default_lambda_integration(lambda_function)

        rest_api_name = "poc-api-gateway"
        self.rest_api = aws_apigateway.RestApi(
            scope=self,
            id=rest_api_name,
            rest_api_name=rest_api_name,
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],

            # Note: we need to set deploy=False to avoid creating automatic deployment and later be able to attch the custom deployment
            deploy=False,

            # Note: setting default integration will have effect only on the root resource,
            # and methods added in the current stack's scope.
            # Therefore method integrations are needed to be specified in the nested stacks
            default_integration=default_integration,
        )

        self.rest_api.root.add_method(
            http_method="ANY",

            # Note: we do not have to specify method integration in NestedStacks since the REST API has a default integration
            # integration=default_integration,

            # authorization_type=aws_apigateway.AuthorizationType.IAM,
        )
        
        # Note: we need to add permission to the Lambda function to allow API Gateway to invoke it
        lambda_function.add_permission(
            id="API invoke permission",
            principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.rest_api.arn_for_execute_api()
        )

        # until 123 we are good, at 124 limit is exceeded
        resource_names = [f"test_{n}" for n in range(124)]

        self.resource_stacks: List[ApiGatewayNestedStack] = []
        for seq, resource_name_batch in enumerate(self._batch_get_resource_names(resource_names)):
            self.resource_stacks.append(
                ApiGatewayNestedStack(
                    scope=self,
                    seq_num=seq,
                    rest_api_name=rest_api_name,
                    rest_api_id=self.rest_api.rest_api_id,
                    root_resource_id=self.rest_api.rest_api_root_resource_id,
                    lambda_integration=default_integration,
                    resource_names=resource_name_batch
                )
            )

        all_methods = []
        for resource_stack in self.resource_stacks:
            all_methods.extend(resource_stack.methods)

        self.rest_api_deployment_stack = ApiGatewayDeployStack(
            scope=self,
            rest_api_name=rest_api_name,
            rest_api_id=self.rest_api.rest_api_id,
            root_resource_id=self.rest_api.rest_api_root_resource_id,
            resource_methods=all_methods
        )

        # lambda_function.add_permission(
        #     id="API invoke permission",
        #     principal=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
        #     action="lambda:InvokeFunction",
        #     source_arn=self.get_rest_api_arn() + "/*/*"
        # )

        CfnOutput(
            scope=self,
            id="api-gateway-arn",
            value=self.get_rest_api_arn(),
            export_name="api-gateway-arn"
        )

        # Note: in case we have a custom domain name, we will need to add a base path mapping
        # domain_name.add_base_path_mapping(
        #     target_api=self.rest_api,
        #     stage=self.rest_api_deployment_stack.stage,
        # )

    @staticmethod
    def _batch_get_resource_names(base: list, batch_size: int = 20):
        for index in range(0, len(base), batch_size):
            yield base[index : index + batch_size]
            index += batch_size

    def _create_lambda_function(self) -> aws_lambda.Function:
        return aws_lambda.Function(
            scope=self,
            id="poc-lambda-function",
            function_name="poc-lambda-function",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset(os.path.join(os.getcwd(), "lambda"))
        )

    def _create_default_lambda_integration(
        self, lambda_function: aws_lambda.Function
    ) -> LambdaIntegration:
        return LambdaIntegration(
            handler=lambda_function,
            allow_test_invoke=True,
            proxy=True
        )

    def get_rest_api_arn(self) -> str:
        aws_region = os.environ.get("CDK_DEFAULT_REGION")
        stage_name = self.rest_api_deployment_stack.stage.stage_name
        return f"arn:aws:apigateway:{aws_region}::/restapis/{self.rest_api.rest_api_id}/stages/{stage_name}"
