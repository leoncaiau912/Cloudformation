from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

t = Template()

# Security Group
#AMI id and instance type
# SSH key pair

sg = ec2.SecurityGroup("LampSg")
sg.GroupDescription = "Allow access through ports 80 and 22 to the web server"
sg.SecurityGroupIngress = [
    ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
    ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp = "0.0.0.0/0"),
]

t.add_resource(sg)
keypair = t.add_parameter(Parameter(
	"KeyName",
	Description = "Name of the SSH key pair that will be used to access the instance",
	Type = "String"
   ))

instance = ec2.Instance("Webserver")
instance.ImageId = "ami-e94e5e8a"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)

ud = Base64(Join('\n',
	[
		"#!/bin/bash",
		"sudo apt-get update && sudo apt-get install apache2 -y",
		"sudo echo abc > /var/www/html/test.html",
		"service apache2 restart",
	]))

instance.UserData = ud

t.add_resource(instance)

t.add_output(Output(
	"InstanceAccess",
	Description = "Command to use to access this instance using SSH",
	Value = Join("",["ssh -i ~/.ssh/LampKey.pem ubuntu@", GetAtt(instance, "PublicDnsName")])
	))
t.add_output(Output(
	"WebUrl",
	Description = "The URL of the web server",
	Value = Join("",["http://",GetAtt(instance, "PublicDnsName")])
	))

print(t.to_json())
