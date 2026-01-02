from fastapi.testclient import TestClient
from main import app
import os
import io

client = TestClient(app)

def test_upload_and_retrieve_file():
    # TEST UPLOAD
    filename = "test_file.txt"
    file_content = b"This is a test file content."
    files = {"file": (filename, io.BytesIO(file_content), "text/plain")}
    
    response = client.post("/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == filename
    assert "short_code" in data
    assert "download_url" in data
    
    short_code = data["short_code"]
    
    # TEST RETRIEVE
    response = client.get(f"/{short_code}")
    assert response.status_code == 200
    assert response.content == file_content
    
    # TEST ADMIN LIST
    response = client.get("/api/admin/files")
    assert response.status_code == 200
    files_list = response.json()
    assert len(files_list) > 0
    found = False
    file_id = None
    for f in files_list:
        if f["short_code"] == short_code:
            found = True
            file_id = f["id"]
            break
    assert found
    
    # TEST DELETE
    if file_id:
        response = client.delete(f"/api/admin/files/{file_id}")
        assert response.status_code == 200
        
        # Verify gone from list
        response = client.get("/api/admin/files")
        files_list = response.json()
        found = False
        for f in files_list:
             if f["id"] == file_id:
                  found = True
        assert not found
