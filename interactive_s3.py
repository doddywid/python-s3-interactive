import requests
from requests_aws4auth import AWS4Auth
import boto3
import os

# Replace with your S3 credentials
access_key = "<your-s3-access-key>"
secret_key = "<your-s3-secret-key>"
region = "<your-s3-region>"  
endpoint_url = "https://<your-s3-endpoint>"
bucket_name = "<your-bucket-name>"
download_folder = "./downloads"  # Folder to save downloaded files
upload_folder = "./uploads"  # Folder where files to upload are stored

# Ensure the local download and upload folders exist
os.makedirs(download_folder, exist_ok=True)
os.makedirs(upload_folder, exist_ok=True)

# Generate AWS Signature v4 Authentication
session = boto3.session.Session()
auth = AWS4Auth(access_key, secret_key, region, "s3")

# Initialize S3 client
s3 = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key, endpoint_url=endpoint_url)

# List objects in the bucket
def list_objects():
    response = s3.list_objects_v2(Bucket=bucket_name)
    if "Contents" in response:
        print("\n📂 Objects in Bucket:")
        for obj in response["Contents"]:
            print(f"- {obj['Key']}")
    else:
        print("\n⚠️ No objects found in the bucket.")

# Upload a file to S3
def upload_file():
    filename = input("\nEnter the name of the file to upload (from 'uploads' folder): ")
    local_file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(local_file_path):
        print("❌ File not found!")
        return              

    s3_url = f"{endpoint_url}/{bucket_name}/{filename}"

    with open(local_file_path, "rb") as file_data:
        file_content = file_data.read()

    headers = {
        "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
        "Content-Type": "application/octet-stream",
    }

    response = requests.put(s3_url, data=file_content, headers=headers, auth=auth)

    if response.status_code in [200, 201]:
        print(f"✅ Successfully uploaded {filename} to S3.")
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")

# Download a file from S3
def download_file():
    filename = input("\nEnter the name of the file to download: ")
    s3_url = f"{endpoint_url}/{bucket_name}/{filename}"
    local_file_path = os.path.join(download_folder, filename)

    response = requests.get(s3_url, auth=auth)

    if response.status_code == 200:
        with open(local_file_path, "wb") as file:
            file.write(response.content)
        print(f"✅ Downloaded '{filename}' to '{local_file_path}'.")
    else:
        print(f"❌ Download failed: {response.status_code} - {response.text}")

# Delete a file from S3
def delete_file():
    filename = input("\nEnter the name of the file to delete: ")

    try:
        s3.delete_object(Bucket=bucket_name, Key=filename)
        print(f"✅ Successfully deleted '{filename}' from S3.")
    except Exception as e:
        print(f"❌ Delete failed: {str(e)}")

# Main Menu
def main():
    while True:
        print("\n=== NetApp S3 Interactive Menu ===")
        print("1️⃣ List Objects in S3")
        print("2️⃣ Upload a File")
        print("3️⃣ Download a File")
        print("4️⃣ Delete a File")
        print("5️⃣ Exit")

        choice = input("\nChoose an option (1-5): ")

        if choice == "1":
            list_objects()
        elif choice == "2":
            upload_file()
        elif choice == "3":
            download_file()
        elif choice == "4":
            delete_file()
        elif choice == "5":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid choice, please try again.")

# Run the interactive menu
if __name__ == "__main__":
    main()
