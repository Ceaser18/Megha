import os
import requests

server_auth_token = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NzdkNDk0N2NiZjNkZTU4YTA3MjcyN2IiLCJvcyI6Im9zIiwiZGV2aWNlTmFtZSI6ImRldmljZU5hbWUiLCJ1c2VyVHlwZSI6ImVudGVycHJpc2UiLCJpYXQiOjE3MzY1ODQ4OTIsImV4cCI6MTczNzc5NDQ5Mn0.tdEomg9vnNUwgCPEpnd7sfbYyL65mg4QS4vtfGAKE5ZeeJn8Fyk8ZingRmhoOq8cVLXR_qQSHmHg84eJuSU7vg"  # Replace with your actual token

class EmbeddingSearch:
    def __init__(self, base_url: str = "https://node-ms-f7nozesjca-em.a.run.app"):
        """Initialize the EmbeddingSearch with the base URL of the API."""
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/query_vec"

    def search_embeddings(self, text, filename=None, folder_name=None):
        """Search embeddings for a given query."""
        payload = {"text": text}
        if filename:
            payload["filename"] = filename
        if folder_name:
            payload["folder_name"] = folder_name

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
            print(f"Error during API call: {e}")
            if e.response:
                print(f"Response content: {e.response.text}")
            return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    base_url = "https://node-ms-f7nozesjca-em.a.run.app"  # Replace with your API base URL

    embedding_search = EmbeddingSearch(base_url)

    while True:
        search_query = input("Enter your query (or type 'exit' to quit): ").strip()
        if search_query.lower() == 'exit':
            print("Exiting the application.")
            break

        filename = input("Enter filename to filter (optional, press Enter to skip): ").strip() or None
        folder_name = input("Enter folder name to filter (optional, press Enter to skip): ").strip() or None

        response = embedding_search.search_embeddings(
            text=search_query,
            filename=filename,
            folder_name=folder_name
        )

        if response.get("status") == "true":
            print("\nSearch results:")
            for result in response.get("results", []):
                print(f"Text: {result['text']}")
                print(f"ID: {result['id']}")
                print(f"Filename: {result['filename']}")
                print(f"Folder name: {result['folder_name']}")
                print(f"Score: {result['score']}")
                print("---")
        else:
            print(f"\nFailed to perform search: {response.get('error', 'Unknown error')}\n")
