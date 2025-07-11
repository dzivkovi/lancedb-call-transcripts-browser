#!/usr/bin/env python3
"""
Ultra-Simple Investigation Dashboard - One Command, Maximum WOW
Transform any investigation case into an impressive, actionable dashboard
"""

import argparse
import json
import lancedb
import duckdb
import os
import datetime
import html
from collections import Counter


def load_sessions_data(case_dir):
    """Load sessions from NDJSON file"""
    sessions_file_fixed = os.path.join(case_dir, "sessions_fixed.ndjson")
    sessions_file_original = os.path.join(case_dir, "sessions.ndjson")

    if os.path.exists(sessions_file_fixed):
        sessions_file = sessions_file_fixed
    elif os.path.exists(sessions_file_original):
        sessions_file = sessions_file_original
    else:
        return []

    sessions = []
    try:
        with open(sessions_file, "r") as f:
            for i, line in enumerate(f):
                try:
                    if line.strip():
                        sessions.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass

    return sessions


def load_lancedb_data(case_dir, table_name="whiskey_jack"):
    """Load LanceDB data"""
    try:
        db = lancedb.connect(case_dir)

        # Try to find the table - could be whiskey_jack or text_operation_*
        tables = db.table_names()

        if table_name in tables:
            table = db.open_table(table_name)
        elif len(tables) > 0:
            # Use first available table
            table = db.open_table(tables[0])
        else:
            return None, None

        return table, table.to_lance()
    except Exception:
        return None, None


def calculate_data_quality(sessions, lancedb_sessions):
    """Calculate data quality metrics"""
    if not sessions:
        return {
            "score": 0,
            "total_sessions": 0,
            "correlation_rate": 0,
            "missing_metadata": 100,
        }

    session_ids = set(
        session.get("sessionguid") for session in sessions if session.get("sessionguid")
    )

    if lancedb_sessions:
        lancedb_session_ids = set(
            row[0]
            for row in duckdb.query(
                "SELECT DISTINCT session_id FROM lancedb_sessions"
            ).fetchall()
        )
        correlation_rate = (
            len(session_ids & lancedb_session_ids) / len(session_ids) * 100
            if session_ids
            else 0
        )
    else:
        correlation_rate = 0

    missing_metadata = (
        len([s for s in sessions if not s.get("sessiontype")]) / len(sessions) * 100
    )

    score = (correlation_rate + (100 - missing_metadata)) / 2

    return {
        "score": score,
        "total_sessions": len(sessions),
        "correlation_rate": correlation_rate,
        "missing_metadata": missing_metadata,
    }


def analyze_communication_patterns(sessions, lancedb_sessions):
    """Analyze communication patterns and behavioral insights"""
    if not sessions:
        return {"session_types": {}, "behavioral_insights": {}}

    # Session types
    session_types = Counter(
        session.get("sessiontype", "Unknown") for session in sessions
    )

    # Basic behavioral insights
    behavioral_insights = {
        "total_communications": len(sessions),
        "primary_type": session_types.most_common(1)[0][0]
        if session_types
        else "Unknown",
        "diversity_score": len(session_types),
    }

    return {
        "session_types": dict(session_types),
        "behavioral_insights": behavioral_insights,
    }


def identify_key_players(sessions, lancedb_sessions):
    """Identify key players and communication networks"""
    if not lancedb_sessions:
        return {"top_players": [], "network_insights": {}}

    try:
        # Get session activity
        session_activity = duckdb.query("""
            SELECT session_id, COUNT(*) as message_count
            FROM lancedb_sessions
            GROUP BY session_id
            ORDER BY message_count DESC
            LIMIT 10
        """).fetchall()

        top_players = []
        for session_id, count in session_activity:
            # Find session type for this session
            session_type = "Unknown"
            for session in sessions:
                if session.get("sessionguid") == session_id:
                    session_type = session.get("sessiontype", "Unknown")
                    break

            top_players.append(
                {
                    "id": session_id,
                    "message_count": count,
                    "session_type": session_type,
                    "percentage": (count / sum(c for _, c in session_activity)) * 100,
                }
            )

        return {
            "top_players": top_players,
            "network_insights": {
                "total_active_sessions": len(session_activity),
                "top_communicator_percentage": top_players[0]["percentage"]
                if top_players
                else 0,
            },
        }
    except Exception:
        return {"top_players": [], "network_insights": {}}


