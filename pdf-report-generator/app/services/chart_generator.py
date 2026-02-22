"""Chart generation service using Matplotlib."""

import os
import uuid
from pathlib import Path
from typing import Any, Optional, Literal
from datetime import datetime

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from loguru import logger

from app.core.config import settings


ChartType = Literal["bar", "line", "pie", "area", "scatter"]


class ChartGenerator:
    """
    Service for generating charts using Matplotlib.
    Supports bar, line, pie, area, and scatter charts.
    """

    # Default color palette
    COLORS = [
        "#4F46E5",  # Indigo
        "#10B981",  # Emerald
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#06B6D4",  # Cyan
        "#F97316",  # Orange
        "#84CC16",  # Lime
    ]

    @classmethod
    def get_temp_path(cls) -> Path:
        """Get the temp directory for chart images."""
        temp_path = Path(settings.storage_path) / "temp"
        temp_path.mkdir(parents=True, exist_ok=True)
        return temp_path

    @classmethod
    def generate_chart(
        cls,
        chart_type: ChartType,
        data: dict[str, Any],
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        figsize: tuple[int, int] = (10, 6),
        colors: Optional[list[str]] = None,
    ) -> str:
        """
        Generate a chart and save it to a temporary file.

        Args:
            chart_type: Type of chart (bar, line, pie, area, scatter)
            data: Chart data (format depends on chart type)
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size in inches
            colors: Custom color palette

        Returns:
            Path to the generated chart image
        """
        colors = colors or cls.COLORS

        fig, ax = plt.subplots(figsize=figsize)

        # Apply styling
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if chart_type == "bar":
            cls._create_bar_chart(ax, data, colors)
        elif chart_type == "line":
            cls._create_line_chart(ax, data, colors)
        elif chart_type == "pie":
            cls._create_pie_chart(ax, data, colors)
        elif chart_type == "area":
            cls._create_area_chart(ax, data, colors)
        elif chart_type == "scatter":
            cls._create_scatter_chart(ax, data, colors)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Set labels and title
        if title:
            ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=11)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=11)

        # Style the chart
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(labelsize=10)

        # Generate unique filename
        filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        filepath = cls.get_temp_path() / filename

        # Save chart
        plt.tight_layout()
        fig.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        logger.debug(f"Generated chart: {filepath}")
        return str(filepath)

    @classmethod
    def _create_bar_chart(cls, ax, data: dict, colors: list) -> None:
        """Create a bar chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])

        if isinstance(values[0], list):
            # Grouped bar chart
            n_groups = len(labels)
            n_bars = len(values)
            width = 0.8 / n_bars

            for i, (series_values, series_name) in enumerate(
                zip(values, data.get("series_names", []))
            ):
                positions = [x + i * width for x in range(n_groups)]
                ax.bar(
                    positions,
                    series_values,
                    width,
                    label=series_name,
                    color=colors[i % len(colors)],
                )

            ax.set_xticks([x + width * (n_bars - 1) / 2 for x in range(n_groups)])
            ax.set_xticklabels(labels)
            ax.legend()
        else:
            # Simple bar chart
            bar_colors = (
                colors[: len(values)]
                if len(values) <= len(colors)
                else colors * (len(values) // len(colors) + 1)
            )
            ax.bar(labels, values, color=bar_colors[: len(values)])

    @classmethod
    def _create_line_chart(cls, ax, data: dict, colors: list) -> None:
        """Create a line chart."""
        x = data.get("x", [])
        y_series = data.get("y", [])
        series_names = data.get("series_names", [])

        # Handle date x-axis
        if x and isinstance(x[0], (str, datetime)):
            try:
                x = [
                    datetime.fromisoformat(str(d)) if isinstance(d, str) else d
                    for d in x
                ]
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.xticks(rotation=45)
            except ValueError:
                pass

        if isinstance(y_series[0], list):
            # Multiple series
            for i, (y, name) in enumerate(zip(y_series, series_names)):
                ax.plot(
                    x,
                    y,
                    label=name,
                    color=colors[i % len(colors)],
                    linewidth=2,
                    marker="o",
                    markersize=4,
                )
            ax.legend()
        else:
            # Single series
            ax.plot(x, y_series, color=colors[0], linewidth=2, marker="o", markersize=4)

        ax.grid(True, alpha=0.3)

    @classmethod
    def _create_pie_chart(cls, ax, data: dict, colors: list) -> None:
        """Create a pie chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors[: len(values)],
            autopct="%1.1f%%",
            startangle=90,
            explode=[0.02] * len(values),
        )

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight("bold")

    @classmethod
    def _create_area_chart(cls, ax, data: dict, colors: list) -> None:
        """Create an area chart."""
        x = data.get("x", [])
        y_series = data.get("y", [])
        series_names = data.get("series_names", [])

        if isinstance(y_series[0], list):
            for i, (y, name) in enumerate(zip(y_series, series_names)):
                ax.fill_between(
                    x, y, alpha=0.4, color=colors[i % len(colors)], label=name
                )
                ax.plot(x, y, color=colors[i % len(colors)], linewidth=2)
            ax.legend()
        else:
            ax.fill_between(x, y_series, alpha=0.4, color=colors[0])
            ax.plot(x, y_series, color=colors[0], linewidth=2)

        ax.grid(True, alpha=0.3)

    @classmethod
    def _create_scatter_chart(cls, ax, data: dict, colors: list) -> None:
        """Create a scatter chart."""
        x = data.get("x", [])
        y = data.get("y", [])
        sizes = data.get("sizes", [50] * len(x))

        ax.scatter(
            x, y, s=sizes, c=colors[0], alpha=0.6, edgecolors="white", linewidths=1
        )
        ax.grid(True, alpha=0.3)

    @classmethod
    def cleanup_chart(cls, filepath: str) -> None:
        """Remove a chart file after use."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"Cleaned up chart: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to cleanup chart {filepath}: {e}")
