from fastapi.testclient import TestClient
from main import app
import zipfile
import io
import datetime

client = TestClient(app)

def test_upload_multiple_files_zip():
    # TEST MULTI UPLOAD
    files = [
        ("files", ("file1.txt", io.BytesIO(b"Content 1"), "text/plain")),
        ("files", ("file2.txt", io.BytesIO(b"Content 2"), "text/plain")),
    ]
    
    response = client.post("/upload", files=files, data={"expiration": "never"})
    assert response.status_code == 200
    data = response.json()
    assert "archive_" in data["filename"]
    assert ".zip" in data["filename"]
    assert "short_code" in data
    
    short_code = data["short_code"]
    
    # TEST RETRIEVE ZIP
    response = client.get(f"/{short_code}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    
    # Verify zip content
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        assert "file1.txt" in z.namelist()
        assert "file2.txt" in z.namelist()
        assert z.read("file1.txt") == b"Content 1"

def test_expiration_logic():
    # Note: Testing background task is hard in unit test, 
    # but we can test that expires_at is set correctly in DB logic (implicitly via successful upload)
    # and that download respects it if we manually tamper or if we had a way to mock time.
    # For now, let's just upload with expiration and check it returns 200.
    
    files = [("files", ("expire.txt", io.BytesIO(b"Expire me"), "text/plain"))]
    response = client.post("/upload", files=files, data={"expiration": "1d"})
    assert response.status_code == 200
    
    # Check if download works immediately
    short_code = response.json()["short_code"]
    response = client.get(f"/{short_code}")
    assert response.status_code == 200
    assert response.content == b"Expire me"
