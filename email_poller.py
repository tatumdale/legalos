#!/usr/bin/env python3
"""Email poller for AD Legal OS — polls himalaya for inbound client emails."""
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

STATE_DIR = Path.home() / '.ad-legal-os'
LAST_CHECK_FILE = STATE_DIR / 'last_email_check.txt'
INBOUND_FILE = STATE_DIR / 'inbound_emails.json'


def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _read_last_check():
    if LAST_CHECK_FILE.exists():
        return LAST_CHECK_FILE.read_text().strip()
    return None


def _write_last_check(ts):
    _ensure_state_dir()
    LAST_CHECK_FILE.write_text(ts)


def _read_inbound():
    if INBOUND_FILE.exists():
        try:
            return json.loads(INBOUND_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _write_inbound(entries):
    _ensure_state_dir()
    INBOUND_FILE.write_text(json.dumps(entries, indent=2))


def _himalaya_available(account='atlas'):
    """Check if himalaya CLI is installed and the account is configured."""
    try:
        result = subprocess.run(
            ['himalaya', 'account', 'list', '-a', account],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _fetch_envelopes(account='atlas', since=None):
    """Fetch envelope list from himalaya."""
    cmd = ['himalaya', 'envelope', 'list', '-a', account, '-o', 'json']
    if since:
        cmd.extend(['-q', f'since:{since}'])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            logger.warning('himalaya envelope list failed: %s', result.stderr)
            return []
        return json.loads(result.stdout) if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning('Failed to fetch envelopes: %s', e)
        return []


def _read_message(envelope_id, account='atlas'):
    """Read a single message body via himalaya."""
    cmd = ['himalaya', 'message', 'read', '-a', account, '-o', 'json', str(envelope_id)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return ''
        data = json.loads(result.stdout) if result.stdout.strip() else ''
        if isinstance(data, list) and data:
            return data[0] if isinstance(data[0], str) else str(data[0])
        return str(data) if data else ''
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return ''


def poll_new_emails(account='atlas', since=None, db_path=None):
    """
    Poll himalaya for new emails since `since` (ISO timestamp).
    Writes to inbound_emails.json.
    Returns list of new email dicts.
    """
    if not _himalaya_available(account):
        logger.warning('himalaya not available or account "%s" not configured — skipping poll', account)
        return []

    if since is None:
        since = _read_last_check()

    envelopes = _fetch_envelopes(account, since)
    if not envelopes:
        _write_last_check(datetime.now(timezone.utc).isoformat())
        return []

    existing = _read_inbound()
    existing_ids = {e['id'] for e in existing}

    new_emails = []
    for env in envelopes:
        eid = str(env.get('id', ''))
        if eid in existing_ids:
            continue

        sender = env.get('from', {})
        if isinstance(sender, list) and sender:
            sender = sender[0]
        elif isinstance(sender, str):
            sender = {'name': sender, 'addr': sender}

        sender_name = sender.get('name', '') if isinstance(sender, dict) else str(sender)
        sender_email = sender.get('addr', '') if isinstance(sender, dict) else str(sender)

        body = _read_message(eid, account)

        entry = {
            'id': eid,
            'from': f'{sender_name} <{sender_email}>',
            'from_name': sender_name,
            'from_email': sender_email,
            'subject': env.get('subject', '(no subject)'),
            'body': body[:5000],
            'received_at': env.get('date', datetime.now(timezone.utc).isoformat()),
            'processed': False,
        }
        new_emails.append(entry)
        existing.append(entry)

    _write_inbound(existing)
    _write_last_check(datetime.now(timezone.utc).isoformat())

    logger.info('Polled %d new emails from account "%s"', len(new_emails), account)
    return new_emails


def get_pending_emails():
    """Return list of unprocessed emails from inbound_emails.json."""
    entries = _read_inbound()
    return [e for e in entries if not e.get('processed')]


def mark_processed(envelope_id):
    """Mark an email as processed in inbound_emails.json."""
    entries = _read_inbound()
    for e in entries:
        if str(e['id']) == str(envelope_id):
            e['processed'] = True
            break
    _write_inbound(entries)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    acct = sys.argv[1] if len(sys.argv) > 1 else 'atlas'
    results = poll_new_emails(account=acct)
    print(json.dumps(results, indent=2))
