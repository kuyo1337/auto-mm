```markdown
# Discord Litecoin Middleman Bot

A Discord bot for secure Litecoin (LTC) transactions, acting as a middleman.

## Features
- **Automated Middleman**: Holds LTC in unique wallets until deals are complete.
- **Currency**: Litecoin (LTC) with USD conversion via CoinGecko API.
- **Transactions**: Uses BlockCypher API for address creation and LTC transfers.
- **Roles**: Sender/receiver identification with deal confirmation.
- **Security**: Encrypted keys, 1 confirmation required, secure channels.
- **Commands**:
  - `/get_private_key`: Get deal key (admin).
  - `/get_wallet_balance`: Check balance.
  - `/send`: Send LTC (staff).
- **Fees**: 0.02% deal fee + 8% transaction fee.

## Setup
1. Install dependencies: `discord.py`, `requests`, `blockcypher`, `pycoingecko`, `urllib3`.
2. Create `config.json`:
   ```json
   {
     "owner_id": "discord_id",
     "token": "bot_token",
     "ticket_channel": "channel_id",
     "api_key": "blockcypher_key"
   }
   ```
3. Ensure `data` directory exists.
4. Run: `python bot.py`.

## Usage
- Start deal via "Crypto Middleman" button.
- Specify partner, USD amount, roles.
- Sender deposits LTC; bot confirms after 1 confirmation.
- Confirm asset exchange; sender releases funds
- Cancel deals with 30-second delay.
## Notes
- Requires BlockCypher API key.
- Comply with Discord ToS and local laws.
- Ty grok AI
```
