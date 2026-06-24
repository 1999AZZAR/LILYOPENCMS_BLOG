"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from datetime import datetime, timezone
from typing import Optional

from models import User


TRUSTED_DOMAINS = {"yourcompany.com"}
BLOCKED_DOMAINS = {"tempmail.com", "mailinator.com", "10minutemail.com"}


def _get_email_domain(email: Optional[str]) -> str:
    if not email or "@" not in email:
        return ""
    return email.split("@", 1)[1].lower().strip()


def evaluate_risk_score(user: User) -> int:
    """Simple heuristic score: lower is safer.
    0-2: low risk, 3-5: medium, >5: high.
    """
    score = 0

    domain = _get_email_domain(user.email)
    if not domain:
        score += 3  # missing email
    elif domain in BLOCKED_DOMAINS:
        score += 5
    elif domain in TRUSTED_DOMAINS:
        score -= 2

    # Basic profile completeness signals
    if not user.first_name:
        score += 1
    if not user.last_name:
        score += 1

    # New accounts are neutral; can add IP/device checks later
    return max(score, 0)


def should_auto_approve(user: User) -> bool:
    """Decide whether to auto-approve a verified user.
    Currently: approve if risk score <= 2.
    """
    score = evaluate_risk_score(user)
    return score <= 2


