"""Tests for chart generator service."""

import os
import pytest
from pathlib import Path

from app.services.chart_generator import ChartGenerator


class TestChartGenerator:
    """Tests for ChartGenerator service."""
    
    def test_generate_bar_chart(self):
        """Test bar chart generation."""
        data = {
            "labels": ["A", "B", "C"],
            "values": [10, 20, 30],
        }
        
        chart_path = ChartGenerator.generate_chart(
            chart_type="bar",
            data=data,
            title="Test Bar Chart",
        )
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        assert chart_path.endswith(".png")
        
        # Cleanup
        ChartGenerator.cleanup_chart(chart_path)
        assert not os.path.exists(chart_path)
    
    def test_generate_line_chart(self):
        """Test line chart generation."""
        data = {
            "x": [1, 2, 3, 4, 5],
            "y": [10, 25, 15, 30, 20],
        }
        
        chart_path = ChartGenerator.generate_chart(
            chart_type="line",
            data=data,
            title="Test Line Chart",
        )
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        
        ChartGenerator.cleanup_chart(chart_path)
    
    def test_generate_pie_chart(self):
        """Test pie chart generation."""
        data = {
            "labels": ["Category A", "Category B", "Category C"],
            "values": [30, 45, 25],
        }
        
        chart_path = ChartGenerator.generate_chart(
            chart_type="pie",
            data=data,
            title="Test Pie Chart",
        )
        
        assert chart_path is not None
        assert os.path.exists(chart_path)
        
        ChartGenerator.cleanup_chart(chart_path)
    
    def test_invalid_chart_type(self):
        """Test with invalid chart type."""
        data = {"labels": [], "values": []}
        
        with pytest.raises(ValueError):
            ChartGenerator.generate_chart(
                chart_type="invalid",
                data=data,
            )
