provider "aws" {
  region = "us-east-2"
}

data "aws_caller_identity" "current" {}

resource "aws_opensearch_domain" "compliance" {
  domain_name    = "compliance-opensearch"
  engine_version = "OpenSearch_2.19"

  cluster_config {
    instance_type          = "r5.large.search"
    instance_count         = 1
    zone_awareness_enabled = false
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"
    volume_size = 10
  }

  vpc_options {
    subnet_ids         = ["subnet-0cf81f6aeb25b1658"]
    security_group_ids = ["sg-0c238d57ccd13a89d"]
  }

  node_to_node_encryption {
    enabled = true
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_arn = "arn:aws:iam::190440599924:user/marco001"
    }
  }

  access_policies = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = { AWS = "*" },
        Action    = "es:*",
        Resource  = "arn:aws:es:us-east-2:${data.aws_caller_identity.current.account_id}:domain/compliance-opensearch/*"
      }
    ]
  })

  snapshot_options {
    automated_snapshot_start_hour = 0
  }
}
