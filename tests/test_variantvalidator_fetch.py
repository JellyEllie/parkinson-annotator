import pytest
from Parkinsons_annotator.utils.variantvalidator_fetch import fetch_variant_validator

# Expected successful API call
def test_fetch_variant_validator_success():
    variant_description = "17:45983420:G:T"
    result = fetch_variant_validator(variant_description)
    expected = {
    "HGVS nomenclature": "NM_001377265.1:c.841G>T",
    "HGNC ID": "HGNC:6893",
    "OMIM ID": "157140"
    }
    assert result == expected

# Empty variant description provided
def test_fetch_variant_validator_empty():
    variant_description = ""
    with pytest.raises (VariantDescriptionError):
        test_fetch_variant_validator_empty(variant_description)

    