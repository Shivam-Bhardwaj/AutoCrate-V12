from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime
import json
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_logs.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

router = APIRouter()

class LogEntry(BaseModel):
    id: str
    timestamp: datetime
    level: int
    message: str
    category: str
    data: Optional[Dict[str, Any]] = None
    userId: Optional[str] = None
    sessionId: str
    userAgent: Optional[str] = None
    url: Optional[str] = None
    stack: Optional[str] = None

class LogBatch(BaseModel):
    logs: list[LogEntry]

@router.post("/logs")
async def receive_log(log_entry: LogEntry, request: Request):
    """
    Receive a single log entry from the web application
    """
    try:
        # Add server-side metadata
        client_ip = request.client.host if request.client else "unknown"
        
        # Create log record
        log_record = {
            "timestamp": log_entry.timestamp.isoformat(),
            "level": log_entry.level,
            "message": log_entry.message,
            "category": log_entry.category,
            "data": log_entry.data,
            "sessionId": log_entry.sessionId,
            "userAgent": log_entry.userAgent,
            "url": log_entry.url,
            "stack": log_entry.stack,
            "clientIP": client_ip,
            "serverTimestamp": datetime.now().isoformat()
        }
        
        # Log to file
        log_file_path = f"logs/web_logs_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily log file
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_record) + '\n')
        
        # Log to Python logger based on level
        if log_entry.level >= 4:  # CRITICAL
            logger.critical(f"[{log_entry.category}] {log_entry.message}", extra={"data": log_entry.data})
        elif log_entry.level >= 3:  # ERROR
            logger.error(f"[{log_entry.category}] {log_entry.message}", extra={"data": log_entry.data})
        elif log_entry.level >= 2:  # WARN
            logger.warning(f"[{log_entry.category}] {log_entry.message}", extra={"data": log_entry.data})
        elif log_entry.level >= 1:  # INFO
            logger.info(f"[{log_entry.category}] {log_entry.message}", extra={"data": log_entry.data})
        else:  # DEBUG
            logger.debug(f"[{log_entry.category}] {log_entry.message}", extra={"data": log_entry.data})
        
        return {"status": "success", "message": "Log received"}
        
    except Exception as e:
        logger.error(f"Failed to process log entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process log entry")

@router.post("/logs/batch")
async def receive_log_batch(log_batch: LogBatch, request: Request):
    """
    Receive multiple log entries in a batch
    """
    try:
        client_ip = request.client.host if request.client else "unknown"
        processed_count = 0
        
        log_file_path = f"logs/web_logs_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(log_file_path, 'a', encoding='utf-8') as f:
            for log_entry in log_batch.logs:
                log_record = {
                    "timestamp": log_entry.timestamp.isoformat(),
                    "level": log_entry.level,
                    "message": log_entry.message,
                    "category": log_entry.category,
                    "data": log_entry.data,
                    "sessionId": log_entry.sessionId,
                    "userAgent": log_entry.userAgent,
                    "url": log_entry.url,
                    "stack": log_entry.stack,
                    "clientIP": client_ip,
                    "serverTimestamp": datetime.now().isoformat()
                }
                
                f.write(json.dumps(log_record) + '\n')
                processed_count += 1
        
        logger.info(f"Processed batch of {processed_count} log entries")
        return {"status": "success", "message": f"Processed {processed_count} log entries"}
        
    except Exception as e:
        logger.error(f"Failed to process log batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process log batch")

@router.get("/logs/health")
async def logging_health():
    """
    Health check for logging system
    """
    try:
        # Check if logs directory exists and is writable
        logs_dir = Path("logs")
        if not logs_dir.exists():
            logs_dir.mkdir(exist_ok=True)
        
        # Test write access
        test_file = logs_dir / "test.tmp"
        test_file.write_text("test")
        test_file.unlink()
        
        return {
            "status": "healthy",
            "logs_directory": str(logs_dir.absolute()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logging health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logging system unhealthy")

@router.get("/logs/stats")
async def get_log_stats():
    """
    Get statistics about logged data
    """
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"total_files": 0, "total_size": 0}
        
        log_files = list(logs_dir.glob("web_logs_*.json"))
        total_size = sum(f.stat().st_size for f in log_files)
        total_lines = 0
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    total_lines += sum(1 for _ in f)
            except:
                continue
        
        return {
            "total_files": len(log_files),
            "total_size_bytes": total_size,
            "total_log_entries": total_lines,
            "files": [f.name for f in log_files]
        }
        
    except Exception as e:
        logger.error(f"Failed to get log stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get log statistics")
