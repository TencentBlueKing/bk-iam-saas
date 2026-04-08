# -*- coding: utf-8 -*-
"""
Crontab utility functions for Celery 5.1 compatibility.

This module includes code from Celery (https://github.com/celery/celery)
Copyright (c) 2017-2026 Asif Saif Uddin, core team & contributors.
Licensed under the BSD 3-Clause License.

Original source: https://github.com/celery/celery
"""

from celery.schedules import crontab


def crontab_from_string(crontab_str: str) -> crontab:
    """
    Create a Crontab from a cron expression string.
    
    This method is backported from Celery 5.6+ for compatibility with Celery 5.1.
    
    Original implementation:
    https://github.com/celery/celery/blob/main/celery/schedules.py
    
    Args:
        crontab_str: Linux crontab format string, e.g., '* * * * *'
                     Format: minute hour day_of_month month_of_year day_of_week
    
    Returns:
        crontab: Celery crontab object
    
    Example:
        >>> schedule = crontab_from_string('*/5 * * * *')  # Every 5 minutes
        >>> schedule = crontab_from_string('0 2 * * *')    # Daily at 2 AM
    
    .. code-block:: text

        ┌───────────── minute (0–59)
        │ ┌───────────── hour (0–23)
        │ │ ┌───────────── day of the month (1–31)
        │ │ │ ┌───────────── month (1–12)
        │ │ │ │ ┌───────────── day of the week (0–6) (Sunday to Saturday)
        * * * * *
    """
    minute, hour, day_of_month, month_of_year, day_of_week = crontab_str.split(" ")
    return crontab(minute, hour, day_of_week, day_of_month, month_of_year)