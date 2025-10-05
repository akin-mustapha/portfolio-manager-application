"""
Log retention and cleanup policies.

This module handles log file rotation, cleanup, and retention policies
to manage disk space and maintain system performance.
"""

import os
import glob
import gzip
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

from app.core.logging import get_context_logger
from app.core.config import settings


logger = get_context_logger(__name__)


class LogRetentionManager:
    """
    Manages log file retention, compression, and cleanup.
    """
    
    def __init__(
        self,
        log_directory: str = "logs",
        retention_days: int = 30,
        compression_days: int = 7,
        max_log_size_mb: int = 100
    ):
        self.log_directory = Path(log_directory)
        self.retention_days = retention_days
        self.compression_days = compression_days
        self.max_log_size_mb = max_log_size_mb
        
        # Ensure log directory exists
        self.log_directory.mkdir(exist_ok=True)
        
        logger.info(
            "LogRetentionManager initialized",
            extra={
                'log_directory': str(self.log_directory),
                'retention_days': retention_days,
                'compression_days': compression_days,
                'max_log_size_mb': max_log_size_mb
            }
        )
    
    def cleanup_old_logs(self) -> Dict[str, Any]:
        """
        Clean up old log files based on retention policy.
        
        Returns:
            Summary of cleanup operations
        """
        logger.info("Starting log cleanup process")
        
        cleanup_summary = {
            'files_deleted': 0,
            'files_compressed': 0,
            'space_freed_mb': 0,
            'errors': []
        }
        
        try:
            # Get all log files
            log_files = list(self.log_directory.glob("*.log*"))
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            compression_date = datetime.now() - timedelta(days=self.compression_days)
            
            for log_file in log_files:
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    file_size_mb = log_file.stat().st_size / (1024 * 1024)
                    
                    # Delete files older than retention period
                    if file_mtime < cutoff_date:
                        logger.debug(
                            f"Deleting old log file: {log_file.name}",
                            extra={
                                'file_age_days': (datetime.now() - file_mtime).days,
                                'file_size_mb': round(file_size_mb, 2)
                            }
                        )
                        
                        cleanup_summary['space_freed_mb'] += file_size_mb
                        log_file.unlink()
                        cleanup_summary['files_deleted'] += 1
                    
                    # Compress files older than compression period (but within retention)
                    elif (file_mtime < compression_date and 
                          not log_file.name.endswith('.gz') and
                          file_size_mb > 1):  # Only compress files larger than 1MB
                        
                        compressed_file = self._compress_log_file(log_file)
                        if compressed_file:
                            cleanup_summary['files_compressed'] += 1
                            logger.debug(
                                f"Compressed log file: {log_file.name} -> {compressed_file.name}",
                                extra={
                                    'original_size_mb': round(file_size_mb, 2),
                                    'compressed_size_mb': round(compressed_file.stat().st_size / (1024 * 1024), 2)
                                }
                            )
                
                except Exception as e:
                    error_msg = f"Error processing log file {log_file.name}: {str(e)}"
                    cleanup_summary['errors'].append(error_msg)
                    logger.error(
                        "Log file processing error",
                        extra={
                            'file_name': log_file.name,
                            'error_type': type(e).__name__,
                            'error_message': str(e)
                        }
                    )
            
            logger.info(
                "Log cleanup completed",
                extra={
                    'files_deleted': cleanup_summary['files_deleted'],
                    'files_compressed': cleanup_summary['files_compressed'],
                    'space_freed_mb': round(cleanup_summary['space_freed_mb'], 2),
                    'errors_count': len(cleanup_summary['errors'])
                }
            )
            
        except Exception as e:
            error_msg = f"Log cleanup process failed: {str(e)}"
            cleanup_summary['errors'].append(error_msg)
            logger.error(
                "Log cleanup process failed",
                extra={'error_type': type(e).__name__, 'error_message': str(e)},
                exc_info=True
            )
        
        return cleanup_summary
    
    def _compress_log_file(self, log_file: Path) -> Path:
        """
        Compress a log file using gzip.
        
        Args:
            log_file: Path to log file to compress
            
        Returns:
            Path to compressed file, or None if compression failed
        """
        try:
            compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
            
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file after successful compression
            log_file.unlink()
            
            return compressed_file
            
        except Exception as e:
            logger.error(
                f"Failed to compress log file {log_file.name}",
                extra={'error_type': type(e).__name__, 'error_message': str(e)}
            )
            return None
    
    def get_log_directory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the log directory.
        
        Returns:
            Dictionary with log directory statistics
        """
        try:
            log_files = list(self.log_directory.glob("*"))
            
            total_size = 0
            file_types = {'log': 0, 'gz': 0, 'other': 0}
            oldest_file = None
            newest_file = None
            
            for log_file in log_files:
                if log_file.is_file():
                    file_size = log_file.stat().st_size
                    total_size += file_size
                    
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if oldest_file is None or file_mtime < oldest_file:
                        oldest_file = file_mtime
                    
                    if newest_file is None or file_mtime > newest_file:
                        newest_file = file_mtime
                    
                    # Categorize file types
                    if log_file.suffix == '.log':
                        file_types['log'] += 1
                    elif log_file.suffix == '.gz':
                        file_types['gz'] += 1
                    else:
                        file_types['other'] += 1
            
            return {
                'total_files': len(log_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_types': file_types,
                'oldest_file_age_days': (datetime.now() - oldest_file).days if oldest_file else None,
                'newest_file_age_days': (datetime.now() - newest_file).days if newest_file else None,
                'directory_path': str(self.log_directory)
            }
            
        except Exception as e:
            logger.error(
                "Failed to get log directory stats",
                extra={'error_type': type(e).__name__, 'error_message': str(e)},
                exc_info=True
            )
            return {'error': str(e)}
    
    def archive_logs_by_date(self, archive_date: datetime) -> Dict[str, Any]:
        """
        Archive logs from a specific date to a separate directory.
        
        Args:
            archive_date: Date to archive logs for
            
        Returns:
            Summary of archival operations
        """
        archive_dir = self.log_directory / "archive" / archive_date.strftime("%Y-%m")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_summary = {
            'files_archived': 0,
            'total_size_mb': 0,
            'archive_directory': str(archive_dir),
            'errors': []
        }
        
        try:
            # Find log files from the specified date
            date_pattern = archive_date.strftime("%Y%m%d")
            log_files = list(self.log_directory.glob(f"*{date_pattern}*"))
            
            for log_file in log_files:
                try:
                    if log_file.is_file():
                        file_size_mb = log_file.stat().st_size / (1024 * 1024)
                        
                        # Move file to archive directory
                        archive_file = archive_dir / log_file.name
                        shutil.move(str(log_file), str(archive_file))
                        
                        archive_summary['files_archived'] += 1
                        archive_summary['total_size_mb'] += file_size_mb
                        
                        logger.debug(
                            f"Archived log file: {log_file.name}",
                            extra={
                                'archive_directory': str(archive_dir),
                                'file_size_mb': round(file_size_mb, 2)
                            }
                        )
                
                except Exception as e:
                    error_msg = f"Error archiving file {log_file.name}: {str(e)}"
                    archive_summary['errors'].append(error_msg)
                    logger.error(
                        "Log file archival error",
                        extra={
                            'file_name': log_file.name,
                            'error_type': type(e).__name__,
                            'error_message': str(e)
                        }
                    )
            
            logger.info(
                f"Log archival completed for {archive_date.strftime('%Y-%m-%d')}",
                extra={
                    'files_archived': archive_summary['files_archived'],
                    'total_size_mb': round(archive_summary['total_size_mb'], 2),
                    'archive_directory': str(archive_dir)
                }
            )
            
        except Exception as e:
            error_msg = f"Log archival process failed: {str(e)}"
            archive_summary['errors'].append(error_msg)
            logger.error(
                "Log archival process failed",
                extra={'error_type': type(e).__name__, 'error_message': str(e)},
                exc_info=True
            )
        
        return archive_summary


def setup_log_retention_policy() -> LogRetentionManager:
    """
    Set up log retention policy based on configuration.
    
    Returns:
        Configured LogRetentionManager instance
    """
    retention_manager = LogRetentionManager(
        log_directory=settings.LOG_DIR,
        retention_days=getattr(settings, 'LOG_RETENTION_DAYS', 30),
        compression_days=getattr(settings, 'LOG_COMPRESSION_DAYS', 7),
        max_log_size_mb=getattr(settings, 'LOG_MAX_SIZE_MB', 100)
    )
    
    logger.info("Log retention policy configured")
    return retention_manager