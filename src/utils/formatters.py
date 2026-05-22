"""Report formatters for human-readable output."""
from datetime import datetime


def format_whale_tx(tx: dict) -> str:
    """Format whale tx for display."""
    chain = tx.get("chain", "?").upper()
    value_usd = tx.get("value_usd", 0)
    value_eth = tx.get("value_eth", 0)
    label = tx.get("label", "unknown")
    tx_hash = tx.get("tx_hash", "")[:10]

    return (
        f"🐋 [{chain}] {label}: {value_eth:.2f} ETH "
        f"(${value_usd:,.0f}) — tx: {tx_hash}..."
    )


def format_social_post(post: dict, max_len: int = 150) -> str:
    """Format social post for display."""
    platform = post.get("platform", "?").upper()
    author = post.get("author", "unknown")
    content = post.get("content", "")[:max_len]
    if len(post.get("content", "")) > max_len:
        content += "..."
    engagement = post.get("engagement_score", 0)

    return f"📱 [{platform}] @{author} ({engagement:.0f}) — {content}"


def format_news(article: dict) -> str:
    """Format news article for display."""
    source = article.get("source", "?")
    title = article.get("title", "")
    relevance = article.get("relevance_score", 0)

    return f"📰 [{source}] {title} (rel: {relevance:.2f})"


def format_alert(alert_type: str, data: dict) -> str:
    """Format alert message for Telegram."""
    if alert_type == "whale":
        return (
            f"🚨 *WHALE ALERT*\n"
            f"Chain: `{data.get('chain', '?').upper()}`\n"
            f"Value: *${data.get('value_usd', 0):,.0f}* "
            f"({data.get('value_eth', 0):.2f} ETH)\n"
            f"From: `{data.get('from_address', '')[:10]}...`\n"
            f"To: `{data.get('to_address', '')[:10]}...`\n"
            f"Tx: `{data.get('tx_hash', '')[:16]}...`"
        )
    elif alert_type == "sentiment":
        sent = data.get("overall_sentiment", 0)
        emoji = "🟢" if sent > 0.3 else "🔴" if sent < -0.3 else "🟡"
        return (
            f"{emoji} *SENTIMENT SHIFT*\n"
            f"Score: *{sent:+.2f}*\n"
            f"Posts analyzed: {data.get('post_count', 0)}\n"
            f"Themes: {', '.join(data.get('key_themes', [])[:3])}"
        )
    return str(data)


def format_briefing_header() -> str:
    """Generate briefing header."""
    now = datetime.now()
    return (
        f"📊 *Web3 Research Briefing*\n"
        f"_{now.strftime('%A, %d %B %Y — %H:%M WIB')}_\n"
        f"{'─' * 30}\n"
    )
