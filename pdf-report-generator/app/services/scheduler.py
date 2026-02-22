"""Scheduling service using APScheduler."""

from datetime import datetime, timezone
from typing import Callable, Any, Optional
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from croniter import croniter
from loguru import logger


class SchedulerService:
    """
    Service for managing scheduled jobs using APScheduler.
    """
    
    _scheduler: Optional[AsyncIOScheduler] = None
    _initialized: bool = False
    
    @classmethod
    def get_scheduler(cls) -> AsyncIOScheduler:
        """Get or create the scheduler instance."""
        if cls._scheduler is None:
            cls._scheduler = AsyncIOScheduler(
                jobstores={
                    'default': MemoryJobStore()
                },
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1,
                    'misfire_grace_time': 60 * 60,  # 1 hour grace time
                }
            )
        return cls._scheduler
    
    @classmethod
    def start(cls) -> None:
        """Start the scheduler."""
        scheduler = cls.get_scheduler()
        if not scheduler.running:
            scheduler.start()
            cls._initialized = True
            logger.info("Scheduler started")
    
    @classmethod
    def shutdown(cls) -> None:
        """Shutdown the scheduler."""
        if cls._scheduler is not None and cls._scheduler.running:
            cls._scheduler.shutdown(wait=False)
            cls._initialized = False
            logger.info("Scheduler stopped")
    
    @classmethod
    def add_job(
        cls,
        job_id: str,
        func: Callable,
        cron_expression: str,
        args: Optional[tuple] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ) -> datetime:
        """
        Add a scheduled job.
        
        Args:
            job_id: Unique identifier for the job
            func: Function to execute
            cron_expression: Cron expression for scheduling
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            
        Returns:
            Next run time
        """
        scheduler = cls.get_scheduler()
        
        # Parse cron expression into trigger
        cron_parts = cron_expression.split()
        if len(cron_parts) == 5:
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4],
            )
        else:
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        # Add job
        job = scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            args=args or (),
            kwargs=kwargs or {},
            replace_existing=True,
        )
        
        next_run = job.next_run_time
        logger.info(f"Added job {job_id}, next run: {next_run}")
        
        return next_run
    
    @classmethod
    def remove_job(cls, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was removed, False if not found
        """
        scheduler = cls.get_scheduler()
        try:
            scheduler.remove_job(job_id)
            logger.info(f"Removed job {job_id}")
            return True
        except Exception:
            logger.warning(f"Job not found: {job_id}")
            return False
    
    @classmethod
    def pause_job(cls, job_id: str) -> bool:
        """Pause a scheduled job."""
        scheduler = cls.get_scheduler()
        try:
            scheduler.pause_job(job_id)
            logger.info(f"Paused job {job_id}")
            return True
        except Exception:
            return False
    
    @classmethod
    def resume_job(cls, job_id: str) -> bool:
        """Resume a paused job."""
        scheduler = cls.get_scheduler()
        try:
            scheduler.resume_job(job_id)
            logger.info(f"Resumed job {job_id}")
            return True
        except Exception:
            return False
    
    @classmethod
    def get_job(cls, job_id: str) -> Optional[dict]:
        """Get job information."""
        scheduler = cls.get_scheduler()
        job = scheduler.get_job(job_id)
        if job:
            return {
                "id": job.id,
                "next_run_time": job.next_run_time,
                "pending": job.pending,
            }
        return None
    
    @classmethod
    def get_next_run_time(cls, cron_expression: str) -> datetime:
        """
        Calculate the next run time for a cron expression.
        
        Args:
            cron_expression: Cron expression
            
        Returns:
            Next run time as datetime
        """
        cron = croniter(cron_expression, datetime.now(timezone.utc))
        return cron.get_next(datetime)
    
    @classmethod
    def is_valid_cron(cls, cron_expression: str) -> bool:
        """Check if a cron expression is valid."""
        try:
            croniter(cron_expression)
            return True
        except (KeyError, ValueError):
            return False
