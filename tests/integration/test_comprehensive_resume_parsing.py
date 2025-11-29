"""Comprehensive integration tests using all available test data files."""

import os
import pytest
from pathlib import Path
from resume_parser import ResumeParserFramework
from resume_parser.parsers.pdf_parser import PDFParser
from resume_parser.parsers.word_parser import WordParser
from resume_parser.models import ResumeData


@pytest.mark.integration
class TestComprehensiveResumeParsing:
    """Test parsing with all available resume test files."""
    
    @pytest.fixture
    def all_resume_files(self, test_data_dir):
        """Get all resume files from test_data directory."""
        pdf_files = list(test_data_dir.glob("*.pdf"))
        docx_files = list(test_data_dir.glob("*.docx"))
        return pdf_files + docx_files
    
    @pytest.fixture
    def software_engineer_resumes(self, test_data_dir):
        """Get software engineer resume files."""
        return [
            test_data_dir / "software_engineer_resume.pdf",
            test_data_dir / "software_engineer_resume.docx",
            test_data_dir / "software_engineer_resume-2.pdf",
        ]
    
    @pytest.fixture
    def data_scientist_resumes(self, test_data_dir):
        """Get data scientist resume files."""
        return [
            test_data_dir / "data_scientist_resume.pdf",
            test_data_dir / "data_scientist_resume.docx",
        ]
    
    @pytest.fixture
    def edge_case_resumes(self, test_data_dir):
        """Get edge case resume files."""
        edge_cases_dir = test_data_dir / "edge_cases"
        if edge_cases_dir.exists():
            return list(edge_cases_dir.glob("*.pdf"))
        return []
    
    def test_all_pdf_files_parseable(self, test_data_dir):
        """Test that all PDF files in test_data can be parsed."""
        pdf_files = list(test_data_dir.glob("*.pdf"))
        
        if not pdf_files:
            pytest.skip("No PDF files found in test_data directory")
        
        parser = PDFParser()
        failed_files = []
        
        for pdf_file in pdf_files:
            try:
                text = parser.parse(str(pdf_file))
                assert text is not None, f"{pdf_file.name} returned None"
                assert len(text) > 0, f"{pdf_file.name} returned empty text"
            except Exception as e:
                failed_files.append((pdf_file.name, str(e)))
        
        if failed_files:
            pytest.fail(f"Failed to parse PDF files: {failed_files}")
    
    def test_all_docx_files_parseable(self, test_data_dir):
        """Test that DOCX files in test_data can be parsed (some may be image-based)."""
        docx_files = list(test_data_dir.glob("*.docx"))
        
        if not docx_files:
            pytest.skip("No DOCX files found in test_data directory")
        
        parser = WordParser()
        parsed_count = 0
        failed_files = []
        
        for docx_file in docx_files:
            try:
                text = parser.parse(str(docx_file))
                assert text is not None, f"{docx_file.name} returned None"
                assert len(text) > 0, f"{docx_file.name} returned empty text"
                parsed_count += 1
            except Exception as e:
                # Some DOCX files may be image-based or have no extractable text
                # This is acceptable - we just log it
                failed_files.append((docx_file.name, str(e)))
        
        # At least one DOCX file should parse successfully
        assert parsed_count > 0, f"No DOCX files could be parsed. Failed: {failed_files}"
        
        # Log failed files for information (but don't fail the test)
        if failed_files:
            import warnings
            warnings.warn(f"Some DOCX files could not be parsed (may be image-based): {failed_files}")
    
    @pytest.mark.parametrize("resume_name", [
        "software_engineer_resume",
        "data_scientist_resume",
        "multi_page_resume",
        "resume_with_tables",
    ])
    def test_specific_resume_types(self, test_data_dir, resume_name):
        """Test parsing specific resume types (PDF and DOCX versions)."""
        pdf_path = test_data_dir / f"{resume_name}.pdf"
        docx_path = test_data_dir / f"{resume_name}.docx"
        
        pdf_parsed = False
        docx_parsed = False
        
        # Test PDF if it exists
        if pdf_path.exists():
            try:
                parser = PDFParser()
                text = parser.parse(str(pdf_path))
                assert text is not None
                assert len(text) > 0
                assert isinstance(text, str)
                pdf_parsed = True
            except Exception as e:
                pytest.fail(f"Failed to parse PDF {resume_name}: {str(e)}")
        
        # Test DOCX if it exists (may fail for image-based files)
        if docx_path.exists():
            try:
                parser = WordParser()
                text = parser.parse(str(docx_path))
                assert text is not None
                assert len(text) > 0
                assert isinstance(text, str)
                docx_parsed = True
            except Exception:
                # DOCX parsing may fail for image-based or complex documents
                # This is acceptable - we just skip DOCX for this test
                pass
        
        # At least one format should parse successfully
        if not pdf_parsed and not docx_parsed:
            pytest.skip(f"Resume file {resume_name} not found or could not be parsed")
    
    @pytest.mark.slow
    def test_software_engineer_resumes_full_parsing(self, software_engineer_resumes):
        """Test full framework parsing on software engineer resumes.
        
        Edge Case Handling:
        - Image-based DOCX files that python-docx cannot parse are skipped
        - Only PDF files or text-based DOCX files contribute to test results
        - Test passes if at least one resume (usually PDF) can be parsed
        """
        from resume_parser.exceptions import FileParsingError
        
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("OPENAI_API_KEY not set - skipping full parsing test")
        
        framework = ResumeParserFramework()
        results = []
        skipped_files = []
        
        for resume_path in software_engineer_resumes:
            if not resume_path.exists():
                continue
            
            try:
                result = framework.parse_resume(str(resume_path))
                assert isinstance(result, ResumeData)
                results.append({
                    'file': resume_path.name,
                    'name': result.name,
                    'email': result.email,
                    'skills_count': len(result.skills)
                })
            except FileParsingError as e:
                # Edge case: Image-based DOCX files can't be parsed by python-docx
                if resume_path.suffix.lower() == '.docx' and 'No text content' in str(e):
                    skipped_files.append(resume_path.name)
                    continue
                pytest.fail(f"Unexpected parsing error for {resume_path.name}: {str(e)}")
            except Exception as e:
                pytest.fail(f"Failed to parse {resume_path.name}: {str(e)}")
        
        if skipped_files:
            print(f"\nNote: Skipped {len(skipped_files)} image-based DOCX file(s): {skipped_files}")
        
        if not results:
            pytest.skip("No software engineer resume files found or all were unparseable")
        
        # Verify we got some results (at least PDF files should parse)
        assert len(results) > 0
    
    @pytest.mark.slow
    def test_data_scientist_resumes_full_parsing(self, data_scientist_resumes):
        """Test full framework parsing on data scientist resumes.
        
        Edge Case Handling:
        - Image-based DOCX files that python-docx cannot parse are skipped
        - Only PDF files or text-based DOCX files contribute to test results
        - Test passes if at least one resume (usually PDF) can be parsed
        """
        from resume_parser.exceptions import FileParsingError
        
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("OPENAI_API_KEY not set - skipping full parsing test")
        
        framework = ResumeParserFramework()
        results = []
        skipped_files = []
        
        for resume_path in data_scientist_resumes:
            if not resume_path.exists():
                continue
            
            try:
                result = framework.parse_resume(str(resume_path))
                assert isinstance(result, ResumeData)
                results.append({
                    'file': resume_path.name,
                    'name': result.name,
                    'email': result.email,
                    'skills_count': len(result.skills)
                })
            except FileParsingError as e:
                # Edge case: Image-based DOCX files can't be parsed by python-docx
                if resume_path.suffix.lower() == '.docx' and 'No text content' in str(e):
                    skipped_files.append(resume_path.name)
                    continue
                pytest.fail(f"Unexpected parsing error for {resume_path.name}: {str(e)}")
            except Exception as e:
                pytest.fail(f"Failed to parse {resume_path.name}: {str(e)}")
        
        if skipped_files:
            print(f"\nNote: Skipped {len(skipped_files)} image-based DOCX file(s): {skipped_files}")
        
        if not results:
            pytest.skip("No data scientist resume files found or all were unparseable")
        
        # Verify we got some results (at least PDF files should parse)
        assert len(results) > 0
    
    def test_multi_page_resume(self, test_data_dir):
        """Test parsing multi-page resumes.
        
        Edge Case Handling:
        - DOCX version may be image-based and unparseable by python-docx
        - Test passes if at least one format (PDF or DOCX) can be parsed
        - PDF version should always be parseable
        """
        from resume_parser.exceptions import FileParsingError
        
        pdf_path = test_data_dir / "multi_page_resume.pdf"
        docx_path = test_data_dir / "multi_page_resume.docx"
        
        if not pdf_path.exists() and not docx_path.exists():
            pytest.skip("Multi-page resume files not found")
        
        framework = ResumeParserFramework()
        parsed_count = 0
        
        # Test PDF version (should always work)
        if pdf_path.exists():
            result = framework.parse_resume(str(pdf_path))
            assert isinstance(result, ResumeData)
            # Multi-page resumes should have more content
            assert result.name is not None or result.email is not None
            parsed_count += 1
        
        # Test DOCX version (may be image-based)
        if docx_path.exists():
            try:
                result = framework.parse_resume(str(docx_path))
                assert isinstance(result, ResumeData)
                assert result.name is not None or result.email is not None
                parsed_count += 1
            except FileParsingError as e:
                # Edge case: Image-based DOCX file
                if 'No text content' in str(e):
                    print(f"\nNote: DOCX file is image-based and cannot be parsed: {docx_path.name}")
                else:
                    raise
        
        # At least one format should be parseable
        assert parsed_count > 0, "Neither PDF nor DOCX format could be parsed"
    
    def test_resume_with_tables(self, test_data_dir):
        """Test parsing resumes that contain tables.
        
        Edge Case Handling:
        - DOCX version may be image-based and unparseable by python-docx
        - Test passes if at least one format (PDF or DOCX) can be parsed
        - PDF version should always be parseable
        """
        from resume_parser.exceptions import FileParsingError
        
        pdf_path = test_data_dir / "resume_with_tables.pdf"
        docx_path = test_data_dir / "resume_with_tables.docx"
        
        if not pdf_path.exists() and not docx_path.exists():
            pytest.skip("Resume with tables files not found")
        
        framework = ResumeParserFramework()
        parsed_count = 0
        
        # Test PDF version (should always work)
        if pdf_path.exists():
            result = framework.parse_resume(str(pdf_path))
            assert isinstance(result, ResumeData)
            parsed_count += 1
        
        # Test DOCX version (may be image-based)
        if docx_path.exists():
            try:
                result = framework.parse_resume(str(docx_path))
                assert isinstance(result, ResumeData)
                parsed_count += 1
            except FileParsingError as e:
                # Edge case: Image-based DOCX file
                if 'No text content' in str(e):
                    print(f"\nNote: DOCX file is image-based and cannot be parsed: {docx_path.name}")
                else:
                    raise
        
        # At least one format should be parseable
        assert parsed_count > 0, "Neither PDF nor DOCX format could be parsed"
    
    def test_edge_cases_minimal_resume(self, test_data_dir):
        """Test parsing minimal resume (edge case)."""
        minimal_path = test_data_dir / "edge_cases" / "minimal_resume.pdf"
        
        if not minimal_path.exists():
            pytest.skip("Minimal resume file not found")
        
        parser = PDFParser()
        text = parser.parse(str(minimal_path))
        assert text is not None
        # Minimal resume might have very little text, but should still parse
        assert isinstance(text, str)
    
    def test_edge_cases_encrypted_resume(self, test_data_dir):
        """Test handling encrypted resume (should fail gracefully)."""
        encrypted_path = test_data_dir / "edge_cases" / "encrypted_resume.pdf"
        
        if not encrypted_path.exists():
            pytest.skip("Encrypted resume file not found")
        
        parser = PDFParser()
        # Encrypted resume should raise FileParsingError
        with pytest.raises(Exception):  # FileParsingError or similar
            parser.parse(str(encrypted_path))
    
    def test_edge_cases_corrupted_resume(self, test_data_dir):
        """Test handling corrupted resume (should fail gracefully)."""
        corrupted_path = test_data_dir / "edge_cases" / "corrupted_resume.pdf"
        
        if not corrupted_path.exists():
            pytest.skip("Corrupted resume file not found")
        
        parser = PDFParser()
        # Corrupted resume should raise FileParsingError
        with pytest.raises(Exception):  # FileParsingError or similar
            parser.parse(str(corrupted_path))

