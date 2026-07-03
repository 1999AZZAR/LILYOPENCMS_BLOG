"""RBAC integration tests — fully isolated per test."""

from app import create_app


def _app():
    a = create_app()
    a.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False})
    return a


def _c(app=None):
    return (app or _app()).test_client()


def _login(c, user, pw):
    c.post("/login", data={"username": user, "password": pw})


def test_homepage():          c=_c();assert c.get("/").status_code == 200
def test_login_page():        c=_c();assert c.get("/login").status_code == 200
def test_tags_page():         c=_c();assert c.get("/tags").status_code == 200
def test_authors():           c=_c();assert c.get("/authors").status_code == 200
def test_rss():               c=_c();assert c.get("/rss.xml").status_code == 200
def test_api_tags():          c=_c();assert c.get("/api/tags").status_code == 200
def test_search():            c=_c();assert c.get("/search?q=AI").status_code == 200
def test_author():            c=_c();assert c.get("/author/admin").status_code == 200
def test_static_pages():
    c=_c()
    for s in ["tentang-kami","kebijakan-privasi","syarat-ketentuan","layanan"]:
        assert c.get(f"/page/{s}").status_code == 200

def test_t3_pages():          c=_c();_login(c,"user","user123");assert c.get("/settings/pages",follow_redirects=False).status_code in (302,403)
def test_t3_tags():           c=_c();_login(c,"user","user123");assert c.get("/settings/tags",follow_redirects=False).status_code in (302,403)
def test_t3_comments():       c=_c();_login(c,"user","user123");assert c.get("/settings/comments",follow_redirects=False).status_code in (302,403)
def test_t3_roles():          c=_c();_login(c,"user","user123");assert c.get("/settings/roles",follow_redirects=False).status_code in (302,403)
def test_t3_dashboard():      c=_c();_login(c,"user","user123");assert c.get("/settings",follow_redirects=False).status_code in (302,403)
def test_t3_brand():          c=_c();_login(c,"user","user123");assert c.get("/settings/brand-identity",follow_redirects=False).status_code in (302,403)

def test_t1_pages():          c=_c();_login(c,"admin","admin123");assert c.get("/settings/pages").status_code == 200
def test_t1_tags():           c=_c();_login(c,"admin","admin123");assert c.get("/settings/tags").status_code == 200
def test_t1_comments():       c=_c();_login(c,"admin","admin123");assert c.get("/settings/comments").status_code == 200
def test_t1_roles():          c=_c();_login(c,"admin","admin123");assert c.get("/settings/roles").status_code == 200
def test_t1_dashboard():      c=_c();_login(c,"admin","admin123");assert c.get("/settings").status_code == 200
def test_t1_brand():          c=_c();_login(c,"admin","admin123");assert c.get("/settings/brand-identity").status_code == 200
def test_t1_account():        c=_c();_login(c,"admin","admin123");assert c.get("/settings/account").status_code == 200

def test_t0_pages():          c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/pages").status_code == 200
def test_t0_tags():           c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/tags").status_code == 200
def test_t0_comments():       c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/comments").status_code == 200
def test_t0_roles():          c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/roles").status_code == 200
def test_t0_dashboard():      c=_c();_login(c,"suadmin","suladang");assert c.get("/settings").status_code == 200
def test_t0_users():          c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/users").status_code == 200
def test_t0_brand():          c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/brand-identity").status_code == 200
def test_t0_account():        c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/account").status_code == 200

def test_su_blocked_admin():  c=_c();_login(c,"admin","admin123");assert c.get("/settings/users",follow_redirects=False).status_code in (302,403)
def test_su_allowed_su():     c=_c();_login(c,"suadmin","suladang");assert c.get("/settings/users").status_code == 200

def test_comment_post():
    c=_c()
    r=c.post("/api/news/1/comments", json={"content":"t","author_name":"T","author_email":"t@t.com"})
    assert r.status_code in (200,201,404)
def test_comment_get():       c=_c();assert c.get("/api/news/1/comments").status_code == 200

def test_tag_t3_get():        c=_c();_login(c,"user","user123");assert c.get("/api/settings/tags",follow_redirects=False).status_code in (302,401,403)
def test_tag_t3_post():       c=_c();_login(c,"user","user123");assert c.post("/api/settings/tags",json={"name":"x"},follow_redirects=False).status_code in (302,401,403)
def test_tag_t1_get():        c=_c();_login(c,"admin","admin123");assert c.get("/api/settings/tags").status_code == 200
def test_tag_t1_post():       c=_c();_login(c,"admin","admin123");r=c.post("/api/settings/tags",json={"name":"pytest-tag"});assert r.status_code in (200,201,409)

def test_rate_limiter():
    a = _app()
    from shared.auth.rate_limiter import check_rate_limit
    with a.test_request_context("/login", method="POST"):
        for _ in range(10): check_rate_limit("login")
        assert not check_rate_limit("login")

def test_csrf_meta():         assert "csrf" in _c().get("/login").data.decode().lower()
def test_csrf_blocks():
    a = _app()
    a.config["WTF_CSRF_ENABLED"] = True
    assert a.test_client().post("/api/news/1/comments", json={"content":"x"}).status_code in (400,401,403)
