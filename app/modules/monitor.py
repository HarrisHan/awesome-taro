#!/usr/bin/env python3
import asyncio
import aiohttp
from solana.rpc.async_api import AsyncClient as Client
from solana.rpc.commitment import Commitment
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Set, List
from dataclasses import dataclass
from app.modules.config import (
    SOLANA_RPC_URL, SMTP_SERVER, SMTP_PORT,
    SMTP_USERNAME, SMTP_PASSWORD, MAIL_DELIVERY_MODE,
    EMAIL_FROM, EMAIL_TO, MONITORING_INTERVAL
)

@dataclass
class TokenMetrics:
    address: str
    initial_price: float
    current_price: float
    buyers: Dict[str, datetime]  # address -> timestamp
    last_alert_time: datetime
    window_minutes: int = 60  # Time window to track buyers
    
    def __init__(self, address: str, initial_price: float, current_price: float):
        self.address = address
        self.initial_price = initial_price
        self.current_price = current_price
        self.buyers = {}
        self.last_alert_time = datetime.min
    
    def add_buyer(self, address: str):
        self.buyers[address] = datetime.now()
        self._cleanup_old_buyers()
    
    def _cleanup_old_buyers(self):
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.buyers = {
            addr: ts for addr, ts in self.buyers.items()
            if ts > cutoff
        }
    
    @property
    def price_change_percentage(self) -> float:
        if self.initial_price == 0:
            return 0
        return ((self.current_price - self.initial_price) / self.initial_price) * 100
    
    @property
    def unique_buyers_count(self) -> int:
        self._cleanup_old_buyers()
        return len(self.buyers)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TokenMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tokens: Dict[str, TokenMetrics] = {}
        self.BUYER_THRESHOLD = 66
        self.PRICE_CHANGE_THRESHOLD = 5.0
        self.ALERT_COOLDOWN = timedelta(hours=1)  # Prevent spam alerts
        self.session = None
        self.client = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()
        self.client = Client(SOLANA_RPC_URL, commitment=Commitment("confirmed"))

    async def send_email_alert(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = EMAIL_TO
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Run SMTP operations in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            self.logger.info(f"Alert email sent via {MAIL_DELIVERY_MODE}: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send email via {MAIL_DELIVERY_MODE}: {str(e)}")
            
    def _send_email(self, msg):
        if MAIL_DELIVERY_MODE == 'smtp':
            try:
                # SMTP delivery mode with debug logging
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.set_debuglevel(1)  # Enable debug logging
                
                # Establish secure connection
                self.logger.info("Starting TLS connection...")
                server.starttls()
                
                # Login with credentials
                self.logger.info(f"Attempting login for {SMTP_USERNAME}...")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                
                # Send message
                self.logger.info("Sending message...")
                server.send_message(msg)
                server.quit()
                self.logger.info("Message sent successfully")
            except smtplib.SMTPAuthenticationError as e:
                self.logger.error(f"SMTP Authentication failed: {str(e)}")
                raise
            except smtplib.SMTPException as e:
                self.logger.error(f"SMTP Error: {str(e)}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error during SMTP: {str(e)}")
                raise
        else:
            try:
                # Local delivery mode using Postfix
                server = smtplib.SMTP('localhost')
                server.send_message(msg)
                server.quit()
                self.logger.info("Message sent via local mail server")
            except Exception as e:
                self.logger.error(f"Local mail delivery failed: {str(e)}")
                raise

    async def get_token_price(self, token_address: str) -> float:
        if not self.session:
            self.logger.error("Session not initialized")
            return 0.0
            
        try:
            # Query Jupiter API for token price
            url = f"https://price.jup.ag/v4/price?ids={token_address}"
            async with self.session.get(url) as response:
                data = await response.json()
                
                if token_address in data.get("data", {}):
                    return float(data["data"][token_address]["price"])
                return 0.0
        except Exception as e:
            self.logger.error(f"Error fetching price for token {token_address}: {str(e)}")
            return 0.0
    
    async def process_transaction(self, transaction: dict) -> None:
        try:
            if not transaction.get("meta") or not transaction.get("transaction"):
                return

            # Extract token transfers from instruction data
            for ix in transaction["transaction"]["message"]["instructions"]:
                if ix.get("program") != "spl-token":
                    continue
                    
                # Check if it's a transfer instruction
                if ix.get("parsed", {}).get("type") == "transfer":
                    data = ix["parsed"]["info"]
                    token_address = data.get("mint")
                    buyer_address = data.get("destination")
                    
                    if not token_address or not buyer_address:
                        continue
                        
                    current_price = await self.get_token_price(token_address)
                    
                    if token_address not in self.tokens:
                        self.tokens[token_address] = TokenMetrics(
                            address=token_address,
                            initial_price=current_price,
                            current_price=current_price
                        )
                    
                    token_metrics = self.tokens[token_address]
                    token_metrics.add_buyer(buyer_address)
                    token_metrics.current_price = current_price
                    
                    await self.check_alert_conditions(token_metrics)
            
            # End of process_transaction
            
        except Exception as e:
            self.logger.error(f"Error processing transaction: {str(e)}")
    
    async def check_alert_conditions(self, metrics: TokenMetrics) -> None:
        now = datetime.now()
        if (metrics.unique_buyers_count > self.BUYER_THRESHOLD and
            metrics.price_change_percentage < self.PRICE_CHANGE_THRESHOLD and
            now - metrics.last_alert_time > self.ALERT_COOLDOWN):
            
            subject = f"Alert: High Buying Activity Detected for Token {metrics.address}"
            body = f"""
Token Address: {metrics.address}
Unique Buyers in Last {metrics.window_minutes} Minutes: {metrics.unique_buyers_count}
Price Change: {metrics.price_change_percentage:.2f}%
Current Price: {metrics.current_price}
Initial Price: {metrics.initial_price}
Time Window: {metrics.window_minutes} minutes
Alert Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
            """
            await self.send_email_alert(subject, body)
            metrics.last_alert_time = now

    async def monitor_recent_transactions(self):
        try:
            # Get all SPL Token program transactions
            TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            
            # Get recent signatures for the Token program
            if not self.client:
                self.logger.error("Solana client not initialized")
                return
                
            signatures = await self.client.get_signatures_for_address(TOKEN_PROGRAM_ID)
            if not signatures or not hasattr(signatures, 'value'):
                self.logger.error("Failed to get signatures")
                return
            
            for sig_info in signatures.value:
                tx = await self.client.get_transaction(
                    sig_info.signature,
                    encoding="jsonParsed"
                )
                
                if tx and tx.value:
                    await self.process_transaction(tx.value)
                    
        except Exception as e:
            self.logger.error(f"Error fetching recent transactions: {str(e)}")

    async def run(self):
        self.logger.info("Starting Solana token monitoring...")
        try:
            await self.initialize()
            while True:
                try:
                    await self.monitor_recent_transactions()
                    await asyncio.sleep(MONITORING_INTERVAL)
                except KeyboardInterrupt:
                    self.logger.info("Monitoring stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Monitoring error: {str(e)}")
                    await asyncio.sleep(MONITORING_INTERVAL)
        finally:
            if self.session:
                await self.session.close()
            self.logger.info("Monitoring stopped, resources cleaned up")

if __name__ == "__main__":
    monitor = TokenMonitor()
    asyncio.run(monitor.run())
