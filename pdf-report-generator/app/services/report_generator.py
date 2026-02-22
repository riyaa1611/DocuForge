"""Report generation orchestration service."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.report import Report, ReportStatus
from app.models.template import Template
from app.services.pdf_generator import PDFGenerator
from app.services.chart_generator import ChartGenerator
from app.services.template_renderer import TemplateRenderer
from app.services.data_fetcher import DataFetcher
from app.services.storage import StorageService


class ReportGeneratorService:
    """
    Orchestration service for the complete report generation pipeline.

    Pipeline: Fetch Data → Generate Charts → Render HTML → Generate PDF → Save
    """

    @classmethod
    async def generate_report(
        cls,
        session: AsyncSession,
        report_id: uuid.UUID,
    ) -> None:
        """
        Generate a report by ID.

        This is the main entry point for report generation.
        Updates report status throughout the process.

        Args:
            session: Database session
            report_id: ID of the report to generate
        """
        chart_files = []

        try:
            # Get report
            report = await session.get(Report, report_id)
            if not report:
                logger.error(f"Report not found: {report_id}")
                return

            # Update status to processing
            report.status = ReportStatus.PROCESSING
            report.started_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"Starting report generation: {report_id}")

            # Get template
            template = await session.get(Template, report.template_id)
            if not template:
                raise ValueError(f"Template not found: {report.template_id}")

            # Fetch data
            data = await cls._fetch_data(session, report.params, template.name)

            # Generate charts
            chart_data = cls._extract_chart_data(data)
            for chart_config in chart_data:
                chart_path = ChartGenerator.generate_chart(
                    chart_type=chart_config["type"],
                    data=chart_config["data"],
                    title=chart_config.get("title"),
                    xlabel=chart_config.get("xlabel"),
                    ylabel=chart_config.get("ylabel"),
                )
                chart_files.append(chart_path)

                # Convert to base64 for embedding
                chart_config["base64"] = TemplateRenderer.image_to_base64(chart_path)

            # Prepare template context
            context = cls._prepare_context(data, chart_data)

            # Render HTML
            html = TemplateRenderer.render_template(template.name, context)

            # Generate PDF
            pdf_bytes = await PDFGenerator.generate_pdf(html)

            # Save PDF
            filename = f"report_{report_id.hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, file_size = await StorageService.save_pdf(pdf_bytes, filename)

            # Update report
            report.status = ReportStatus.COMPLETED
            report.file_path = file_path
            report.file_size = file_size
            report.completed_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(f"Report generated successfully: {report_id}")

        except Exception as e:
            logger.error(f"Report generation failed: {report_id}, error: {e}")

            # Update report with error
            report = await session.get(Report, report_id)
            if report:
                report.status = ReportStatus.FAILED
                report.error_message = str(e)
                report.completed_at = datetime.now(timezone.utc)
                await session.commit()

            raise

        finally:
            # Cleanup chart files
            for chart_file in chart_files:
                ChartGenerator.cleanup_chart(chart_file)

    @classmethod
    async def _fetch_data(
        cls,
        session: AsyncSession,
        params: Optional[dict[str, Any]],
        template_name: str,
    ) -> dict[str, Any]:
        """Fetch data based on params configuration."""
        if not params:
            # Use sample data
            return DataFetcher.get_sample_data(template_name)

        data_source = params.get("data_source")
        data_config = params.get("data_config", {})

        if data_source == "sql":
            query = data_config.get("query")
            query_params = data_config.get("params", {})
            rows = await DataFetcher.fetch_from_sql(session, query, query_params)
            return {"rows": rows, **params.get("context", {})}

        elif data_source == "api":
            url = data_config.get("url")
            headers = data_config.get("headers")
            api_data = await DataFetcher.fetch_from_api(url, headers=headers)
            return {"api_data": api_data, **params.get("context", {})}

        elif data_source == "csv":
            file_path = data_config.get("file_path")
            content = data_config.get("content")
            rows = DataFetcher.fetch_from_csv(file_path=file_path, content=content)
            return {"rows": rows, **params.get("context", {})}

        else:
            # Use sample data as fallback
            sample = DataFetcher.get_sample_data(template_name)
            if params.get("context"):
                sample.update(params["context"])
            return sample

    @classmethod
    def _extract_chart_data(cls, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract chart configurations from data."""
        charts = []

        # Look for chart data patterns in the data
        if "revenue_data" in data:
            charts.append(
                {
                    "type": "bar",
                    "data": data["revenue_data"],
                    "title": "Revenue by Period",
                    "ylabel": "Revenue ($)",
                    "key": "revenue_chart",
                }
            )

        if "expense_breakdown" in data:
            charts.append(
                {
                    "type": "pie",
                    "data": data["expense_breakdown"],
                    "title": "Expense Breakdown",
                    "key": "expense_chart",
                }
            )

        if "sales_by_region" in data:
            charts.append(
                {
                    "type": "bar",
                    "data": data["sales_by_region"],
                    "title": "Sales by Region",
                    "ylabel": "Sales ($)",
                    "key": "region_chart",
                }
            )

        if "sales_trend" in data:
            charts.append(
                {
                    "type": "line",
                    "data": data["sales_trend"],
                    "title": "Sales Trend",
                    "ylabel": "Sales ($)",
                    "key": "trend_chart",
                }
            )

        # Look for explicit chart configs
        if "charts" in data:
            for chart_config in data["charts"]:
                charts.append(chart_config)

        return charts

    @classmethod
    def _prepare_context(
        cls,
        data: dict[str, Any],
        charts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Prepare the template context with data and charts."""
        context = data.copy()

        # Add charts by key
        context["charts"] = {}
        for chart in charts:
            key = chart.get("key", f"chart_{len(context['charts'])}")
            context["charts"][key] = chart.get("base64", "")

        # Add metadata
        context["generated_at"] = datetime.now(timezone.utc).isoformat()
        context["report_date"] = data.get(
            "report_date", datetime.now().strftime("%Y-%m-%d")
        )

        return context

    @classmethod
    async def regenerate_report(
        cls,
        session: AsyncSession,
        report_id: uuid.UUID,
    ) -> None:
        """Regenerate an existing report."""
        report = await session.get(Report, report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")

        # Delete old file if exists
        if report.file_path:
            StorageService.delete_pdf(report.file_path)

        # Reset status
        report.status = ReportStatus.PENDING
        report.file_path = None
        report.file_size = None
        report.error_message = None
        report.started_at = None
        report.completed_at = None
        await session.commit()

        # Generate new report
        await cls.generate_report(session, report_id)
