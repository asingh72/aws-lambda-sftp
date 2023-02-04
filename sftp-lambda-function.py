import json
import paramiko
import boto3
import os

def lambda_handler(event, context):

    # s3 client
    S3Client = boto3.client('s3')

    # Bucket name and Key name
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    #print("key: "+object_key)
    #print("bucket_name: "+bucket_name)

    # Downloading object
    file_name = os.path.basename(object_key)
    print("------- file name: "+file_name)
    temp_file_path='/tmp/'+file_name
    S3Client.download_file(bucket_name,object_key, temp_file_path)


    # Downloading private key
    S3Client.download_file ('sftp-bucket-ec2', 'sshKey/ec2-access.pem', '/tmp/keyname.pem')
    pem_key = paramiko.RSAKey.from_private_key_file("/tmp/keyname.pem")
    #Create a new ssh client
    SSHClient = paramiko.SSHClient()
    SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host ="Host_IP"
    SSHClient.connect(hostname=host, username="ec2-user", pkey=pem_key)
    print("Connected to:" + host)

    sftp = SSHClient.open_sftp()
    sftp.put(temp_file_path, '/home/ec2-user/test_folder/' + file_name)
    print("-------- File uploaded ----------")
    sftp.close()
    SSHClient.close()

    S3Client.delete_object(Bucket=bucket_name,Key=object_key)
    print("-------- File deleted ----------")
