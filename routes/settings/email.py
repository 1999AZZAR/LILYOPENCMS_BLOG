"""
Email Management Routes

Pages: email settings, outbox, mail log, compose mail.
All routes restricted to admin-tier or owner.
"""

import os
from routes import main_blueprint
from .common_imports import *
from models import EmailLog, EmailStatus, EmailType


# ─── helpers ────────────────────────────────────────────────────────────────

SMTP_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "smtp_config.txt")


def _read_smtp_config() -> dict:
    cfg = {}
    if not os.path.exists(SMTP_CONFIG_PATH):
        return cfg
    with open(SMTP_CONFIG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if v.lower() in ("true", "false"):
                    cfg[k] = v.lower() == "true"
                elif v.isdigit():
                    cfg[k] = int(v)
                elif v == "":
                    cfg[k] = None
                else:
                    cfg[k] = v
    return cfg


def _format_cfg_val(val) -> str:
    if val is None:
        return ""
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)


def _write_smtp_config(cfg: dict) -> None:
    existing_lines = []
    if os.path.exists(SMTP_CONFIG_PATH):
        with open(SMTP_CONFIG_PATH, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()

    result = []
    written_keys = set()
    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(line)
            continue
        if "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k in cfg:
                result.append(f"{k}={_format_cfg_val(cfg[k])}\n")
                written_keys.add(k)
            else:
                result.append(line)
    for k, v in cfg.items():
        if k not in written_keys:
            result.append(f"{k}={_format_cfg_val(v)}\n")

    os.makedirs(os.path.dirname(SMTP_CONFIG_PATH), exist_ok=True)
    with open(SMTP_CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(result)


# ─── pages ──────────────────────────────────────────────────────────────────

@main_blueprint.route("/settings/email")
@login_required
def settings_email():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    smtp_config = _read_smtp_config()
    return render_template("admin/settings/email_settings.html", smtp_config=smtp_config)


@main_blueprint.route("/settings/email/outbox")
@login_required
def settings_email_outbox():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    page = request.args.get("page", 1, type=int)
    per_page = 30
    outbox = (
        EmailLog.query
        .filter(EmailLog.status.in_([EmailStatus.QUEUED, EmailStatus.SENT]))
        .order_by(EmailLog.queued_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template("admin/settings/email_outbox.html", outbox=outbox)


@main_blueprint.route("/settings/email/log")
@login_required
def settings_email_log():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    page = request.args.get("page", 1, type=int)
    per_page = 30
    status_filter = request.args.get("status", "")
    type_filter = request.args.get("type", "")
    q = request.args.get("q", "").strip()

    query = EmailLog.query
    if status_filter:
        try:
            query = query.filter(EmailLog.status == EmailStatus(status_filter))
        except ValueError:
            pass
    if type_filter:
        try:
            query = query.filter(EmailLog.email_type == EmailType(type_filter))
        except ValueError:
            pass
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(EmailLog.recipient.ilike(like), EmailLog.subject.ilike(like))
        )

    logs = query.order_by(EmailLog.queued_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    statuses = [s.value for s in EmailStatus]
    types = [t.value for t in EmailType]
    return render_template(
        "admin/settings/email_log.html",
        logs=logs,
        statuses=statuses,
        types=types,
        status_filter=status_filter,
        type_filter=type_filter,
        q=q,
    )


@main_blueprint.route("/settings/email/compose")
@login_required
def settings_email_compose():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return render_template("admin/settings/email_compose.html")


# ─── API ────────────────────────────────────────────────────────────────────

@main_blueprint.route("/api/settings/email/config", methods=["GET"])
@login_required
def api_email_config_get():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    return jsonify({"success": True, "config": _read_smtp_config()})


@main_blueprint.route("/api/settings/email/config", methods=["POST"])
@login_required
def api_email_config_save():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    allowed = {
        "smtp_server", "smtp_port", "smtp_use_tls", "smtp_use_ssl",
        "smtp_username", "smtp_password",
        "mail_default_sender", "mail_sender_name", "mail_reply_to",
        "email_rate_limit_per_hour", "email_rate_limit_per_day",
        "smtp_verify_ssl", "smtp_timeout", "smtp_debug", "smtp_suppress_send",
    }

    int_fields = {"smtp_port", "email_rate_limit_per_hour", "email_rate_limit_per_day", "smtp_timeout"}
    bool_fields = {"smtp_use_tls", "smtp_use_ssl", "smtp_verify_ssl", "smtp_debug", "smtp_suppress_send"}

    cfg = _read_smtp_config()
    for k, v in data.items():
        if k in allowed:
            if v == "" or v is None:
                cfg[k] = None
            elif k in int_fields:
                try:
                    cfg[k] = int(v)
                except (ValueError, TypeError):
                    cfg[k] = None
            elif k in bool_fields:
                if isinstance(v, str):
                    cfg[k] = v.lower() == "true"
                else:
                    cfg[k] = bool(v)
            else:
                cfg[k] = str(v)
    _write_smtp_config(cfg)

    try:
        from routes.utils.email_service import email_service
        email_service._initialized = False
    except Exception:
        pass

    return jsonify({"success": True, "message": "Email configuration saved."})


@main_blueprint.route("/api/settings/email/test", methods=["POST"])
@login_required
def api_email_test():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    data = request.get_json(force=True) or {}
    recipient = data.get("recipient", "").strip()
    if not recipient:
        return jsonify({"success": False, "message": "Recipient email required"}), 400

    try:
        from routes.utils.email_service import email_service
        result = email_service.test_smtp_connection()
        if not result["success"]:
            return jsonify({"success": False, "message": result["message"]})

        sent = email_service.send_email(
            to=recipient,
            subject="Test Email from LilyOpenCMS",
            body="This is a test email sent from your LilyOpenCMS dashboard.",
            html_body="<p>This is a <strong>test email</strong> sent from your LilyOpenCMS dashboard.</p>",
        )
        if sent:
            return jsonify({"success": True, "message": f"Test email sent to {recipient}"})
        return jsonify({"success": False, "message": "Failed to send test email. Check SMTP config."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@main_blueprint.route("/api/settings/email/smtp-test", methods=["POST"])
@login_required
def api_smtp_connection_test():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    try:
        from routes.utils.email_service import email_service
        result = email_service.test_smtp_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@main_blueprint.route("/api/settings/email/send", methods=["POST"])
@login_required
def api_email_send():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    data = request.get_json(force=True) or {}
    to = data.get("to", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()

    if not to or not subject or not body:
        return jsonify({"success": False, "message": "to, subject, and body are required"}), 400

    try:
        from routes.utils.email_service import email_service
        html_body = data.get("html_body") or f"<p>{body}</p>"
        sent = email_service.send_email(
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
            user_id=current_user.id,
        )
        if sent:
            return jsonify({"success": True, "message": f"Email sent to {to}"})
        return jsonify({"success": False, "message": "Failed to send email. Check SMTP config."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@main_blueprint.route("/api/settings/email/log/<int:log_id>", methods=["GET"])
@login_required
def api_email_log_detail(log_id):
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    log = EmailLog.query.get_or_404(log_id)
    return jsonify({"success": True, "log": log.to_dict()})


@main_blueprint.route("/api/settings/email/log/<int:log_id>/retry", methods=["POST"])
@login_required
def api_email_log_retry(log_id):
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    log = EmailLog.query.get_or_404(log_id)
    if log.status not in [EmailStatus.FAILED, EmailStatus.BOUNCED]:
        return jsonify({"success": False, "message": "Only failed/bounced emails can be retried"}), 400
    try:
        from routes.utils.email_service import email_service
        sent = email_service.send_email(
            to=log.recipient,
            subject=log.subject,
            body="(Retry) Please check your original email.",
            user_id=log.user_id,
            email_type=log.email_type,
            template_name=log.template_name,
        )
        if sent:
            return jsonify({"success": True, "message": "Email re-queued successfully."})
        return jsonify({"success": False, "message": "Retry failed. Check SMTP config."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@main_blueprint.route("/api/settings/email/stats", methods=["GET"])
@login_required
def api_email_stats():
    if not (current_user.is_admin_tier() or current_user.is_owner()):
        abort(403)
    total = EmailLog.query.count()
    sent = EmailLog.query.filter_by(status=EmailStatus.SENT).count()
    delivered = EmailLog.query.filter_by(status=EmailStatus.DELIVERED).count()
    failed = EmailLog.query.filter_by(status=EmailStatus.FAILED).count()
    queued = EmailLog.query.filter_by(status=EmailStatus.QUEUED).count()
    bounced = EmailLog.query.filter_by(status=EmailStatus.BOUNCED).count()
    return jsonify({
        "success": True,
        "stats": {
            "total": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "queued": queued,
            "bounced": bounced,
        },
    })
