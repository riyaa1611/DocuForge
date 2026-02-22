"""Data fetching service for multiple sources."""

from typing import Any, Optional
from pathlib import Path

import httpx
import pandas as pd
import io
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger


class DataFetcher:
    """
    Service for fetching data from various sources.
    Supports SQL queries, REST APIs, and CSV files.
    """
    
    @classmethod
    async def fetch_from_sql(
        cls,
        session: AsyncSession,
        query: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch data using a SQL query.
        
        Args:
            session: Database session
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            result = await session.execute(text(query), params or {})
            columns = result.keys()
            rows = result.fetchall()
            
            data = [dict(zip(columns, row)) for row in rows]
            logger.debug(f"Fetched {len(data)} rows from SQL")
            
            return data
            
        except Exception as e:
            logger.error(f"SQL fetch error: {e}")
            raise
    
    @classmethod
    async def fetch_from_api(
        cls,
        url: str,
        method: str = "GET",
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Fetch data from a REST API.
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            params: Query parameters
            json_data: JSON body for POST/PUT requests
            timeout: Request timeout in seconds
            
        Returns:
            JSON response as dictionary
        """
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"Fetched data from API: {url}")
                
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"API fetch error: {e}")
            raise
    
    @classmethod
    def fetch_from_csv(
        cls,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        encoding: str = "utf-8",
        **pandas_kwargs,
    ) -> list[dict[str, Any]]:
        """
        Fetch data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            **pandas_kwargs: Additional pandas read_csv arguments
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            if content:
                # Read from content string
                df = pd.read_csv(io.StringIO(content), **pandas_kwargs)
                source_desc = "provided content"
            elif file_path:
                # Read from file path
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"CSV file not found: {file_path}")
                
                df = pd.read_csv(path, encoding=encoding, **pandas_kwargs)
                source_desc = f"file: {file_path}"
            else:
                raise ValueError("Either file_path or content must be provided")
            
            # Convert NaN to None for JSON serialization
            df = df.where(pd.notna(df), None)
            
            data = df.to_dict(orient='records')
            logger.debug(f"Fetched {len(data)} rows from CSV ({source_desc})")
            
            return data
            
        except Exception as e:
            logger.error(f"CSV fetch error: {e}")
            raise
    
    @classmethod
    def get_sample_data(cls, template_name: str) -> dict[str, Any]:
        """
        Get sample data for a template (for testing/demo purposes).
        
        Args:
            template_name: Name of the template
            
        Returns:
            Sample data dictionary
        """
        samples = {
            "financial_report.html": {
                "company_name": "Acme Corporation",
                "report_date": "2025-01-29",
                "period": "Q4 2024",
                "revenue": 1250000.00,
                "expenses": 875000.00,
                "net_income": 375000.00,
                "revenue_data": {
                    "labels": ["Oct", "Nov", "Dec"],
                    "values": [380000, 420000, 450000],
                },
                "expense_breakdown": {
                    "labels": ["Salaries", "Operations", "Marketing", "R&D", "Other"],
                    "values": [350000, 200000, 150000, 125000, 50000],
                },
                "metrics": [
                    {"name": "Gross Margin", "value": "30.0%", "change": "+2.5%"},
                    {"name": "Operating Margin", "value": "28.0%", "change": "+1.8%"},
                    {"name": "ROI", "value": "15.2%", "change": "+3.1%"},
                ],
            },
            "invoice.html": {
                "invoice_number": "INV-2025-0042",
                "invoice_date": "2025-01-29",
                "due_date": "2025-02-28",
                "company": {
                    "name": "Your Company Inc.",
                    "address": "123 Business Ave, Suite 100",
                    "city": "San Francisco, CA 94102",
                    "email": "billing@yourcompany.com",
                },
                "client": {
                    "name": "Client Corporation",
                    "address": "456 Customer Blvd",
                    "city": "New York, NY 10001",
                    "email": "accounts@clientcorp.com",
                },
                "items": [
                    {"description": "Web Development Services", "quantity": 40, "rate": 150.00, "amount": 6000.00},
                    {"description": "UI/UX Design", "quantity": 20, "rate": 125.00, "amount": 2500.00},
                    {"description": "Project Management", "quantity": 10, "rate": 100.00, "amount": 1000.00},
                ],
                "subtotal": 9500.00,
                "tax_rate": 8.5,
                "tax_amount": 807.50,
                "total": 10307.50,
            },
            "sales_summary.html": {
                "report_title": "Monthly Sales Summary",
                "report_date": "January 2025",
                "total_sales": 524750.00,
                "total_orders": 1247,
                "average_order": 420.73,
                "growth_percent": 12.5,
                "sales_by_region": {
                    "labels": ["North", "South", "East", "West"],
                    "values": [145000, 98500, 156250, 125000],
                },
                "sales_trend": {
                    "x": ["Week 1", "Week 2", "Week 3", "Week 4"],
                    "y": [98500, 115750, 142000, 168500],
                },
                "top_products": [
                    {"name": "Product A", "units": 342, "revenue": 85500},
                    {"name": "Product B", "units": 287, "revenue": 71750},
                    {"name": "Product C", "units": 245, "revenue": 61250},
                    {"name": "Product D", "units": 198, "revenue": 49500},
                    {"name": "Product E", "units": 175, "revenue": 43750},
                ],
            },
        }
        
        return samples.get(template_name, {})
