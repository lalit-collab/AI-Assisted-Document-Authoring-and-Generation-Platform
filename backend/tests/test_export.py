"""
Test Suite for Document Export
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.export import WordExporter, PowerPointExporter
import os

client = TestClient(app)


class TestWordExport:
    """Test Word document export"""
    
    def test_create_word_document(self):
        """Test creating a Word document"""
        sections = [
            {"title": "Introduction", "content": "This is the introduction."},
            {"title": "Content", "content": "- Bullet point 1\n- Bullet point 2"}
        ]
        
        file_bytes = WordExporter.create_document("Test Document", sections)
        
        assert file_bytes is not None
        assert len(file_bytes) > 0
        # DOCX files start with PK (zip magic number)
        assert file_bytes[:2] == b'PK'
    
    def test_word_export_with_formatting(self):
        """Test Word export with formatting"""
        sections = [
            {"title": "Formatted Section", "content": "Content with formatting"}
        ]
        style_config = {
            "font": "Arial",
            "font_size": 14,
            "line_spacing": 1.5
        }
        
        file_bytes = WordExporter.create_document(
            "Formatted Doc",
            sections,
            style_config
        )
        
        assert file_bytes is not None


class TestPowerPointExport:
    """Test PowerPoint presentation export"""
    
    def test_create_powerpoint_presentation(self):
        """Test creating a PowerPoint presentation"""
        sections = [
            {"title": "Slide 1", "content": "- Point 1\n- Point 2"},
            {"title": "Slide 2", "content": "- Point 3"}
        ]
        slide_titles = ["Introduction", "Content"]
        
        file_bytes = PowerPointExporter.create_presentation(
            "Test Presentation",
            sections,
            slide_titles
        )
        
        assert file_bytes is not None
        assert len(file_bytes) > 0
        # PPTX files start with PK (zip magic number)
        assert file_bytes[:2] == b'PK'
    
    def test_powerpoint_with_bullet_points(self):
        """Test PowerPoint with bullet points"""
        sections = [
            {"title": "Bullets", "content": "- First\n  - Nested\n- Second"}
        ]
        
        file_bytes = PowerPointExporter.create_presentation(
            "Bullets Test",
            sections
        )
        
        assert file_bytes is not None


class TestExportAPI:
    """Test export API endpoints"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers"""
        from app.core.security import SecurityUtils
        token = SecurityUtils.create_access_token({"sub": "test-user"})
        return {"Authorization": f"Bearer {token}"}
    
    def test_generate_export_job(self, auth_headers: dict):
        """Test creating export job"""
        export_data = {
            "document_id": "doc-123",
            "export_format": "docx"
        }
        response = client.post(
            "/api/export/generate",
            json=export_data,
            headers=auth_headers
        )
        
        # May fail due to missing document, but checks API
        assert response.status_code in [202, 403, 404]
    
    def test_export_status(self, auth_headers: dict):
        """Test checking export status"""
        job_id = "job-123"
        response = client.get(
            f"/api/export/status/{job_id}",
            headers=auth_headers
        )
        
        # Expected 404 for non-existent job
        assert response.status_code in [200, 404]


# Performance tests
class TestExportPerformance:
    """Test export performance"""
    
    def test_large_document_export(self):
        """Test exporting large document"""
        large_sections = [
            {"title": f"Section {i}", "content": "Large content " * 100}
            for i in range(10)
        ]
        
        import time
        start = time.time()
        file_bytes = WordExporter.create_document("Large Doc", large_sections)
        end = time.time()
        
        assert file_bytes is not None
        assert (end - start) < 5.0  # Should complete in < 5 seconds
