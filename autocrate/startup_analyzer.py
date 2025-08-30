"""
AutoCrate Startup Log Analyzer
Automatically analyzes logs when the application starts and provides insights.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from log_analyst import LogAnalysisAgent, analyze_last_run, print_last_run_summary
    from debug_logger import get_logger
except ImportError as e:
    print(f"Warning: Could not import log analysis modules: {e}")
    LogAnalysisAgent = None

class StartupAnalyzer:
    """
    Analyzes logs at startup and provides insights about the previous run.
    """
    
    def __init__(self, enable_console_output: bool = True):
        self.enable_console_output = enable_console_output
        self.logger = None
        try:
            self.logger = get_logger("AutoCrate.Startup")
        except:
            pass
    
    def analyze_and_report(self) -> dict:
        """
        Analyze previous runs and return a report with recommendations.
        """
        if not LogAnalysisAgent:
            return {'status': 'analyzer_unavailable', 'message': 'Log analysis not available'}
        
        try:
            # Get last run summary
            last_run = analyze_last_run()
            
            if self.logger:
                self.logger.info("Startup log analysis completed", {
                    'last_run_status': last_run.get('status'),
                    'last_run_errors': last_run.get('errors', 0),
                    'last_run_warnings': last_run.get('warnings', 0)
                })
            
            # Print summary if enabled
            if self.enable_console_output:
                self._print_startup_summary(last_run)
            
            return last_run
            
        except Exception as e:
            error_msg = f"Error during startup analysis: {e}"
            if self.logger:
                self.logger.error("Startup analysis failed", e)
            elif self.enable_console_output:
                print(f"WARNING: {error_msg}")
            
            return {'status': 'analysis_error', 'message': error_msg}
    
    def _print_startup_summary(self, last_run: dict):
        """Print a concise startup summary."""
        if last_run['status'] == 'no_sessions':
            try:
                print("🆕 Welcome to AutoCrate! This appears to be your first run.")
            except UnicodeEncodeError:
                print("Welcome to AutoCrate! This appears to be your first run.")
            return
        
        print("\n" + "="*50)
        try:
            print("PREVIOUS RUN SUMMARY")
        except UnicodeEncodeError:
            print("PREVIOUS RUN SUMMARY")
        print("="*50)
        
        # Status indicator
        if last_run['status'] == 'success':
            try:
                print("[SUCCESS] Last run completed successfully")
            except UnicodeEncodeError:
                print("Last run completed successfully")
        else:
            try:
                print("[WARNING] Issues detected in last run")
            except UnicodeEncodeError:
                print("Issues detected in last run")
        
        # Quick stats
        try:
            print(f"Last run: {last_run['timestamp'][:19]}")  # Remove milliseconds
        except UnicodeEncodeError:
            print(f"Last run: {last_run['timestamp'][:19]}")  # Remove milliseconds
        if last_run.get('duration'):
            try:
                print(f"⏱️ Duration: {last_run['duration']:.2f}s")
            except UnicodeEncodeError:
                print(f"Duration: {last_run['duration']:.2f}s")
        if last_run.get('operations'):
            try:
                print(f"Operations: {last_run['operations']}")
            except UnicodeEncodeError:
                print(f"Operations: {last_run['operations']}")
        
        # Issues
        if last_run.get('errors', 0) > 0:
            try:
                print(f"[ERROR] Errors: {last_run['errors']}")
            except UnicodeEncodeError:
                print(f"Errors: {last_run['errors']}")
        if last_run.get('warnings', 0) > 0:
            try:
                print(f"[WARNING] Warnings: {last_run['warnings']}")
            except UnicodeEncodeError:
                print(f"Warnings: {last_run['warnings']}")
        
        # Quick insights
        insights = last_run.get('insights', [])
        if insights:
            critical_insights = [i for i in insights if i['type'] in ['error', 'warning']]
            if critical_insights:
                try:
                    print("\nKey Issues:")
                except UnicodeEncodeError:
                    print("\nKey Issues:")
                for insight in critical_insights[:2]:  # Top 2 critical insights
                    try:
                        icon = '[ERROR]' if insight['type'] == 'error' else '[WARNING]'
                        print(f"   {icon} {insight['title']}")
                    except UnicodeEncodeError:
                        icon = '[X]' if insight['type'] == 'error' else '[!]'
                        print(f"   {icon} {insight['title']}")
        
        print("="*50)
        
        # Show recovery suggestions if there were errors
        if last_run.get('errors', 0) > 0:
            try:
                print("Suggestions:")
            except UnicodeEncodeError:
                print("Suggestions:")
            print("   • Check logs/ directory for detailed error information")
            print("   • Run with AUTOCRATE_DEBUG=1 for more details")
            print("   • Use log_analyst.py for full analysis")
            print()
    
    def check_for_critical_issues(self) -> list:
        """
        Check for critical issues that need immediate attention.
        Returns list of critical issues found.
        """
        if not LogAnalysisAgent:
            return []
        
        try:
            agent = LogAnalysisAgent()
            last_run = agent.get_last_run_summary()
            
            critical_issues = []
            
            # Check for recent errors
            if last_run.get('errors', 0) > 0:
                critical_issues.append({
                    'type': 'errors',
                    'severity': 'high',
                    'message': f"Last run had {last_run['errors']} errors",
                    'action': 'Check error logs immediately'
                })
            
            # Check for performance issues
            if last_run.get('duration', 0) > 30:  # More than 30 seconds
                critical_issues.append({
                    'type': 'performance',
                    'severity': 'medium',
                    'message': f"Last run took {last_run['duration']:.1f}s (slow)",
                    'action': 'Consider performance optimization'
                })
            
            # Check insights for critical items
            insights = last_run.get('insights', [])
            error_insights = [i for i in insights if i['type'] == 'error']
            if error_insights:
                for insight in error_insights[:2]:  # Top 2 error insights
                    critical_issues.append({
                        'type': 'insight_error',
                        'severity': 'high',
                        'message': insight['title'],
                        'action': insight['message']
                    })
            
            return critical_issues
            
        except Exception as e:
            return [{
                'type': 'analysis_error',
                'severity': 'low',
                'message': f"Could not analyze logs: {e}",
                'action': 'Manual log review recommended'
            }]
    
    def get_startup_recommendations(self) -> list:
        """Get recommendations for the current startup."""
        recommendations = []
        
        # Check if debug mode should be enabled
        debug_mode = os.getenv('AUTOCRATE_DEBUG', '0') == '1'
        if not debug_mode:
            critical_issues = self.check_for_critical_issues()
            if any(issue['severity'] == 'high' for issue in critical_issues):
                recommendations.append({
                    'priority': 'high',
                    'title': 'Enable Debug Mode',
                    'action': 'Set AUTOCRATE_DEBUG=1 to get detailed logging for troubleshooting',
                    'command': 'set AUTOCRATE_DEBUG=1'
                })
        
        # Check log directory size
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.json"))
                total_size = sum(f.stat().st_size for f in log_files if f.exists())
                
                if total_size > 100 * 1024 * 1024:  # More than 100MB
                    recommendations.append({
                        'priority': 'low',
                        'title': 'Log Cleanup Needed',
                        'action': f'Log directory is {total_size / (1024*1024):.1f}MB. Consider cleaning old logs.',
                        'command': 'python -c "from log_analyst import *; # cleanup script"'
                    })
        except:
            pass
        
        return recommendations

def run_startup_analysis(enable_console_output: bool = True) -> dict:
    """
    Run startup analysis and return results.
    This is the main function to call when starting the application.
    """
    analyzer = StartupAnalyzer(enable_console_output)
    return analyzer.analyze_and_report()

def quick_status_check() -> str:
    """
    Get a one-line status of the previous run.
    Returns: "[OK]", "[WARNINGS]", "[ERRORS]", or "[UNKNOWN]"
    """
    try:
        if not LogAnalysisAgent:
            return "[UNKNOWN]"
        
        last_run = analyze_last_run()
        
        if last_run['status'] == 'no_sessions':
            return "[FIRST RUN]"
        elif last_run.get('errors', 0) > 0:
            return f"[ERRORS] ({last_run['errors']})"
        elif last_run.get('warnings', 0) > 0:
            return f"[WARNINGS] ({last_run['warnings']})"
        else:
            return "[OK]"
    except:
        return "[UNKNOWN]"

# Auto-run analysis if this module is imported
if __name__ != "__main__":
    # Only auto-analyze if not in test mode and console output is available
    is_test_mode = os.getenv('AUTOCRATE_TEST_MODE', '0') == '1'
    has_console = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    if not is_test_mode and has_console:
        try:
            # Run quick analysis on import
            status = quick_status_check()
            if status not in ["[OK]", "[FIRST RUN]"]:
                print(f"\nAutoCrate Status: {status}")
                print("   Run 'python -m autocrate.log_analyst' for detailed analysis\n")
        except:
            pass  # Silently ignore errors during auto-analysis

if __name__ == "__main__":
    # Full analysis when run directly
    print("AutoCrate Startup Analyzer")
    print("="*40)
    
    analyzer = StartupAnalyzer(enable_console_output=True)
    result = analyzer.analyze_and_report()
    
    # Check for critical issues
    critical_issues = analyzer.check_for_critical_issues()
    if critical_issues:
        print("\n[CRITICAL] Issues Found:")
        for issue in critical_issues:
            severity_icon = {'high': '[HIGH]', 'medium': '[MEDIUM]', 'low': '[LOW]'}.get(issue['severity'], '-')
            print(f"   {severity_icon} {issue['message']}")
            print(f"      → {issue['action']}")
    
    # Show recommendations
    recommendations = analyzer.get_startup_recommendations()
    if recommendations:
        print("\nRecommendations:")
        for rec in recommendations:
            priority_icon = {'high': '[HIGH]', 'medium': '[MEDIUM]', 'low': '[LOW]'}.get(rec['priority'], '-')
            print(f"   {priority_icon} {rec['title']}: {rec['action']}")
            if 'command' in rec:
                print(f"      Command: {rec['command']}")
    
    print("\n[COMPLETE] Startup analysis complete.")