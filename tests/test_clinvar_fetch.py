"""
Tests for ClinVar fetch functions:
fetch_clinvar_id(),
fetch_clinvar_esummary(),
extract_clinvar_annotation().

References:
Testing APIs with PyTest
(https://codilime.com/blog/testing-apis-with-pytest-mocks-in-python/)
"""

from unittest.mock import patch
import pytest
from parkinsons_annotator.utils.clinvar_fetch import fetch_clinvar_id, fetch_clinvar_esummary, extract_clinvar_annotation, HGVSFormatError, ClinVarConnectionError, ClinVarIDFormatError

# Expected successful API call for ESearch
def test_fetch_clinvar_id_success():
    """Test that a variant in the correct HGVS notation returns the correct ClinVar ID."""
    hgvs_variant = "NM_001377265.1:c.841G>T"
    result = fetch_clinvar_id(hgvs_variant)
    expected = "578075"
    assert result == expected


# Empty HGVS variant provided
def test_fetch_clinvar_id_empty():
    """Test that empty HGVS variant strings raise HGVSFormatError."""
    hgvs_variant = ""
    with pytest.raises(HGVSFormatError):
        fetch_clinvar_id(hgvs_variant)


# Passing a non-string as the variant description
def test_fetch_clinvar_id_non_string_variant():
    """Test that non-strings raise HGVSFormatError."""
    hgvs_variant = False
    with pytest.raises(HGVSFormatError):
        fetch_clinvar_id(hgvs_variant)


# Invalid HGVS variant provided
def test_fetch_clinvar_id_invalid_hgvs_description():
    """Test that invalid HGVS variant formats raise HGVSFormatError."""
    hgvs_variant = "chr17(GRCh38):g.50198002C>A"
    with pytest.raises(HGVSFormatError):
        fetch_clinvar_id(hgvs_variant)


# API failure during ClinVar ESearch
@patch("Bio.Entrez.esearch")  # Replaces Entrez.esearch() with a mock object during this test
def test_fetch_clinvar_id_api_failure(mock_esearch):
    """Test that an API failure during ClinVar ESearch raises ClinVarConnectionError using a mocked ESearch."""
    hgvs_variant = "NM_001377265.1:c.841G>T"
    mock_esearch.side_effect = Exception()  # Simulate an API failure
    with pytest.raises(ClinVarConnectionError):
        fetch_clinvar_id(hgvs_variant)
    mock_esearch.assert_called_once()  # Verify that exactly one API call was attempted


# Empty ClinVar provided
def test_fetch_clinvar_esummary_empty():
    """Test that empty ClinVar ID strings raise ClinVarIDFormatError."""
    clinvar_id = ""
    with pytest.raises(ClinVarConnectionError):
        fetch_clinvar_esummary(clinvar_id)


# Passing a non-string as the ClinVar ID
def test_fetch_clinvar_esummary_non_string_clinvar_id():
    """Test that non-strings raise ClinVarIDFormatError."""
    clinvar_id = 5
    with pytest.raises(ClinVarIDFormatError):
        fetch_clinvar_esummary(clinvar_id)

# API failure during ClinVar ESummary
@patch("Bio.Entrez.esummary")  # Replaces Entrez.esummary() with a mock object during this test
def test_fetch_clinvar_esummary_api_failure(mock_esummary):
    """Test that an API failure during ClinVar ESummary raises ClinVarConnectionError using a mocked ESummary."""
    clinvar_id = "578075"
    mock_esummary.side_effect = Exception()  # Simulate an API failure
    with pytest.raises(ClinVarConnectionError):
        fetch_clinvar_esummary(clinvar_id)
    mock_esummary.assert_called_once()  # Verify that exactly one API call was attempted


# Expected successful extraction of ClinVar annotation from the ESummary
@patch("src.parkinsons_annotator.utils.clinvar_fetch.fetch_clinvar_id")  # Replaces 'fetch_clinvar_id' function with a mock object during this test
@patch("src.parkinsons_annotator.utils.clinvar_fetch.fetch_clinvar_esummary")  # Replaces 'fetch_clinvar_esummary' function with a mock object during this tes
def test_extract_clinvar_annotation_success(mock_esummary, mock_id):
    """Test that the correct ClinVar annotations are extracted from the ESummary."""

    mock_id.return_value = "12345"  # Mocks the ClinVar ID returned

    mock_esummary.return_value = {  # Mocks the ClinVar ESummary record
        "genes": [{"symbol": "GENE"}],
        "variation_set": [{"cdna_change": "c.123A>T"}],
        "accession": "ACCESSION123",
        "germline_classification": {
            "description": "pathogenic",
            "review_status": "criteria provided",
            "trait_set": [{"trait_name": "Condition"}],
        },
        "supporting_submissions": {"scv": [1, 2, 3]},
    }

    result = extract_clinvar_annotation("NM_001377265.1:c.841G>T") # HGVS string variant is not sent to the real ClinVar API, API calls are fully mocked above
    assert result["Gene symbol"] == "GENE"
    assert result["cDNA change"] == "c.123A>T"
    assert result["ClinVar variant ID"] == "12345"
    assert result["ClinVar accession"] == "ACCESSION123"
    assert result["ClinVar consensus classification"] == "pathogenic"
    assert result["Number of submitted records"] == 3
    assert result["Associated condition"] == "Condition"


# Missing annotation fields from ClinVar ESummary
@patch("src.parkinsons_annotator.utils.clinvar_fetch.fetch_clinvar_id")  # Replaces 'fetch_clinvar_id' function with a mock object during this test
@patch("src.parkinsons_annotator.utils.clinvar_fetch.fetch_clinvar_esummary")  # Replaces 'fetch_clinvar_esummary' function with a mock object during this test
def test_extract_clinvar_annotation_missing_fields(mock_esummary, mock_id):
    """Test that missing fields in ClinVar ESummary returns "N/A"."""

    mock_id.return_value = "12345"  # Mocks the ClinVar ID returned
    
    mock_esummary.return_value = {} # Mocks that all fields missing in ClinVar ESummary

    result = extract_clinvar_annotation("NM_001377265.1:c.841G>T")  # HGVS string variant is not sent to the real ClinVar API, API calls are fully mocked above
    assert result["Gene symbol"] == "N/A"
    assert result["cDNA change"] == "N/A"
    assert result["ClinVar accession"] == "N/A"
    assert result["ClinVar consensus classification"] == "N/A"
    assert result["Number of submitted records"] == "N/A"
    assert result["Review status"] == "N/A"
    assert result["Associated condition"] == "N/A"
    assert result["ClinVar variant ID"] == "12345"
    assert result["ClinVar record URL"].endswith("12345")
