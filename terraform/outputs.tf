output "public_ip" {

  value = aws_instance.secureapp.public_ip

}

output "public_dns" {

  value = aws_instance.secureapp.public_dns

}