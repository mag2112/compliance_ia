# SageMaker Domain - Terraform completo

provider "aws" {
  region = "us-east-2"
}

#=======================
# IAM Execution Role (preexistente)
#=======================
variable "sagemaker_execution_role" {
  default = "arn:aws:iam::190440599924:role/datazone_usr_role_cge14z3mtzpvl5_dl3sc8ac8p84vd"
}

#=======================
# SageMaker Domain
#=======================
resource "aws_sagemaker_domain" "studio_domain" {
  domain_name = "sagemaker-studio-dev"
  auth_mode   = "IAM"
  vpc_id      = "vpc-05e3f43c40ce5a7ae"

  subnet_ids = [
    "subnet-0c9368644fd1a16bd",
    "subnet-05d1ffe519e261e1a",
    "subnet-0cf81f6aeb25b1658"
  ]

  default_user_settings {
    execution_role = var.sagemaker_execution_role
    security_groups = []

    jupyter_server_app_settings {
      default_resource_spec {
        instance_type = "system"
      }
    }
  }

  retention_policy {
    home_efs_file_system = "Delete"
  }

  tags = {
    AmazonDataZoneProject                 = "cge14z3mtzpvl5"
    AmazonDataZoneScopeName              = "dev"
    AmazonDataZoneProjectRepositoryName  = "datazone-cge14z3mtzpvl5-dev"
    ProjectS3Path                         = "s3://amazon-sagemaker-190440599924-us-east-2-xxx/cge14z3mtzpvl5/dev"
    AmazonDataZoneStage                  = "prod"
    AmazonDataZoneEnvironment            = "dl3sc8ac8p84vd"
    AmazonDataZoneDomain                 = "dzd_5a8n303w118e3t"
    AmazonDataZoneDomainAccount          = "190440599924"
    AmazonDataZoneDomainRegion           = "us-east-2"
  }
}

#=======================
# SageMaker User Profile
#=======================
resource "aws_sagemaker_user_profile" "studio_user" {
  domain_id         = aws_sagemaker_domain.studio_domain.id
  user_profile_name = "marco"

  user_settings {
    execution_role = var.sagemaker_execution_role

    jupyter_server_app_settings {
      default_resource_spec {
        instance_type = "system"
      }
    }
  }
}

#=======================
# EFS e outras opções adicionais se necessário
#=======================
# (Não necessário criar manualmente - SageMaker gerencia internamente)

output "studio_url" {
  value = aws_sagemaker_domain.studio_domain.url
}
