from aws_cdk import aws_lambda
from aws_cdk import aws_apigateway


class LambdaIntegration(aws_apigateway.LambdaIntegration):
    """
        LambdaIntegration class which prevents the creation of too many policy statements.
        In case of use Lambda permissions need to be manually granted for API Gateway.

        Source: https://medium.com/@antonius.golly/how-to-fix-the-final-policy-size-x-is-bigger-than-the-limit-20480-on-api-gateway-deploys-with-4a27e4d20850
    """

    def __init__(self, handler, **kwargs):
        super().__init__(handler, **kwargs)

    def bind(self, method: aws_apigateway.Method) -> aws_apigateway.IntegrationConfig:
        integration_config = super().bind(method)

        permissions = filter(lambda x: isinstance(x, aws_lambda.CfnPermission), method.node.children)

        for permission in permissions:
            method.node.try_remove_child(permission.node.id)

        return integration_config
