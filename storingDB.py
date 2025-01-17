import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue
from threading import Semaphore
import math

server_auth_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzdkNDk0N2NiZjNkZTU4YTA3MjcyN2IiLCJvcyI6Im9zIiwiZGV2aWNlTmFtZSI6ImRldmljZU5hbWUiLCJ1c2VyVHlwZSI6ImVudGVycHJpc2UiLCJpYXQiOjE3MzY1ODQ4OTIsImV4cCI6MTczNzc5NDQ5Mn0.tdEomg9vnNUwgCPEpnd7sfbYyL65mg4QS4vtfGAKE5ZeeJn8Fyk8ZingRmhoOq8cVLXR_qQSHmHg84eJuSU7vg"


class FolderUploader:
    def __init__(self, base_url: str = "https://node-ms-f7nozesjca-em.a.run.app"):
        """Initialize the uploader with the API endpoint and concurrency control"""
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/storeDocToDbEnterprise"
        self.MAX_CONCURRENT = 1
        self.semaphore = Semaphore(self.MAX_CONCURRENT)
        
    def upload_file(self, filepath: Path, folder_name: str, description: str) -> dict:
        """Upload a single file to the database with semaphore control"""
        with self.semaphore:  # Ensure only 1 upload
            try:
                with open(filepath, 'rb') as file:
                    files = {'file': (filepath.name, file)}
                    data = {
                        'fileMod': str(int(time.time() * 1000)),
                        'folder_name': folder_name,
                        'description': description
                    }
                    
                    response = requests.post(
                        self.endpoint,
                        files=files,
                        headers={"Authorization": f"Bearer {server_auth_token}"},
                        data=data,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    return {
                        'filename': filepath.name,
                        'status': 'success',
                        'response': response.json()
                    }
                    
            except Exception as e:
                return {
                    'filename': filepath.name,
                    'status': 'error',
                    'error': str(e)
                }

    def upload_folder(self, folder_path: str, description: str = None):
        """Upload files from a folder with progress tracking"""
        folder_path = Path(folder_path)
        
        # Verify folder exists
        if not folder_path.is_dir():
            print(f"Error: Folder '{folder_path}' not found!")
            return
        
        # Use folder name as defaults
        folder_name = folder_path.name
        if description is None:
            description = f"Files from folder {folder_name}"

        # Get list of all files
        files = [f for f in folder_path.iterdir() if f.is_file()]
        
        if not files:
            print(f"No files found in folder '{folder_path}'")
            return

        total_files = len(files)
        print(f"Found {total_files} files in {folder_path}")
        print(f"Uploading with maximum {self.MAX_CONCURRENT} concurrent uploads")
        
        # Calculate number of batches
        batch_size = self.MAX_CONCURRENT
        num_batches = math.ceil(total_files / batch_size)
        
        results = []
        files_processed = 0
        
        # Process files in batches of 5
        for batch_num in range(num_batches):
            time.sleep(1)
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_files)
            batch_files = files[start_idx:end_idx]
            
            print(f"\nProcessing batch {batch_num + 1}/{num_batches}")
            
            with ThreadPoolExecutor(max_workers=self.MAX_CONCURRENT) as executor:
                future_to_file = {
                    executor.submit(self.upload_file, f, folder_name, description): f
                    for f in batch_files
                }
                
                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    files_processed += 1
                    
                    # Print progress
                    status = "✓" if result['status'] == 'success' else "✗"
                    print(f"[{files_processed}/{total_files}] {status} {result['filename']}")

        # Print summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        print("\nUpload Summary:")
        print(f"Successfully uploaded: {successful}")
        print(f"Failed uploads: {failed}")
        
        if failed > 0:
            print("\nFailed uploads:")
            for result in results:
                if result['status'] == 'error':
                    print(f"{result['filename']}: {result['error']}")

def main():
    # Example usage
    folder_path = r"C:\Users\Hp\OneDrive\Desktop\Pregnancy_Maternity artciles"  # Replace with your folder path
    description = "Batch upload from folder"  # Optional description
    
    uploader = FolderUploader()
    uploader.upload_folder(folder_path, description)

if __name__ == "__main__":
    main()