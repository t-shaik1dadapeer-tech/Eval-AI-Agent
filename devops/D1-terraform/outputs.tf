output "bucket_name" {
  description = "Name of the S3 bucket storing service data and Lambda artifacts."
  value       = aws_s3_bucket.service_data.id
}

output "lambda_name" {
  description = "Name of the Lambda function backing the HTTP API."
  value       = aws_lambda_function.api.function_name
}

output "lambda_arn" {
  description = "ARN of the Lambda function."
  value       = aws_lambda_function.api.arn
}

output "api_url" {
  description = "Invoke URL for the HTTP API Gateway stage."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "api_id" {
  description = "ID of the API Gateway HTTP API."
  value       = aws_apigatewayv2_api.http.id
}

output "iam_role_name" {
  description = "IAM role name used by the Lambda function."
  value       = aws_iam_role.lambda_exec.name
}
