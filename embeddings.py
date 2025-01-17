import os
import requests
from pathlib import Path
from docx import Document

server_auth_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzdkNDk0N2NiZjNkZTU4YTA3MjcyN2IiLCJvcyI6Im9zIiwiZGV2aWNlTmFtZSI6ImRldmljZU5hbWUiLCJ1c2VyVHlwZSI6ImVudGVycHJpc2UiLCJpYXQiOjE3MzY1ODQ4OTIsImV4cCI6MTczNzc5NDQ5Mn0.tdEomg9vnNUwgCPEpnd7sfbYyL65mg4QS4vtfGAKE5ZeeJn8Fyk8ZingRmhoOq8cVLXR_qQSHmHg84eJuSU7vg"  # Replace with your actual token

class EmbeddingGenerator:
    def __init__(self, base_url: str = "https://node-ms-f7nozesjca-em.a.run.app"):
        """Initialize the EmbeddingGenerator with the base URL of the API."""
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/generateEmbeddingFromChunks"

    def generate_embeddings(self, text_chunks):
        """Generate embeddings for given text chunks.

        Args:
            text_chunks (list): List of text strings to generate embeddings for.

        Returns:
            dict: A dictionary containing the embeddings and status.
        """
        payload = {"text": text_chunks}

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {server_auth_token}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}

    def read_word_file(self, filepath):
        """Read the content of a Word file.

        Args:
            filepath (Path): Path to the Word file.

        Returns:
            str: Text content of the Word file.
        """
        try:
            doc = Document(filepath)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return ""

    def process_folder(self, folder_path):
        """Process all Word files in a folder and generate embeddings.

        Args:
            folder_path (str): Path to the folder containing Word files.
        """
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            print(f"Error: Folder '{folder_path}' not found!")
            return

        files = [f for f in folder_path.iterdir() if f.is_file() and f.suffix == '.docx']
        if not files:
            print(f"No Word files found in folder '{folder_path}'")
            return

        print(f"Found {len(files)} Word files in {folder_path}")

        for file in files:
            print(f"Processing file: {file.name}")
            text_content = self.read_word_file(file)
            if text_content.strip():
                response = self.generate_embeddings([text_content])
                if response["status"] == "true":
                    embeddings = response["embeddings"]
                    print(f"Embeddings for {file.name}: {embeddings}")
                else:
                    print(f"Failed to generate embeddings for {file.name}: {response.get('error', 'Unknown error')}")
            else:
                print(f"File {file.name} is empty or could not be read.")

# Example usage
def main():
    base_url = "https://node-ms-f7nozesjca-em.a.run.app"  # Replace with your API base URL
    folder_path = r"C:/Users/Hp/OneDrive/Desktop/Pregnancy_Maternity artciles"  # Replace with your folder path

    embedding_generator = EmbeddingGenerator(base_url)
    embedding_generator.process_folder(folder_path)

if __name__ == "__main__":
    main()