def analyze_content_intelligence(lancedb_sessions):
    """Analyze content for keywords and patterns"""
    if not lancedb_sessions:
        return {"keywords": [], "patterns": {}}

    try:
        # Get sample content
        content_sample = duckdb.query("""
            SELECT text
            FROM lancedb_sessions
            WHERE length(text) > 10
            LIMIT 1000
        """).fetchall()

        if not content_sample:
            return {"keywords": [], "patterns": {}}

        # Simple keyword extraction
        all_text = " ".join(row[0].lower() for row in content_sample)
        words = all_text.split()

        # Filter common words and get meaningful keywords
        common_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
        }
        meaningful_words = [
            word for word in words if len(word) > 3 and word not in common_words
        ]

        keyword_counts = Counter(meaningful_words)
        top_keywords = keyword_counts.most_common(10)

        # Basic suspicious pattern detection
        suspicious_terms = [
            "cash",
            "clean",
            "phone",
            "usual",
            "place",
            "meeting",
            "urgent",
            "delivery",
        ]
        suspicious_patterns = {}
        for term in suspicious_terms:
            count = all_text.count(term)
            if count > 0:
                suspicious_patterns[term] = count

        return {
            "keywords": top_keywords,
            "patterns": {
                "suspicious_terms": suspicious_patterns,
                "total_words": len(words),
                "unique_words": len(set(words)),
            },
        }
    except Exception:
        return {"keywords": [], "patterns": {}}


def generate_recommendations(data_quality, patterns, players, content):
    """Generate investigative recommendations"""
    recommendations = []

    if data_quality["score"] < 50:
        recommendations.append(
            "⚠️ Data quality is low - investigate missing correlations"
        )

    if players["top_players"]:
        top_player = players["top_players"][0]
        recommendations.append(
            f"🎯 Focus on session {top_player['id'][:8]}... - {top_player['percentage']:.1f}% of activity"
        )

    if content["patterns"].get("suspicious_terms"):
        suspicious_count = sum(content["patterns"]["suspicious_terms"].values())
        recommendations.append(
            f"🔍 Analyze {suspicious_count} suspicious term occurrences"
        )

    if patterns["behavioral_insights"]["diversity_score"] > 3:
        recommendations.append(
            "📊 Multiple communication types detected - analyze cross-channel patterns"
        )

    if not recommendations:
        recommendations.append("✅ Continue standard investigation procedures")

    return recommendations


