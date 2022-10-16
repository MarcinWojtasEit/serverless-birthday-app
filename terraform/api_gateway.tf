resource "aws_apigatewayv2_api" "birthday_lambda" {
  name          = "serverless_birthday_lambda_gw"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "birthday_lambda" {
  api_id = aws_apigatewayv2_api.birthday_lambda.id

  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "aws_proxy" {
  api_id = aws_apigatewayv2_api.birthday_lambda.id

  integration_uri    = aws_lambda_function.birthday.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "post" {
  api_id = aws_apigatewayv2_api.birthday_lambda.id
  route_key = "PUT /hello/{username}"

  target    = "integrations/${aws_apigatewayv2_integration.aws_proxy.id}"
}

resource "aws_apigatewayv2_route" "get" {
  api_id    = aws_apigatewayv2_api.birthday_lambda.id
  route_key = "GET /hello/{username}"

  target    = "integrations/${aws_apigatewayv2_integration.aws_proxy.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.birthday_lambda.name}"

  retention_in_days = 7
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.birthday.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.birthday_lambda.execution_arn}/*/*"
}