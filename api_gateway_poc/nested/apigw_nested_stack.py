from aws_cdk import Stack
from aws_cdk import NestedStack
from aws_cdk import aws_apigateway

from typing import List

from api_gateway_poc.nested.lambda_integration import LambdaIntegration


class ApiGatewayNestedStack(NestedStack):

    def __init__(
        self,
        *,
        scope: Stack,
        seq_num: int,
        rest_api_name: str,
        rest_api_id: str,
        root_resource_id: str,
        lambda_integration: LambdaIntegration,
        resource_names: list,
    ):
        super().__init__(
            scope=scope,
            id=f"{rest_api_name}-nested-stack-{seq_num}"
        )

        self.methods: List[aws_apigateway.Method] = []

        rest_api = aws_apigateway.RestApi.from_rest_api_attributes(
            self,
            id=rest_api_name,
            rest_api_id=rest_api_id,
            root_resource_id=root_resource_id,
        )

        for resource_name in resource_names:
            resource = rest_api.root.add_resource(
                path_part=resource_name,

                # Note: we do have to specify method integration in NestedStacks
                # since we are out of the root stack's scope
                default_integration=lambda_integration,
            )

            # Note: we do not have to specify method integration since the REST API has a default integration
            method = resource.add_method(
                http_method="GET",
                authorization_type=aws_apigateway.AuthorizationType.IAM,
            )

            self.methods.append(method)
