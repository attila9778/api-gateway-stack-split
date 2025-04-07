def lambda_handler(event: dict, context) -> None:
    print('Endpoint successfulyy called:', event['resource'])
    return {
        'statusCode': 200,
        'body': 'Endpoint successfully called: ' + event['resource']
    }
