#!/usr/bin/env python3
"""
AutoCrate Log Analysis Tool - Simple Version
Windows-compatible version without emoji characters.

Usage:
    python analyze_logs_simple.py              # Quick last run summary
    python analyze_logs_simple.py --full       # Full analysis of recent runs
    python analyze_logs_simple.py --sessions 5 # Analyze last 5 sessions
    python analyze_logs_simple.py --status     # Just status check
"""

import sys
import os
import argparse
from pathlib import Path

# Add autocrate directory to path
sys.path.insert(0, str(Path(__file__).parent / "autocrate"))

try:
    from log_analyst import LogAnalysisAgent, analyze_last_run, analyze_recent_runs, print_last_run_summary
    from startup_analyzer import StartupAnalyzer, quick_status_check
except ImportError as e:
    print(f"Error: Could not import log analysis modules: {e}")
    print("Make sure you're running this from the AutoCrate root directory.")
    sys.exit(1)

def print_header():
    """Print the tool header."""
    print("="*60)
    print("AUTOCRATE LOG ANALYSIS TOOL")
    print("="*60)

def print_simple_analysis(max_sessions: int = 10):
    """Print comprehensive analysis of recent runs."""
    print(f"Analyzing last {max_sessions} sessions...")
    
    analysis = analyze_recent_runs(max_sessions)
    
    if analysis.get('status') == 'no_data':
        print("No log data found to analyze.")
        return
    
    summary = analysis['summary']
    print(f"\nOVERALL STATISTICS")
    print(f"   Sessions analyzed: {analysis['sessions_analyzed']}")
    print(f"   System status: {summary['status'].upper()}")
    print(f"   Error rate: {summary['error_rate']}")
    if summary.get('avg_duration_seconds'):
        print(f"   Average duration: {summary['avg_duration_seconds']}s")
    
    # Show insights by category
    insights = analysis['insights']
    
    if insights.get('errors'):
        print(f"\nERRORS FOUND ({len(insights['errors'])}): [X]")
        for error in insights['errors'][:3]:  # Top 3 errors
            print(f"   - {error['title']}: {error['message']}")
    
    if insights.get('warnings'):
        print(f"\nWARNINGS ({len(insights['warnings'])}): [!]")
        for warning in insights['warnings'][:3]:  # Top 3 warnings
            print(f"   - {warning['title']}: {warning['message']}")
    
    if insights.get('success'):
        print(f"\nSUCCESS HIGHLIGHTS ({len(insights['success'])}): [OK]")
        for success in insights['success'][:3]:  # Top 3 successes
            print(f"   - {success['title']}: {success['message']}")
    
    if insights.get('trends'):
        print(f"\nTRENDS ({len(insights['trends'])}): [>>]")
        for trend in insights['trends']:
            print(f"   - {trend['title']}: {trend['message']}")
    
    # Show recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print(f"\nRECOMMENDATIONS:")
        for rec in recommendations:
            priority_mark = {'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}.get(rec['priority'], '[?]')
            print(f"   {priority_mark} {rec['title']}")
            print(f"      -> {rec['action']}")
    
    # Show common operations
    stats = analysis.get('statistics', {})
    common_ops = stats.get('common_operations', [])
    if common_ops:
        print(f"\nMOST COMMON OPERATIONS:")
        for op, count in common_ops[:5]:
            print(f"   - {op}: {count} times")

def print_session_timeline(max_sessions: int = 10):
    """Print timeline of recent sessions."""
    analysis = analyze_recent_runs(max_sessions)
    
    if analysis.get('status') == 'no_data':
        print("No session data found.")
        return
    
    timeline = analysis.get('statistics', {}).get('session_timeline', [])
    
    print(f"\nSESSION TIMELINE (Last {len(timeline)} sessions):")
    print("-" * 80)
    print("Session ID               | Time     | Duration | Errors | Status")
    print("-" * 80)
    
    for session in timeline:
        session_id = session['session_id'][:20] + "..." if len(session['session_id']) > 23 else session['session_id']
        timestamp = session['timestamp'][11:19]  # Just time part
        duration = f"{session['duration']:.2f}s" if session['duration'] else "N/A"
        errors = session['errors']
        status = "OK" if errors == 0 else f"{errors} errors"
        
        print(f"{session_id:<25} | {timestamp} | {duration:>8} | {errors:>6} | {status}")

def print_last_run_simple():
    """Print a simple version of last run summary."""
    summary = analyze_last_run()
    
    print("\n" + "="*60)
    print("AUTOCRATE - LAST RUN ANALYSIS")
    print("="*60)
    
    if summary['status'] == 'no_sessions':
        print("No previous runs found")
        return
    
    print(f"Session: {summary['session_id']}")
    print(f"Time: {summary['timestamp']}")
    print(f"Status: {summary['status'].upper()}")
    
    if summary['errors'] > 0:
        print(f"Errors: {summary['errors']}")
    if summary['warnings'] > 0:
        print(f"Warnings: {summary['warnings']}")
    if summary['duration']:
        print(f"Duration: {summary['duration']:.2f}s")
    
    # Show insights
    if summary['insights']:
        print("\nKey Insights:")
        for insight in summary['insights'][:3]:  # Top 3 insights
            icon = {'success': '[OK]', 'error': '[X]', 'warning': '[!]', 'trend': '[>>]'}.get(insight['type'], '[-]')
            print(f"   {icon} {insight['title']}: {insight['message']}")
    
    print("="*60)

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="AutoCrate Log Analysis Tool - Simple Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze_logs_simple.py                 # Quick summary of last run
    python analyze_logs_simple.py --full          # Full analysis
    python analyze_logs_simple.py --sessions 20   # Analyze last 20 sessions
    python analyze_logs_simple.py --status        # Just status check
    python analyze_logs_simple.py --timeline      # Show session timeline
        """
    )
    
    parser.add_argument('--full', action='store_true',
                       help='Run full analysis of recent sessions')
    parser.add_argument('--sessions', type=int, default=10,
                       help='Number of sessions to analyze (default: 10)')
    parser.add_argument('--status', action='store_true',
                       help='Show just the status of last run')
    parser.add_argument('--timeline', action='store_true',
                       help='Show timeline of recent sessions')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_header()
    
    try:
        if args.status:
            # Just show status
            status = quick_status_check()
            # Clean up status for simple display
            status_clean = status  # Status should already be clean without emojis
            print(f"AutoCrate Status: {status_clean}")
            
        elif args.timeline:
            # Show session timeline
            print_session_timeline(args.sessions)
            
        elif args.full:
            # Full analysis
            print_simple_analysis(args.sessions)
            
        else:
            # Default: last run summary
            if not args.quiet:
                print("Last Run Summary:")
            print_last_run_simple()
        
        if not args.quiet:
            print("\n" + "="*60)
            print("Tip: Use --help to see all available options")
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during analysis: {e}")
        if not args.quiet:
            print("Try running with --quiet for minimal output, or check log files manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()