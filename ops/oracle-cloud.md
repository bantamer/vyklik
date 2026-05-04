# Deploy on Oracle Cloud (Always Free)

This walks through deploying `vyklik` on an Oracle Cloud Always Free VM. The free tier
includes a `VM.Standard.A1.Flex` ARM Ampere instance with up to 4 OCPUs and 24 GB RAM,
which is wildly overkill for this workload but means we can run everything (Postgres,
poller, bot) in the same box without ever hitting limits.

## 0. Prerequisites

- Oracle Cloud account (free tier; requires a credit card for verification, no charges
  if you stay within the Always Free shapes).
- A Telegram bot token from `@BotFather` and the bot already added to (and given Post
  Messages in) any channel you want notifications in. For DMs the bot doesn't need to
  be anywhere.
- An SSH keypair on the laptop you'll deploy from.

## 1. Create the VM

In the OCI console:

1. **Compute → Instances → Create instance**.
2. Image and shape:
   - Image: **Canonical Ubuntu 22.04** (latest minimal).
   - Shape: **VM.Standard.A1.Flex**, 2 OCPUs, 12 GB RAM. (Always Free covers up to 4
     OCPU / 24 GB across A1 instances.)
3. Networking: pick a VCN with a public subnet, **assign a public IPv4**.
4. Add SSH public key from your laptop.
5. Boot volume: 50 GB default is fine.
6. Create.

Wait ~1 minute, copy the public IP.

## 2. Open the security list

The default Always Free security list lets through SSH only. We don't need any other
inbound for `vyklik` — the bot uses outbound long-polling to `api.telegram.org` and
the poller fetches DUW. Healthz is bound to localhost in `compose.yml`, so it's not
reachable from the internet by default.

If you want to expose `/healthz` to an external uptime checker, add an ingress rule
for TCP/8080 from that monitor's IP and unbind the localhost prefix in
`compose.yml` (`8080:8080`).

## 3. Bootstrap the host

SSH in (Ubuntu user is `ubuntu` on Canonical images):

```bash
ssh ubuntu@<PUBLIC_IP>
```

Install Docker:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
exit
```

Reconnect so the docker group takes effect, then verify:

```bash
ssh ubuntu@<PUBLIC_IP>
docker --version && docker compose version
```

## 4. Clone the repo and configure

```bash
sudo mkdir -p /opt/vyklik
sudo chown ubuntu:ubuntu /opt/vyklik
git clone https://github.com/bantamer/vyklik.git /opt/vyklik
cd /opt/vyklik
cp .env.example .env
nano .env   # set TELEGRAM_BOT_TOKEN, change POSTGRES_PASSWORD
```

## 5. Pull or build the image

If you have a tagged release, pull from GHCR (multi-arch image so ARM works):

```bash
docker compose pull
```

Otherwise build locally — first run takes ~3 minutes on A1.Flex:

```bash
docker compose build
```

## 6. Bring it up

```bash
docker compose up -d
docker compose logs -f
```

You should see:

```
poller-1  | poller starting: interval=30s ... curated_queues=22
poller-1  | ingested queues=23 events=0 (no-change)
bot-1     | bot starting (long polling)
bot-1     | notifier listening on channel=vyklik_events
bot-1     | Run polling for bot @vyklik_bot ...
```

Send `/start` to the bot from your phone — it should reply with the welcome message.

## 7. Daily backups

Install the cron job:

```bash
sudo cp /opt/vyklik/ops/backup.sh /usr/local/bin/vyklik-backup.sh
sudo chmod +x /usr/local/bin/vyklik-backup.sh
echo "0 3 * * * ubuntu /usr/local/bin/vyklik-backup.sh >> /var/log/vyklik-backup.log 2>&1" \
  | sudo tee /etc/cron.d/vyklik-backup
```

Verify by running the script manually once: `sudo -u ubuntu /usr/local/bin/vyklik-backup.sh`.

## 8. Updating

When a new release is tagged:

```bash
cd /opt/vyklik
git pull
docker compose pull && docker compose up -d
```

Migrations apply automatically via the `migrate` one-shot service at startup.

## 9. Keeping the Always Free tier alive

Oracle reclaims A1 instances that show < 20% CPU **and** < 20% network **and** < 20%
memory utilization for 7 consecutive days. The poller alone is well under that. To
stay safely above the threshold without cron jobs that twiddle CPU just to game the
metric:

- Don't shrink below the 2 OCPU / 12 GB shape — at smaller shapes the percentage
  thresholds are easier to trip.
- Postgres and the poller already keep memory in active use; that bucket should be
  fine.
- If you start getting "instance reclaimed" warnings in the OCI console, the cleanest
  fix is to run a small synthetic load (e.g. `nice -n 19 stress-ng --cpu 1 --timeout
  300s` from a hourly cron). Avoid this if you can.

If Oracle does reclaim your VM, restore takes ~10 minutes: spin a new VM, repeat
steps 3–6, restore the most recent dump from `/var/backups/vyklik` (kept on local
boot volume — back it up off-host if you care).

## Fallback: Hetzner

If Oracle ever becomes more trouble than it's worth, the same `compose.yml` runs
unchanged on a Hetzner CX22 (€4.51/mo). Skip steps 1, 2, 9; the rest is identical.
