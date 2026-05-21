#s3 bucket to handle state file:-
resource "aws_s3_bucket" "my-remote-s3-bucket" {
  bucket = "fitops-remote-s3-bucket1"
  region = "eu-north-1"


  tags = {
    Environment = "Production"
  }
}
resource "aws_s3_bucket_versioning" "my_bucket_versioning" {
  bucket = aws_s3_bucket.my-remote-s3-bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}


#dynamoDB
resource "aws_dynamodb_table" "remote-dynamodb-table" {
  name         = "fitops-remote-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
