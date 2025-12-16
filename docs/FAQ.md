# Frequently Asked Questions (FAQ)

## General Questions

### What is the Earning Robot?

The Earning Robot is an autonomous AI-powered system that can:
- Execute AI tasks using OpenAI and Mistral APIs
- Accept payments via Stripe
- Generate automated financial reports
- Be controlled remotely via Telegram or REST API
- Run on a laptop, VPS, or cloud platform

### How much does it cost to run?

**Infrastructure costs:**
- Free if running on your laptop
- $5-20/month for a basic VPS
- Variable for cloud platforms

**Operating costs:**
- OpenAI API: ~$0.002 per 1K tokens (GPT-3.5-turbo)
- Mistral API: ~$0.0002 per 1K tokens (Mistral-tiny)
- Stripe fees: 2.9% + $0.30 per transaction

### Can I make money with this?

Yes! The robot is designed for:
- Offering AI services to customers
- Subscription-based access
- Per-query micro-payments
- Automated business processes

Your revenue depends on your pricing and customer base.

## Setup and Configuration

### Do I need all the API keys?

**Required:**
- Telegram Bot Token (for control)
- Telegram Owner ID (for authentication)

**Optional but recommended:**
- At least one AI API key (OpenAI or Mistral)
- Stripe keys (if you want to accept payments)

### How do I get a Telegram Bot Token?

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow the instructions
5. Copy the token you receive

### How do I find my Telegram User ID?

1. Search for `@userinfobot` in Telegram
2. Send `/start`
3. Copy the number shown as your user ID

### Can I use the robot without AI APIs?

No, you need at least one AI provider (OpenAI or Mistral) for the robot to function. However, you can run it without Stripe if you don't need payment processing.

### How do I change the pricing?

Edit `.env` file:
```env
SUBSCRIPTION_MONTHLY_PRICE=29.99
MICRO_PAYMENT_PRICE=0.50
```

## Usage Questions

### Can multiple people use the robot?

Yes! The robot supports multiple users. Each user can:
- Send queries via Telegram (if they know your bot)
- Use the REST API
- Have their own subscription

Only the owner (configured in `TELEGRAM_OWNER_ID`) can access admin commands like `/report`.

### How do I add more users?

Users are automatically created when they:
- Send a message to your Telegram bot
- Make an API request with their email/ID

No manual user creation needed!

### Can I use multiple AI providers?

Yes! The robot supports both OpenAI and Mistral. You can:
- Configure both API keys
- Choose per request: `/ask [question]` uses OpenAI by default
- Specify in API calls: `{"provider": "mistral"}`

### How accurate are the cost calculations?

Cost calculations are approximate and based on:
- Token usage reported by APIs
- Current API pricing
- Standard pricing tiers

Actual costs may vary. Monitor your API dashboards for exact billing.

## Technical Questions

### What database does it use?

SQLite by default. It's:
- Zero configuration
- File-based
- Perfect for small to medium deployments

For high-traffic production, consider PostgreSQL or MySQL (requires code modifications).

### Can I run it 24/7?

Yes! Recommended approaches:
- **Laptop:** Use `nohup python main.py &` to run in background
- **VPS:** Use systemd service (see INSTALLATION.md)
- **Docker:** Run with `--restart unless-stopped`
- **Cloud:** Use managed services (Cloud Run, ECS, etc.)

### What happens if the robot crashes?

- **Data:** All data is saved to SQLite database - nothing is lost
- **Recovery:** Simply restart the robot
- **Prevention:** Use process managers (systemd, Docker, supervisor)

### Can I run multiple robots?

Yes! Just use different:
- Ports (change `PORT` in `.env`)
- Database files (change `DATABASE_PATH`)
- Telegram bots (different `TELEGRAM_BOT_TOKEN`)

### How do I backup my data?

```bash
# Backup database
cp data/robot.db backups/robot-$(date +%Y%m%d).db

# Or backup entire data directory
tar -czf backup.tar.gz data/
```

Restore by copying back.

## Security Questions

### Is it secure?

The robot includes:
- Owner authentication for admin commands
- Stripe webhook signature verification
- SQLAlchemy ORM (prevents SQL injection)
- Environment-based configuration (keeps secrets safe)

**For production, also consider:**
- HTTPS/SSL for API
- API authentication
- Rate limiting
- Firewall rules
- Regular security updates

### How do I protect my API keys?

