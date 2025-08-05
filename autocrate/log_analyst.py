"""
AutoCrate Log Analysis Agent
Intelligent system that analyzes previous runs to provide insights and recommendations.
"""

import json
import os
import re
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import glob

@dataclass
class SessionInfo:
    """Information about a logging session."""
    session_id: str
    timestamp: datetime.datetime
    duration_seconds: Optional[float] = None
    success_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    performance_data: Dict[str, Any] = None
    last_operation: Optional[str] = None
    errors: List[Dict] = None
    
    def __post_init__(self):
        if self.performance_data is None:
            self.performance_data = {}
        if self.errors is None:
            self.errors = []

@dataclass
class LogInsight:
    """An insight or recommendation from log analysis."""
    type: str  # 'success', 'warning', 'error', 'recommendation', 'trend'
    title: str
    message: str
    details: Dict[str, Any] = None
    confidence: float = 1.0  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class LogAnalysisAgent:
    """
    Intelligent agent that analyzes AutoCrate logs to provide insights about previous runs.
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.sessions: List[SessionInfo] = []
        self.insights: List[LogInsight] = []
        
        # Pattern matchers for log analysis
        self.patterns = {
            'session_start': re.compile(r'=== AutoCrate Debug Session Started ==='),
            'session_id': re.compile(r'Session ID: (\d{8}_\d{6}_\d+)'),
            'import_success': re.compile(r'(Relative|Direct) imports? successful'),
            'import_failure': re.compile(r'import failed: (.+)'),
            'expression_start': re.compile(r'Starting crate expression generation'),
            'expression_success': re.compile(r'Expression generation completed successfully'),
            'expression_failure': re.compile(r'Expression generation failed'),
            'performance': re.compile(r'PERFORMANCE: (.+) completed in ([\d.]+)ms'),
            'error': re.compile(r'ERROR.+?Error Info: (.+)'),
            'warning': re.compile(r'WARNING.+?(.+)'),
        }
    
    def analyze_recent_runs(self, max_sessions: int = 10) -> Dict[str, Any]:
        """
        Analyze the most recent runs and return comprehensive insights.
        """
        try:
            print("🔍 AutoCrate Log Analysis Agent Starting...")
        except UnicodeEncodeError:
            print("AutoCrate Log Analysis Agent Starting...")
        
        # Load and parse sessions
        self._load_sessions(max_sessions)
        
        # Generate insights
        self._analyze_sessions()
        
        # Create summary report
        report = self._create_analysis_report()
        
        try:
            print(f"✅ Analysis complete. Found {len(self.sessions)} sessions with {len(self.insights)} insights.")
        except UnicodeEncodeError:
            print(f"Analysis complete. Found {len(self.sessions)} sessions with {len(self.insights)} insights.")
        return report
    
    def get_last_run_summary(self) -> Dict[str, Any]:
        """Get a quick summary of what happened in the last run."""
        if not self.sessions:
            self._load_sessions(1)
        
        if not self.sessions:
            return {
                'status': 'no_sessions',
                'message': 'No previous runs found',
                'details': {}
            }
        
        last_session = self.sessions[0]  # Most recent
        
        # Analyze just the last session
        insights = self._analyze_single_session(last_session)
        
        return {
            'status': 'success' if last_session.error_count == 0 else 'errors',
            'session_id': last_session.session_id,
            'timestamp': last_session.timestamp.isoformat(),
            'duration': last_session.duration_seconds,
            'operations': len(last_session.performance_data),
            'errors': last_session.error_count,
            'warnings': last_session.warning_count,
            'last_operation': last_session.last_operation,
            'insights': [asdict(insight) for insight in insights],
            'quick_summary': self._generate_quick_summary(last_session)
        }
    
    def _load_sessions(self, max_sessions: int):
        """Load and parse recent sessions from log files."""
        if not self.log_dir.exists():
            return
        
        # Find all debug log files
        debug_files = sorted(
            self.log_dir.glob("debug_*.log"), 
            key=lambda f: f.stat().st_mtime, 
            reverse=True
        )[:max_sessions]
        
        try:
            print(f"📁 Found {len(debug_files)} recent log files")
        except UnicodeEncodeError:
            print(f"Found {len(debug_files)} recent log files")
        
        for log_file in debug_files:
            session = self._parse_debug_log(log_file)
            if session:
                # Load additional data
                self._load_performance_data(session)
                self._load_error_details(session)
                self.sessions.append(session)
    
    def _parse_debug_log(self, log_file: Path) -> Optional[SessionInfo]:
        """Parse a debug log file to extract session information."""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic session info
            session_match = self.patterns['session_id'].search(content)
            if not session_match:
                return None
            
            session_id = session_match.group(1)
            timestamp = self._parse_timestamp_from_session_id(session_id)
            
            session = SessionInfo(
                session_id=session_id,
                timestamp=timestamp
            )
            
            # Count different log levels
            lines = content.split('\n')
            for line in lines:
                if '| ERROR |' in line:
                    session.error_count += 1
                elif '| WARNING |' in line:
                    session.warning_count += 1
                elif 'completed successfully' in line:
                    session.success_count += 1
            
            # Find last operation
            perf_matches = self.patterns['performance'].findall(content)
            if perf_matches:
                session.last_operation = perf_matches[-1][0]  # Last performance entry
            
            return session
            
        except Exception as e:
            try:
                print(f"⚠️ Error parsing {log_file}: {e}")
            except UnicodeEncodeError:
                print(f"Error parsing {log_file}: {e}")
            return None
    
    def _load_performance_data(self, session: SessionInfo):
        """Load performance data from JSON performance log."""
        perf_file = self.log_dir / f"performance_{session.session_id.split('_')[0]}_{session.session_id.split('_')[1]}.json"
        
        if not perf_file.exists():
            return
        
        try:
            performance_entries = []
            with open(perf_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        if entry.get('session_id') == session.session_id:
                            performance_entries.append(entry)
            
            # Aggregate performance data
            operations = defaultdict(list)
            for entry in performance_entries:
                op_name = entry.get('operation', 'unknown')
                duration = entry.get('duration_ms', 0)
                operations[op_name].append(duration)
            
            # Calculate statistics
            session.performance_data = {}
            total_time = 0
            for op_name, durations in operations.items():
                stats = {
                    'count': len(durations),
                    'total_ms': sum(durations),
                    'avg_ms': sum(durations) / len(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations)
                }
                session.performance_data[op_name] = stats
                total_time += stats['total_ms']
            
            session.duration_seconds = total_time / 1000.0
            
        except Exception as e:
            try:
                print(f"⚠️ Error loading performance data: {e}")
            except UnicodeEncodeError:
                print(f"Error loading performance data: {e}")
    
    def _load_error_details(self, session: SessionInfo):
        """Load detailed error information."""
        error_detail_file = self.log_dir / f"error_detail_{session.session_id.split('_')[0]}_{session.session_id.split('_')[1]}.json"
        
        if not error_detail_file.exists():
            return
        
        try:
            with open(error_detail_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # File might contain multiple JSON objects
                    for line in content.split('\n'):
                        if line.strip():
                            error_data = json.loads(line)
                            if error_data.get('session_id') == session.session_id:
                                session.errors.append(error_data)
        except Exception as e:
            try:
                print(f"⚠️ Error loading error details: {e}")
            except UnicodeEncodeError:
                print(f"Error loading error details: {e}")
    
    def _analyze_sessions(self):
        """Analyze all loaded sessions to generate insights."""
        if not self.sessions:
            return
        
        # Analyze each session individually
        for session in self.sessions:
            session_insights = self._analyze_single_session(session)
            self.insights.extend(session_insights)
        
        # Add trend analysis
        trend_insights = self._analyze_trends()
        self.insights.extend(trend_insights)
    
    def _analyze_single_session(self, session: SessionInfo) -> List[LogInsight]:
        """Analyze a single session and return insights."""
        insights = []
        
        # Success/failure analysis
        if session.error_count == 0:
            insights.append(LogInsight(
                type='success',
                title='Clean Execution',
                message=f'Session completed without errors ({session.success_count} successful operations)',
                details={'session_id': session.session_id}
            ))
        else:
            insights.append(LogInsight(
                type='error',
                title='Errors Detected',
                message=f'Session had {session.error_count} errors and {session.warning_count} warnings',
                details={'session_id': session.session_id, 'errors': session.errors}
            ))
        
        # Performance analysis
        if session.performance_data:
            total_operations = sum(data['count'] for data in session.performance_data.values())
            avg_duration = session.duration_seconds / total_operations if total_operations > 0 else 0
            
            if avg_duration > 5.0:  # Slow operations
                insights.append(LogInsight(
                    type='warning',
                    title='Performance Warning',
                    message=f'Operations averaged {avg_duration:.2f}s, which may be slow',
                    details={'avg_duration': avg_duration, 'total_operations': total_operations}
                ))
            elif avg_duration < 0.1:  # Fast operations
                insights.append(LogInsight(
                    type='success',
                    title='Good Performance',
                    message=f'Operations completed quickly (avg: {avg_duration*1000:.1f}ms)',
                    details={'avg_duration': avg_duration}
                ))
        
        # Import analysis
        if session.last_operation and 'import' in session.last_operation.lower():
            if session.error_count == 0:
                insights.append(LogInsight(
                    type='success',
                    title='Import Resolution',
                    message='Module imports completed successfully',
                    details={'method': 'direct_imports'}
                ))
        
        # Operation-specific analysis
        if session.last_operation == 'generate_crate_expressions':
            if session.error_count == 0:
                insights.append(LogInsight(
                    type='success',
                    title='Expression Generation Success',
                    message='Crate expression generation completed successfully',
                    details=session.performance_data.get('generate_crate_expressions', {})
                ))
        
        return insights
    
    def _analyze_trends(self) -> List[LogInsight]:
        """Analyze trends across multiple sessions."""
        insights = []
        
        if len(self.sessions) < 2:
            return insights
        
        # Error trend analysis
        recent_errors = [s.error_count for s in self.sessions[:5]]  # Last 5 sessions
        if sum(recent_errors) == 0:
            insights.append(LogInsight(
                type='trend',
                title='Stable Performance',
                message='No errors in recent runs - system is stable',
                details={'sessions_analyzed': len(recent_errors)}
            ))
        elif recent_errors[0] > recent_errors[-1]:
            insights.append(LogInsight(
                type='trend',
                title='Improving Reliability',
                message='Error count decreasing over recent runs',
                details={'trend': 'improving', 'recent_errors': recent_errors}
            ))
        
        # Performance trends
        recent_durations = [s.duration_seconds for s in self.sessions[:5] if s.duration_seconds]
        if len(recent_durations) >= 3:
            avg_recent = sum(recent_durations[:3]) / 3
            avg_older = sum(recent_durations[3:]) / len(recent_durations[3:]) if len(recent_durations) > 3 else avg_recent
            
            if avg_recent < avg_older * 0.8:  # 20% improvement
                insights.append(LogInsight(
                    type='trend',
                    title='Performance Improvement',
                    message=f'Recent runs are {((avg_older - avg_recent) / avg_older * 100):.1f}% faster',
                    details={'avg_recent': avg_recent, 'avg_older': avg_older}
                ))
        
        return insights
    
    def _create_analysis_report(self) -> Dict[str, Any]:
        """Create comprehensive analysis report."""
        if not self.sessions:
            return {'status': 'no_data', 'message': 'No sessions found to analyze'}
        
        # Categorize insights
        success_insights = [i for i in self.insights if i.type == 'success']
        error_insights = [i for i in self.insights if i.type == 'error']
        warning_insights = [i for i in self.insights if i.type == 'warning']
        trend_insights = [i for i in self.insights if i.type == 'trend']
        
        # Calculate overall statistics
        total_sessions = len(self.sessions)
        error_sessions = len([s for s in self.sessions if s.error_count > 0])
        avg_duration = sum(s.duration_seconds for s in self.sessions if s.duration_seconds) / len([s for s in self.sessions if s.duration_seconds])
        
        # Most common operations
        all_operations = []
        for session in self.sessions:
            if session.performance_data:
                all_operations.extend(session.performance_data.keys())
        common_operations = Counter(all_operations).most_common(5)
        
        return {
            'analysis_timestamp': datetime.datetime.now().isoformat(),
            'sessions_analyzed': total_sessions,
            'summary': {
                'status': 'healthy' if error_sessions / total_sessions < 0.2 else 'issues_detected',
                'error_rate': f"{(error_sessions / total_sessions * 100):.1f}%",
                'avg_duration_seconds': round(avg_duration, 3) if avg_duration else None,
                'most_recent_session': self.sessions[0].session_id if self.sessions else None
            },
            'insights': {
                'success': [asdict(i) for i in success_insights],
                'errors': [asdict(i) for i in error_insights],
                'warnings': [asdict(i) for i in warning_insights],
                'trends': [asdict(i) for i in trend_insights]
            },
            'statistics': {
                'common_operations': common_operations,
                'session_timeline': [
                    {
                        'session_id': s.session_id,
                        'timestamp': s.timestamp.isoformat(),
                        'errors': s.error_count,
                        'duration': s.duration_seconds
                    } for s in self.sessions
                ]
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Check for frequent errors
        error_sessions = [s for s in self.sessions if s.error_count > 0]
        if len(error_sessions) > len(self.sessions) * 0.3:  # More than 30% error rate
            recommendations.append({
                'priority': 'high',
                'title': 'High Error Rate Detected',
                'action': 'Review recent error logs and fix recurring issues',
                'details': {'error_rate': f"{len(error_sessions) / len(self.sessions) * 100:.1f}%"}
            })
        
        # Check for performance issues
        slow_sessions = [s for s in self.sessions if s.duration_seconds and s.duration_seconds > 10]
        if slow_sessions:
            recommendations.append({
                'priority': 'medium',
                'title': 'Performance Optimization Needed',
                'action': 'Consider optimizing slow operations or checking system resources',
                'details': {'slow_sessions': len(slow_sessions)}
            })
        
        # Check for import issues
        import_warnings = sum(1 for i in self.insights if 'import' in i.message.lower() and i.type == 'warning')
        if import_warnings > 0:
            recommendations.append({
                'priority': 'low',
                'title': 'Import Path Optimization',
                'action': 'Consider restructuring imports to avoid fallback to direct imports',
                'details': {'import_warnings': import_warnings}
            })
        
        return recommendations
    
    def _generate_quick_summary(self, session: SessionInfo) -> str:
        """Generate a human-readable quick summary."""
        if session.error_count > 0:
            return f"❌ Last run had {session.error_count} errors. Check error logs for details."
        elif session.warning_count > 0:
            return f"⚠️ Last run completed with {session.warning_count} warnings. System functional but check logs."
        elif session.last_operation:
            duration_text = f" in {session.duration_seconds:.2f}s" if session.duration_seconds else ""
            return f"✅ Last run successful. Completed {session.last_operation}{duration_text}."
        else:
            return "✅ Last run completed successfully."
    
    def _parse_timestamp_from_session_id(self, session_id: str) -> datetime.datetime:
        """Parse timestamp from session ID format: YYYYMMDD_HHMMSS_PID"""
        try:
            date_part, time_part = session_id.split('_')[:2]
            timestamp_str = f"{date_part}_{time_part}"
            return datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except:
            return datetime.datetime.now()

# Convenience functions for easy usage
def analyze_last_run() -> Dict[str, Any]:
    """Quick function to analyze the last run."""
    agent = LogAnalysisAgent()
    return agent.get_last_run_summary()

def analyze_recent_runs(max_sessions: int = 10) -> Dict[str, Any]:
    """Quick function to analyze recent runs."""
    agent = LogAnalysisAgent()
    return agent.analyze_recent_runs(max_sessions)

def print_last_run_summary():
    """Print a formatted summary of the last run."""
    summary = analyze_last_run()
    
    print("\n" + "="*60)
    print("🔍 AUTOCRATE - LAST RUN ANALYSIS")
    print("="*60)
    
    if summary['status'] == 'no_sessions':
        print("❌ No previous runs found")
        return
    
    print(f"📅 Session: {summary['session_id']}")
    print(f"⏰ Time: {summary['timestamp']}")
    print(f"📊 Quick Summary: {summary['quick_summary']}")
    
    if summary['errors'] > 0:
        print(f"❌ Errors: {summary['errors']}")
    if summary['warnings'] > 0:
        print(f"⚠️ Warnings: {summary['warnings']}")
    if summary['duration']:
        print(f"⏱️ Duration: {summary['duration']:.2f}s")
    
    # Show insights
    if summary['insights']:
        print("\n💡 Key Insights:")
        for insight in summary['insights'][:3]:  # Top 3 insights
            icon = {'success': '✅', 'error': '❌', 'warning': '⚠️', 'trend': '📈'}.get(insight['type'], '•')
            print(f"   {icon} {insight['title']}: {insight['message']}")
    
    print("="*60)

if __name__ == "__main__":
    # Run analysis when script is executed directly
    print_last_run_summary()
    print("\n🔍 Running full analysis...")
    full_analysis = analyze_recent_runs()
    
    if full_analysis.get('recommendations'):
        print("\n📋 Recommendations:")
        for rec in full_analysis['recommendations']:
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '•')
            print(f"   {priority_icon} {rec['title']}: {rec['action']}")