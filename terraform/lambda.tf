resource "aws_cloudwatch_log_group" "birthday_lambda" {
  name = "/aws/lambda/birthday-func"
  retention_in_days = 7
}

data "archive_file" "birthday" {
  type        = "zip"
  source_file = "../${path.module}/src/birthday.py"
  output_path = "../${path.module}/src/birthday.zip"
}

resource "aws_lambda_function" "birthday" {
  function_name = "birthday-func"
  description   = "Function responsible for return hello birthday message for the given user and saves/updates the given user’s name and date of birth in the database"
  role          = aws_iam_role.lambda.arn
  filename      = data.archive_file.birthday.output_path
  handler       = "birthday.handler"
  runtime       = "python3.8"
  source_code_hash = data.archive_file.birthday.output_base64sha256

  environment {
    variables = {
      TABLENAME = aws_dynamodb_table.users.name,
      AWSENV = var.aws_env,
    }
  }

  depends_on = [
    aws_iam_role.lambda, aws_dynamodb_table.users
  ]
}