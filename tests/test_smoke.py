"""Basic smoke tests for collectors and orchestrator."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_db_init():
    """Test DB initialization and basic ops."""
    import time
    from src.storage.db import Database

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        now_ts = int(time.time())

        # Insert whale tx (use current time so it's within query window)
        row_id = db.insert_whale_tx(
            chain="arbitrum",
            tx_hash="0xtest123",
            from_address="0xabc",
            to_address="0xdef",
            value_eth=10.5,
            value_usd=35000,
            token_symbol="ETH",
            block_number=12345,
            timestamp=now_ts,
            label="test",
        )
        assert row_id is not None, "First insert should succeed"

        # Duplicate should return None
        dup_id = db.insert_whale_tx(
            chain="arbitrum",
            tx_hash="0xtest123",
            from_address="0xabc",
            to_address="0xdef",
            value_eth=10.5,
            value_usd=35000,
            token_symbol="ETH",
            block_number=12345,
            timestamp=now_ts,
            label="test",
        )
        assert dup_id is None, "Duplicate should be rejected"

        # Query last 24h
        whales = db.get_recent_whales(hours=24, limit=10)
        assert len(whales) == 1, f"Expected 1 whale, got {len(whales)}"

        print("✅ test_db_init passed")
    finally:
        os.unlink(db_path)


def test_sentiment_quick():
    """Test quick sentiment scoring."""
    from src.analyzers.sentiment import SentimentAnalyzer

    analyzer = SentimentAnalyzer()

    # Bullish
    score = analyzer.quick_score("LFG! This is going to moon, super bullish!")
    assert score > 0, f"Expected positive, got {score}"

    # Bearish
    score = analyzer.quick_score("Total rug, market about to crash, ngmi")
    assert score < 0, f"Expected negative, got {score}"

    # Neutral
    score = analyzer.quick_score("The weather is nice today")
    assert score == 0, f"Expected 0, got {score}"

    print("✅ test_sentiment_quick passed")


def test_news_relevance():
    """Test news relevance scoring."""
    from src.collectors.news import NewsCollector

    # No DB needed for this
    class MockDB:
        def insert_news(self, **kw):
            return None

    nc = NewsCollector(MockDB())

    # High relevance
    score = nc._calc_relevance(
        "Arbitrum hits $5B TVL milestone with new DeFi protocols"
    )
    assert score > 0.5, f"Expected high score, got {score}"

    # Low relevance
    score = nc._calc_relevance("Random unrelated tech news")
    assert score < 0.2, f"Expected low score, got {score}"

    print("✅ test_news_relevance passed")


def test_formatters():
    """Test output formatters."""
    from src.utils.formatters import format_whale_tx, format_alert

    whale = {
        "chain": "arbitrum",
        "value_usd": 1500000,
        "value_eth": 500,
        "label": "binance",
        "tx_hash": "0xabc123def456",
    }

    msg = format_whale_tx(whale)
    assert "ARBITRUM" in msg
    assert "binance" in msg
    assert "$1,500,000" in msg

    alert = format_alert("whale", whale)
    assert "WHALE ALERT" in alert
    assert "$1,500,000" in alert

    print("✅ test_formatters passed")


def test_config_load():
    """Test config loading."""
    from src.utils.config import Config

    cfg = Config()
    # Just ensure it loads without crashing
    chains = cfg.get("whale_watching.chains", [])
    assert isinstance(chains, list)

    print("✅ test_config_load passed")


def run_all():
    """Run all tests."""
    print("\n=== Running smoke tests ===\n")
    test_db_init()
    test_sentiment_quick()
    test_news_relevance()
    test_formatters()
    test_config_load()
    print("\n✅ All tests passed!\n")


if __name__ == "__main__":
    run_all()