1. Never commit `.env` to git (it's in `.gitignore`)
2. Use environment variables in production
3. Use secret management (AWS Secrets, etc.)
4. Rotate keys periodically
5. Use read-only keys when possible

### Can someone steal my earnings?

If you use Stripe:
- Payments go directly to your Stripe account
- The robot only records transactions
- No money is stored in the robot

Keep your Stripe credentials secure!

## Payment Questions

### How do customers pay?

1. Robot creates a Stripe Checkout session
2. Customer is redirected to Stripe's secure checkout
3. Customer pays with credit card
4. Stripe processes payment
5. Robot receives webhook notification
6. Income is recorded automatically

### What payment methods are supported?

Stripe supports:
- Credit/debit cards
- Apple Pay / Google Pay
- Bank transfers (in some countries)
- Various local payment methods

### How do I withdraw my earnings?

Earnings go directly to your Stripe account. Withdraw from Stripe to your bank account (setup in Stripe Dashboard).

### Are there any payment fees?

Stripe charges:
- 2.9% + $0.30 per successful transaction (US)
- Rates vary by country
- No monthly fees

Check [Stripe Pricing](https://stripe.com/pricing) for details.

## Troubleshooting

### Bot doesn't respond to commands

Check:
1. Bot is running (`python main.py`)
2. `TELEGRAM_BOT_TOKEN` is correct
3. You're messaging the right bot
4. Check logs for errors

### API returns errors

Common causes:
1. Invalid API keys
2. API rate limits exceeded
3. Insufficient API credits
4. Network connectivity issues

Check error messages in logs.

### "Module not found" errors

Install dependencies:
```bash
pip install -r requirements.txt
```

### Database errors

Try:
```bash
rm -rf data/
# Database will be recreated on next run
```

### Payment webhooks not working

Verify:
1. Webhook URL is publicly accessible
2. `STRIPE_WEBHOOK_SECRET` is correct
3. Webhook events are configured in Stripe
4. Check Stripe Dashboard for webhook delivery logs

## Performance Questions

### How many requests can it handle?

Depends on:
- Your infrastructure (laptop/VPS/cloud)
- AI API rate limits
- Database performance

**Typical performance:**
- Laptop: 10-50 concurrent requests
- VPS: 50-200 concurrent requests
- Cloud (scaled): 1000+ concurrent requests

### How can I improve performance?

1. **Use caching** for repeated queries
2. **Add load balancing** for multiple instances
3. **Upgrade infrastructure** (more CPU/RAM)
4. **Use CDN** for static content
5. **Optimize database** queries
6. **Add Redis** for session storage

### Can I use a different database?

Yes, but requires code changes:
- Update `backend/database.py`
- Change SQLAlchemy connection string
- Migrate schema
- Update configuration

## Deployment Questions

### Where can I deploy it?

**Free/cheap options:**
- Your laptop (free)
- Raspberry Pi (one-time cost)
- Oracle Cloud (free tier)
- Google Cloud Run (free tier)

**Paid options:**
- DigitalOcean ($5/month)
- AWS EC2 (from $5/month)
- Heroku (from $7/month)
- Azure (from $5/month)

### Do I need a domain name?

Not required, but recommended for:
- Professional appearance
- HTTPS/SSL certificates
- Stable webhook URLs
- Email notifications

Cost: $10-15/year

### How do I get HTTPS?

**Options:**
1. **Let's Encrypt** (free) with nginx/Apache
2. **Cloud platforms** provide SSL automatically
3. **Cloudflare** (free tier)
4. **ngrok** for development/testing

## Business Questions

### Is this legal?

Yes, but:
- Follow AI provider terms of service
- Comply with payment processing rules
- Follow local business regulations
- Consider terms for commercial use
- Consult a lawyer for specific advice

### Do I need a business license?

Depends on:
- Your country/state
- Revenue level
- Business structure
- Local regulations

Consult local authorities or a lawyer.

### How do I get customers?

**Marketing ideas:**
- Social media promotion
- Content marketing (blog, YouTube)
- SEO optimization
- Paid advertising
- Partnerships
- Referral programs
- Community engagement

### What pricing should I use?

Consider:
- Your costs (API + infrastructure)
- Competitor pricing
- Target market
- Value provided
- Profit margin

**Common models:**
- Free tier + paid upgrades
- Subscription ($10-50/month)
- Per-query ($0.10-1.00)
- Credits/tokens

## Support

### Where can I get help?

1. **Documentation:** Read README, INSTALLATION, EXAMPLES
2. **GitHub Issues:** Report bugs or ask questions
3. **Community:** Join discussions (if available)
4. **Professional:** Hire a developer for customization

### How do I report a bug?

1. Check if it's already reported
2. Create a GitHub issue
3. Include:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - System info
   - Error messages/logs

### Can I hire someone to set this up?

Yes! Look for:
- Python developers
- DevOps engineers
- Freelancers on Upwork/Fiverr
- Local tech consultants

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Future Development

### What features are planned?

See [CHANGELOG.md](CHANGELOG.md) for roadmap including:
- Web dashboard
- More AI providers
- Multi-language support
- Advanced analytics
- Kubernetes support

### Can I request features?

Yes! Open a GitHub issue with:
- Feature description
- Use case
- Benefits
- Implementation ideas

### How often is it updated?

Depends on:
- Community contributions
- Bug reports
- New AI provider APIs
- Security updates

Watch the repository for updates!

---

**Still have questions? Open a GitHub issue!**