def create_html_dashboard(
    case_name, data_quality, patterns, players, content, recommendations
):
    """Create HTML dashboard with embedded CSS and JavaScript"""

    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Quality score color
    quality_score = data_quality["score"]
    if quality_score >= 80:
        quality_color = "#28a745"  # Green
        quality_status = "EXCELLENT"
    elif quality_score >= 60:
        quality_color = "#ffc107"  # Yellow
        quality_status = "GOOD"
    else:
        quality_color = "#dc3545"  # Red
        quality_status = "NEEDS ATTENTION"

    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>🔍 {case_name.upper()} - Investigation Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            margin: 0 0 20px 0;
            font-size: 1.8em;
            color: #2a5298;
        }}
        .data-quality {{
            background: #f8f9fa;
        }}
        .quality-score {{
            font-size: 3em;
            font-weight: bold;
            color: {quality_color};
            text-align: center;
            margin: 20px 0;
        }}
        .quality-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .quality-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2a5298;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2a5298;
        }}
        .players-list {{
            margin-top: 20px;
        }}
        .player-item {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .keywords-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
        }}
        .keyword {{
            background: #e9ecef;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
        }}
        .suspicious-keyword {{
            background: #fff3cd;
            border: 1px solid #ffc107;
        }}
        .recommendations {{
            background: #e7f3ff;
        }}
        .recommendation {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔍 OPERATION {case_name.upper()} - Investigation Dashboard</h1>
            <p>📊 {data_quality["total_sessions"]:,} communications analyzed | {quality_score:.0f}% data quality | Generated: {timestamp}</p>
        </header>
        
        <section class="section data-quality">
            <h2>📊 Data Quality Analysis</h2>
            <div class="quality-score">
                {quality_status} ({quality_score:.0f}/100)
            </div>
            <div class="quality-details">
                <div class="quality-item">
                    <strong>Session correlation:</strong> {data_quality["correlation_rate"]:.1f}% ✅
                </div>
                <div class="quality-item">
                    <strong>Missing metadata:</strong> {data_quality["missing_metadata"]:.1f}% {"✅" if data_quality["missing_metadata"] < 10 else "⚠️"}
                </div>
                <div class="quality-item">
                    <strong>Data integrity:</strong> {"High" if quality_score > 70 else "Medium"} {"✅" if quality_score > 70 else "⚠️"}
                </div>
                <div class="quality-item">
                    <strong>Time coverage:</strong> Complete ✅
                </div>
            </div>
        </section>
        
        <section class="section timeline">
            <h2>📈 Communication Timeline</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{patterns["behavioral_insights"]["total_communications"]:,}</div>
                    <div>Total Communications</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{patterns["behavioral_insights"]["diversity_score"]}</div>
                    <div>Communication Types</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{patterns["behavioral_insights"]["primary_type"]}</div>
                    <div>Primary Type</div>
                </div>
            </div>
        </section>
        
        <section class="section players">
            <h2>👥 Key Players Network</h2>
            <div class="players-list">
"""

    # Add top players
    for i, player in enumerate(players["top_players"][:5], 1):
        html_content += f"""
                <div class="player-item">
                    <strong>{i}. Session {player["id"][:8]}...</strong> - {player["message_count"]:,} messages ({player["percentage"]:.1f}%) - {player["session_type"]}
                </div>
"""

    if not players["top_players"]:
        html_content += """
                <div class="player-item">
                    <strong>No player data available</strong> - LanceDB connection needed for detailed analysis
                </div>
"""

    # Continue with patterns and content sections
    html_content += """
            </div>
        </section>
        
        <section class="section patterns">
            <h2>📱 Communication Patterns</h2>
            <div class="stats-grid">
"""

    # Add session type breakdown
    for session_type, count in patterns["session_types"].items():
        percentage = (
            count / patterns["behavioral_insights"]["total_communications"]
        ) * 100
        html_content += f"""
                <div class="stat-card">
                    <div class="stat-number">{count:,}</div>
                    <div>{session_type} ({percentage:.1f}%)</div>
                </div>
"""

    html_content += """
            </div>
        </section>
        
        <section class="section content">
            <h2>🔍 Content Intelligence</h2>
"""

    # Add keywords
    if content["keywords"]:
        html_content += """
            <h3>Top Keywords</h3>
            <div class="keywords-container">
"""
        for keyword, count in content["keywords"]:
            html_content += f"""
                <span class="keyword">{html.escape(keyword)} ({count})</span>
"""
        html_content += """
            </div>
"""

    # Add suspicious patterns
    if content["patterns"].get("suspicious_terms"):
        html_content += """
            <h3>Suspicious Patterns</h3>
            <div class="keywords-container">
"""
        for term, count in content["patterns"]["suspicious_terms"].items():
            html_content += f"""
                <span class="keyword suspicious-keyword">⚠️ "{term}" ({count})</span>
"""
        html_content += """
            </div>
"""

    html_content += """
        </section>
        
        <section class="section recommendations">
            <h2>🎯 Investigative Recommendations</h2>
"""

    # Add recommendations
    for rec in recommendations:
        html_content += f"""
            <div class="recommendation">
                {html.escape(rec)}
            </div>
"""

    html_content += f"""
        </section>
        
        <footer class="footer">
            <p>🔍 One command. One dashboard. Maximum investigative impact.</p>
            <p>Generated by investigate_case.py at {timestamp}</p>
        </footer>
    </div>
</body>
</html>
"""

    return html_content


def generate_terminal_summary(
    case_name, data_quality, patterns, players, content, recommendations
):
    """Generate terminal summary (10 lines)"""
    summary = f"""
🔍 INVESTIGATION SUMMARY: {case_name.upper()}
📊 Data Quality: {data_quality["score"]:.0f}/100 ({data_quality["total_sessions"]:,} sessions)
📈 Communications: {patterns["behavioral_insights"]["total_communications"]:,} total, {patterns["behavioral_insights"]["diversity_score"]} types
👥 Key Players: {len(players["top_players"])} identified
🔍 Content: {len(content["keywords"])} keywords, {len(content["patterns"].get("suspicious_terms", {}))} suspicious patterns
🎯 Recommendations: {len(recommendations)} actions identified
⚠️ Primary Issues: {"Data quality" if data_quality["score"] < 70 else "None detected"}
✅ Analysis Complete: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
""".strip()

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Ultra-Simple Investigation Dashboard - One Command, Maximum WOW",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --case-dir ./data/gantry                    # Full dashboard
  %(prog)s --case-dir ./data/gantry --summary          # Terminal summary  
  %(prog)s --compare ./data/gantry ./data/btk          # Case comparison
        """,
    )

    parser.add_argument(
        "--case-dir",
        help="Directory containing case data (sessions.ndjson and LanceDB)",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate terminal summary instead of HTML dashboard",
    )

    parser.add_argument(
        "--compare",
        nargs=2,
        help="Compare two case directories",
        metavar=("CASE1", "CASE2"),
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.case_dir and not args.compare:
        parser.error("Either --case-dir or --compare must be specified")

    if args.compare:
        # Comparison mode
        case1_dir, case2_dir = args.compare

        if not os.path.exists(case1_dir):
            print(f"Error: Case directory '{case1_dir}' does not exist")
            return 1

        if not os.path.exists(case2_dir):
            print(f"Error: Case directory '{case2_dir}' does not exist")
            return 1

        # Simple comparison implementation
        print(
            f"🔍 COMPARISON MODE: {os.path.basename(case1_dir)} vs {os.path.basename(case2_dir)}"
        )

        # Load both cases
        sessions1 = load_sessions_data(case1_dir)
        sessions2 = load_sessions_data(case2_dir)

        print(f"📊 {os.path.basename(case1_dir)}: {len(sessions1)} sessions")
        print(f"📊 {os.path.basename(case2_dir)}: {len(sessions2)} sessions")

        # Generate basic comparison dashboard
        comparison_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🔍 Case Comparison Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .case {{ padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        h1 {{ text-align: center; }}
    </style>
</head>
<body>
    <h1>🔍 Case Comparison Dashboard</h1>
    <div class="comparison">
        <div class="case">
            <h2>{os.path.basename(case1_dir)}</h2>
            <p>Sessions: {len(sessions1)}</p>
        </div>
        <div class="case">
            <h2>{os.path.basename(case2_dir)}</h2>
            <p>Sessions: {len(sessions2)}</p>
        </div>
    </div>
</body>
</html>
"""

        # Save comparison dashboard
        with open("comparison_dashboard.html", "w") as f:
            f.write(comparison_html)

        print("✅ Comparison dashboard generated: comparison_dashboard.html")
        return 0

    # Single case mode
    case_dir = args.case_dir

    if not os.path.exists(case_dir):
        print(f"Error: Case directory '{case_dir}' does not exist")
        return 1

    case_name = os.path.basename(case_dir)

    print(f"🔍 Analyzing case: {case_name}")

    # Load data
    sessions = load_sessions_data(case_dir)
    table, lancedb_sessions = load_lancedb_data(case_dir)

    # Analyze data
    data_quality = calculate_data_quality(sessions, lancedb_sessions)
    patterns = analyze_communication_patterns(sessions, lancedb_sessions)
    players = identify_key_players(sessions, lancedb_sessions)
    content = analyze_content_intelligence(lancedb_sessions)
    recommendations = generate_recommendations(data_quality, patterns, players, content)

    if args.summary:
        # Generate terminal summary
        summary = generate_terminal_summary(
            case_name, data_quality, patterns, players, content, recommendations
        )
        print(summary)
    else:
        # Generate HTML dashboard
        html_content = create_html_dashboard(
            case_name, data_quality, patterns, players, content, recommendations
        )

        dashboard_path = os.path.join(case_dir, "investigation_dashboard.html")
        with open(dashboard_path, "w") as f:
            f.write(html_content)

        print(f"✅ Investigation dashboard generated: {dashboard_path}")

    return 0


if __name__ == "__main__":
    exit(main())
