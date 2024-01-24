output "ecr_registry_id_container_exec" {
  value = trimsuffix(aws_ecr_repository.dataiku_container_exec.repository_url, "/${aws_ecr_repository.dataiku_container_exec.name}")
}

output "ecr_registry_id_apideployer" {
  value = trimsuffix(aws_ecr_repository.dataiku_apideployer.repository_url, "/${aws_ecr_repository.dataiku_apideployer.name}")
}

output "ecr_registry_id_spark_exec" {
  value = trimsuffix(aws_ecr_repository.dataiku_spark_exec.repository_url, "/${aws_ecr_repository.dataiku_spark_exec.name}")
}