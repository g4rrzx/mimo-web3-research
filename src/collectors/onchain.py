"""On-chain whale watching via block explorer APIs."""
import time
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.storage.db import Database


CHAIN_CONFIG = {
    "arbitrum": {
        "explorer_api": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "native_symbol": "ETH",
    },
    "base": {
        "explorer_api": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "native_symbol": "ETH",
    },
    "optimism": {
        "explorer_api": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
    },
}


class OnChainCollector:
    """Collect whale transactions from EVM chains."""

    def __init__(self, db: Database):
        self.cfg = get_config()
        self.db = db
        self.log = get_logger()
        self._eth_price_cache = None
        self._eth_price_ts = 0

    def _get_eth_price(self) -> float:
        """Get ETH price (cached for 5 min)."""
        now = time.time()
        if self._eth_price_cache and (now - self._eth_price_ts) < 300:
            return self._eth_price_cache

        try:
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
                timeout=10,
            )
            price = r.json()["ethereum"]["usd"]
            self._eth_price_cache = price
            self._eth_price_ts = now
            return price
        except Exception as e:
            self.log.warning(f"ETH price fetch failed: {e}")
            return self._eth_price_cache or 3000.0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    def _fetch_explorer(self, chain: str, params: dict) -> dict:
        """Call block explorer API."""
        chain_cfg = CHAIN_CONFIG[chain]
        api_key = self.cfg.env(chain_cfg["api_key_env"], "")
        params["apikey"] = api_key

        r = requests.get(chain_cfg["explorer_api"], params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_wallet_txs(
        self,
        chain: str,
        address: str,
        limit: int = 50,
    ) -> list:
        """Get recent transactions for a wallet."""
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "page": 1,
            "offset": limit,
            "sort": "desc",
        }

        try:
            data = self._fetch_explorer(chain, params)
            if data.get("status") != "1":
                return []
            return data.get("result", [])
        except Exception as e:
            self.log.error(f"Failed fetching txs for {address} on {chain}: {e}")
            return []

    def filter_whale_txs(
        self,
        txs: list,
        min_value_usd: float,
        chain: str,
    ) -> list:
        """Filter transactions above threshold."""
        eth_price = self._get_eth_price()
        whales = []

        for tx in txs:
            try:
                value_wei = int(tx.get("value", 0))
                value_eth = value_wei / 1e18
                value_usd = value_eth * eth_price

                if value_usd >= min_value_usd:
                    whales.append({
                        "chain": chain,
                        "tx_hash": tx.get("hash"),
                        "from_address": tx.get("from"),
                        "to_address": tx.get("to"),
                        "value_eth": value_eth,
                        "value_usd": value_usd,
                        "token_symbol": CHAIN_CONFIG[chain]["native_symbol"],
                        "block_number": int(tx.get("blockNumber", 0)),
                        "timestamp": int(tx.get("timeStamp", 0)),
                    })
            except (ValueError, TypeError) as e:
                self.log.debug(f"Skipping tx (parse error): {e}")
                continue

        return whales

    def collect(self) -> list:
        """Run full collection cycle. Returns new whale txs saved."""
        if not self.cfg.get("whale_watching.enabled", False):
            return []

        chains = self.cfg.get("whale_watching.chains", [])
        wallets = self.cfg.get("whale_watching.watched_wallets", [])
        min_value = self.cfg.get("whale_watching.min_tx_value_usd", 100000)

        new_txs = []

        for chain in chains:
            if chain not in CHAIN_CONFIG:
                self.log.warning(f"Unknown chain: {chain}")
                continue

            for wallet in wallets:
                addr = wallet.get("address")
                label = wallet.get("label", "unknown")

                if not addr or addr == "0x0000000000000000000000000000000000000000":
                    continue

                self.log.info(f"Scanning {label} ({addr[:10]}...) on {chain}")
                txs = self.get_wallet_txs(chain, addr, limit=20)
                whales = self.filter_whale_txs(txs, min_value, chain)

                for w in whales:
                    w["label"] = label
                    row_id = self.db.insert_whale_tx(**w)
                    if row_id:
                        new_txs.append(w)
                        self.log.info(
                            f"NEW whale: {w['value_eth']:.2f} ETH "
                            f"(${w['value_usd']:,.0f}) on {chain}"
                        )

                # Rate limit
                time.sleep(0.5)

        return new_txs
