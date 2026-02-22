import pytest
from app.services.data_fetcher import DataFetcher

def test_fetch_from_csv_content():
    csv_content = "name,age,city\nAlice,30,New York\nBob,25,Los Angeles"
    
    result = DataFetcher.fetch_from_csv(content=csv_content)
    
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[0]["age"] == 30
    assert result[0]["city"] == "New York"
    assert result[1]["name"] == "Bob"
    assert result[1]["age"] == 25
    assert result[1]["city"] == "Los Angeles"

def test_fetch_from_csv_content_empty():
    csv_content = "name,age,city"
    result = DataFetcher.fetch_from_csv(content=csv_content)
    assert len(result) == 0

def test_fetch_from_csv_error_no_input():
    with pytest.raises(ValueError, match="Either file_path or content must be provided"):
        DataFetcher.fetch_from_csv()
