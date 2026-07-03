#!/usr/bin/env python3
"""
Seed script — comprehensive demo data for LilyOpenCMS.
Creates users, categories, tags, news, comments, pages,
navigation, social media, team, contact info.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import (
    db, User, UserRole, BrandIdentity,
    Permission, CustomRole, Page,
    Category, Tag, News, Comment,
    news_tags,
    SocialMedia, ContactDetail, TeamMember,
    NavigationLink, CommentStatus,
)


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        now = datetime.now(timezone.utc)

        # ═══════════════════════════════════════════════════════════════
        # USERS
        # ═══════════════════════════════════════════════════════════════
        if not User.query.filter_by(username="suadmin").first():
            su = User(
                username="suadmin",
                email="admin@lilyopencms.local",
                role=UserRole.SUPERUSER,
                tier=0,
                is_active=True, is_premium=True, verified=True,
                first_name="Super", last_name="Admin",
                bio="Founder and lead developer of LilyOpenCMS.",
                social_links={"twitter": "https://twitter.com/lilyopencms", "github": "https://github.com/1999AZZAR"},
            )
            su.set_password("suladang")
            db.session.add(su)
            print("  + suadmin / suladang")
        else:
            print("  ~ suadmin exists")

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin", email="admin@example.com",
                role=UserRole.ADMIN, tier=1, is_active=True, verified=True,
                first_name="Admin", last_name="User",
                bio="Content manager and editor. Passionate about quality journalism.",
                social_links={"twitter": "https://twitter.com/admin", "linkedin": "https://linkedin.com/in/admin"},
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("  + admin / admin123")
        else:
            admin = User.query.filter_by(username="admin").first()
            print("  ~ admin exists")

        if not User.query.filter_by(username="user").first():
            u = User(
                username="user", email="user@example.com",
                role=UserRole.GENERAL, tier=3, is_active=True, verified=True,
                first_name="Test", last_name="User",
            )
            u.set_password("user123")
            db.session.add(u)
            print("  + user / user123")
        else:
            print("  ~ user exists")

        # ═══════════════════════════════════════════════════════════════
        # BRAND
        # ═══════════════════════════════════════════════════════════════
        if not BrandIdentity.query.first():
            brand = BrandIdentity(
                brand_name="LilyOpenCMS",
                tagline="Modern content management for the digital age",
                homepage_design="news",
                logo_header="/static/pic/light.png",
                logo_footer="/static/pic/dark.png",
                favicon="/static/favicon.ico",
                enable_news=True, enable_videos=True, enable_gallery=True,
                enable_albums=True, enable_premium=True, enable_about=True,
            )
            db.session.add(brand)
            print("  + brand identity")
        else:
            print("  ~ brand exists")

        # ═══════════════════════════════════════════════════════════════
        # PERMISSIONS
        # ═══════════════════════════════════════════════════════════════
        if Permission.query.count() == 0:
            perms = [
                ("news:read","Read news","news","read"), ("news:create","Create news","news","create"),
                ("news:update","Update news","news","update"), ("news:delete","Delete news","news","delete"),
                ("news:publish","Publish news","news","publish"),
                ("users:read","Read users","users","read"), ("users:update","Update users","users","update"),
                ("users:delete","Delete users","users","delete"), ("users:suspend","Suspend users","users","suspend"),
                ("roles:read","Read roles","roles","read"), ("roles:create","Create roles","roles","create"),
                ("roles:update","Update roles","roles","update"), ("roles:delete","Delete roles","roles","delete"),
                ("permissions:read","Read permissions","permissions","read"),
                ("permissions:create","Create permissions","permissions","create"),
                ("permissions:update","Update permissions","permissions","update"),
                ("permissions:delete","Delete permissions","permissions","delete"),
                ("settings:read","Read settings","settings","read"), ("settings:update","Update settings","settings","update"),
                ("analytics:read","Read analytics","analytics","read"), ("analytics:export","Export analytics","analytics","export"),
            ]
            for n, d, r, a in perms:
                db.session.add(Permission(name=n, description=d, resource=r, action=a))
            print(f"  + {len(perms)} permissions")
        else:
            print("  ~ permissions exist")

        # ═══════════════════════════════════════════════════════════════
        # CUSTOM ROLES
        # ═══════════════════════════════════════════════════════════════
        if CustomRole.query.count() == 0:
            editor = CustomRole(name="Editor", description="Manage and publish content", is_active=True)
            writer = CustomRole(name="Writer", description="Create content", is_active=True)
            db.session.add_all([editor, writer])
            db.session.flush()
            editor.permissions = Permission.query.filter(Permission.resource.in_(["news","images","videos"])).all()
            writer.permissions = Permission.query.filter(Permission.name.in_(["news:read","news:create","news:update"])).all()
            print("  + roles: Editor, Writer")
        else:
            print("  ~ roles exist")

        # ═══════════════════════════════════════════════════════════════
        # CATEGORIES
        # ═══════════════════════════════════════════════════════════════
        cat_names = ["Teknologi", "Bisnis", "Olahraga", "Hiburan", "Kesehatan", "Otomotif", "Pendidikan", "Lifestyle"]
        cats = {}
        for name in cat_names:
            c = Category.query.filter_by(name=name).first()
            if not c:
                c = Category(name=name)
                db.session.add(c)
                db.session.flush()
            cats[name] = c
        print(f"  + {len(cats)} categories")

        # ═══════════════════════════════════════════════════════════════
        # TAGS
        # ═══════════════════════════════════════════════════════════════
        tag_data = [
            ("python", "Python"), ("ai", "AI"), ("web", "Web Development"),
            ("mobile", "Mobile"), ("startup", "Startup"), ("fintech", "Fintech"),
            ("sepakbola", "Sepakbola"), ("basket", "Basket"),
            ("film", "Film"), ("musik", "Musik"),
            ("sehat", "Hidup Sehat"), ("nutrisi", "Nutrisi"),
            ("mobil", "Mobil"), ("motor", "Motor"),
            ("edtech", "EdTech"), ("beasiswa", "Beasiswa"),
            ("fashion", "Fashion"), ("travel", "Travel"),
        ]
        tag_map = {}
        for slug, name in tag_data:
            t = Tag.query.filter_by(slug=slug).first()
            if not t:
                t = Tag(name=name, slug=slug)
                db.session.add(t)
                db.session.flush()
            tag_map[slug] = t
        print(f"  + {len(tag_data)} tags")

        # ═══════════════════════════════════════════════════════════════
        # NEWS ARTICLES
        # ═══════════════════════════════════════════════════════════════
        if News.query.count() == 0:
            articles = [
                {
                    "title": "Revolusi AI: Bagaimana Kecerdasan Buatan Mengubah Industri Media",
                    "content": "<h2>Transformasi Digital di Industri Media</h2><p>Kecerdasan buatan telah membawa perubahan fundamental dalam cara kita mengonsumsi dan memproduksi konten. Dari algoritma rekomendasi yang dipersonalisasi hingga pembuatan konten otomatis, AI menjadi tulang punggung transformasi digital industri media.</p><h3>Dampak pada Jurnalisme</h3><p>AI membantu jurnalis dalam riset, fact-checking, dan bahkan menulis berita sederhana seperti laporan keuangan dan hasil pertandingan olahraga.</p><h3>Personalisasi Konten</h3><p>Platform media menggunakan machine learning untuk menampilkan konten yang relevan bagi setiap pengguna, meningkatkan engagement dan waktu kunjungan.</p><h2>Masa Depan AI di Media</h2><p>Ke depannya, kita akan melihat integrasi yang lebih dalam antara AI dan produksi konten, dengan tetap mempertahankan sentuhan manusiawi yang tidak bisa digantikan oleh mesin.</p>",
                    "excerpt": "AI telah mengubah wajah industri media secara fundamental. Dari algoritma rekomendasi hingga jurnalisme otomatis, berikut dampaknya.",
                    "cat": "Teknologi", "tags": ["python", "ai", "web"],
                    "writer": "Admin User", "date": now - timedelta(hours=2),
                    "is_news": True, "is_main_news": True,
                },
                {
                    "title": "Startup Fintech Indonesia Raup Pendanaan Seri B Senilai $50 Juta",
                    "content": "<h2>Pendanaan Terbaru</h2><p>Startup fintech asal Indonesia berhasil mengamankan pendanaan Seri B sebesar $50 juta yang dipimpin oleh investor internasional. Putaran pendanaan ini akan digunakan untuk ekspansi pasar dan pengembangan produk.</p><h3>Rencana Ekspansi</h3><p>Dana segar ini akan dialokasikan untuk memperluas jangkauan layanan ke 20 kota baru di Indonesia dan mempekerjakan 200 talenta teknologi.</p><h3>Inovasi Produk</h3><p>Perusahaan berencana meluncurkan fitur AI-powered financial advisor yang akan membantu pengguna mengelola keuangan pribadi mereka secara lebih cerdas.</p>",
                    "excerpt": "Startup fintech Indonesia mengamankan pendanaan Seri B senilai $50 juta untuk ekspansi pasar dan pengembangan produk inovatif.",
                    "cat": "Bisnis", "tags": ["startup", "fintech", "ai"],
                    "writer": "Admin User", "date": now - timedelta(hours=5),
                    "is_news": True, "is_main_news": True,
                },
                {
                    "title": "Timnas Indonesia Lolos ke Piala Asia: Sebuah Perjalanan Bersejarah",
                    "content": "<h2>Sejarah Baru untuk Sepak Bola Indonesia</h2><p>Tim Nasional Indonesia berhasil memastikan satu tempat di putaran final Piala Asia setelah penampilan gemilang di babak kualifikasi. Ini adalah pertama kalinya dalam 16 tahun Indonesia lolos ke turnamen sepak bola terbesar di Asia.</p><h3>Momen Kunci</h3><p>Kemenangan dramatis 2-1 di laga penentu melawan lawan tangguh menjadi puncak perjuangan panjang Garuda di kualifikasi.</p><h3>Dukungan Publik</h3><p>Kebangkitan sepak bola Indonesia tidak lepas dari dukungan luar biasa para suporter dan transformasi sistem pembinaan usia muda.</p>",
                    "excerpt": "Indonesia memastikan tempat di Piala Asia untuk pertama kalinya dalam 16 tahun setelah kemenangan dramatis di laga kualifikasi.",
                    "cat": "Olahraga", "tags": ["sepakbola"],
                    "writer": "Admin User", "date": now - timedelta(hours=8),
                    "is_news": True, "is_main_news": True,
                },
                {
                    "title": "5 Film Indonesia Paling Dinanti yang Rilis Tahun Ini",
                    "content": "<h2>Industri Film Indonesia Bangkit</h2><p> tahun ini menjadi tahun yang gemilang bagi perfilman Indonesia dengan deretan film berkualitas yang siap menghibur penonton. Dari genre horor hingga drama, berikut lima film yang paling dinanti.</p><h2>Daftar Film</h2><p>Dari sutradara-sutradara ternama hingga pendatang baru berbakat, industri film Indonesia menunjukkan vitalitasnya dengan produksi-produksi yang mendunia.</p>",
                    "excerpt": "Deretan film Indonesia paling dinanti tahun ini, dari horor hingga drama yang siap menghibur.",
                    "cat": "Hiburan", "tags": ["film"],
                    "writer": "Admin User", "date": now - timedelta(hours=24),
                    "is_news": True,
                },
                {
                    "title": "Panduan Hidup Sehat: Tips Menjaga Kebugaran di Era Digital",
                    "content": "<h2>Kebugaran di Era Digital</h2><p>Di tengah kesibukan digital yang semakin tinggi, menjaga kesehatan fisik dan mental menjadi tantangan tersendiri. Berikut panduan praktis untuk tetap bugar.</p><h3>Olahraga Teratur</h3><p>Luangkan waktu minimal 30 menit setiap hari untuk bergerak. Bisa berupa jalan kaki, bersepeda, atau yoga di rumah.</p><h3>Pola Makan Sehat</h3><p>Konsumsi makanan bergizi seimbang dengan porsi yang tepat. Hindari makanan olahan berlebihan.</p><h3>Digital Detox</h3><p>Kurangi waktu layar minimal 1 jam sebelum tidur. Gunakan waktu tersebut untuk membaca buku atau meditasi.</p>",
                    "excerpt": "Panduan lengkap menjaga kesehatan fisik dan mental di tengah gaya hidup digital yang serba cepat.",
                    "cat": "Kesehatan", "tags": ["sehat", "nutrisi"],
                    "writer": "Admin User", "date": now - timedelta(days=1),
                    "is_news": True,
                },
                {
                    "title": "Mobil Listrik Mulai Dominasi Pasar Otomotif Indonesia",
                    "content": "<h2>Revolusi Kendaraan Listrik</h2><p>Mobil listrik semakin populer di Indonesia dengan berbagai merek global dan lokal yang berlomba-lomba menghadirkan produk terjangkau. Pemerintah terus mendorong adopsi kendaraan ramah lingkungan melalui berbagai insentif.</p><h3>Insentif Pemerintah</h3><p>Berbagai kebijakan seperti pengurangan pajak dan pembangunan infrastruktur charging station menjadi katalis pertumbuhan pasar mobil listrik.</p><h3>Pilihan Konsumen</h3><p>Dengan harga yang semakin kompetitif dan jangkauan baterai yang terus meningkat, mobil listrik menjadi pilihan menarik bagi konsumen Indonesia.</p>",
                    "excerpt": "Mobil listrik semakin dominan di pasar Indonesia didorong insentif pemerintah dan harga yang semakin terjangkau.",
                    "cat": "Otomotif", "tags": ["mobil"],
                    "writer": "Admin User", "date": now - timedelta(days=2),
                    "is_news": True,
                },
                {
                    "title": "Revolusi EdTech: Platform Belajar Online Mengubah Wajah Pendidikan",
                    "content": "<h2>Pendidikan di Era Digital</h2><p>Platform pendidikan online atau EdTech telah mengubah cara kita belajar. Dari kursus singkat hingga program gelar penuh, semuanya tersedia dalam genggaman.</p><h3>Akses Pendidikan</h3><p>EdTech membuka akses pendidikan berkualitas bagi siapa saja, di mana saja, tanpa batasan geografis.</p><h3>Beasiswa dan Kesempatan</h3><p>Banyak platform menawarkan beasiswa penuh bagi siswa berprestasi dari latar belakang kurang mampu, menciptakan kesetaraan kesempatan.</p>",
                    "excerpt": "Platform EdTech merevolusi pendidikan dengan akses belajar online berkualitas dan program beasiswa yang inklusif.",
                    "cat": "Pendidikan", "tags": ["edtech", "beasiswa"],
                    "writer": "Admin User", "date": now - timedelta(days=3),
                    "is_news": True,
                },
                {
                    "title": "Tren Fashion 2026: Gaya Minimalis yang Elegan dan Berkelanjutan",
                    "content": "<h2>Fashion Berkelanjutan</h2><p>Tren fashion tahun ini didominasi oleh gaya minimalis yang elegan dengan penekanan pada keberlanjutan. Konsumen semakin sadar akan dampak lingkungan dari industri fashion.</p><h3>Material Ramah Lingkungan</h3><p>Penggunaan bahan daur ulang dan organik menjadi standar baru dalam industri fashion global.</p><h3>Slow Fashion Movement</h3><p>Gerakan slow fashion mendorong konsumen untuk membeli lebih sedikit namun dengan kualitas lebih baik dan tahan lama.</p>",
                    "excerpt": "Tren fashion 2026: gaya minimalis elegan dengan fokus pada keberlanjutan dan material ramah lingkungan.",
                    "cat": "Lifestyle", "tags": ["fashion"],
                    "writer": "Admin User", "date": now - timedelta(days=4),
                    "is_news": True,
                },
            ]
            for i, art in enumerate(articles):
                news = News(
                    title=art["title"],
                    content=art["content"],
                    tagar=", ".join(art["tags"]),
                    date=art["date"],
                    writer=art["writer"],
                    category_id=cats[art["cat"]].id,
                    user_id=admin.id,
                    author=admin,
                    is_visible=True,
                    is_news=art.get("is_news", True),
                    is_main_news=art.get("is_main_news", False),
                    meta_description=art["excerpt"],
                )
                db.session.add(news)
                db.session.flush()
                # Attach tags
                for slug in art["tags"]:
                    if slug in tag_map:
                        db.session.execute(news_tags.insert().values(news_id=news.id, tag_id=tag_map[slug].id))
            print(f"  + {len(articles)} articles")
        else:
            print("  ~ articles exist")

        # ═══════════════════════════════════════════════════════════════
        # COMMENTS
        # ═══════════════════════════════════════════════════════════════
        if Comment.query.count() == 0:
            first_news = News.query.order_by(News.date.desc()).first()
            if first_news:
                c1 = Comment(
                    content="Artikel yang sangat informatif! Saya setuju bahwa AI akan terus mengubah industri media. Terima kasih untuk wawasannya.",
                    author_name="Budi Santoso", author_email="budi@example.com",
                    status=CommentStatus.APPROVED, news_id=first_news.id,
                )
                db.session.add(c1)
                db.session.flush()
                r1 = Comment(
                    content="Terima kasih Budi! Senang artikelnya bermanfaat.",
                    author_name="Admin User", author_email="admin@example.com",
                    status=CommentStatus.APPROVED, news_id=first_news.id, parent_id=c1.id,
                )
                db.session.add(r1)
                db.session.flush()
                db.session.add(Comment(
                    content="Menarik, tapi saya rasa masih banyak tantangan yang harus diatasi terutama dalam hal etika penggunaan AI.",
                    author_name="Siti Rahayu", author_email="siti@example.com",
                    status=CommentStatus.PENDING, news_id=first_news.id,
                ))
                print("  + demo comments")
        else:
            print("  ~ comments exist")

        # ═══════════════════════════════════════════════════════════════
        # PAGES
        # ═══════════════════════════════════════════════════════════════
        if Page.query.count() == 0:
            for pdata in [
                {"title":"Tentang Kami","slug":"tentang-kami","content":"<h2>Tentang LilyOpenCMS</h2><p>LilyOpenCMS adalah sistem manajemen konten modern berbasis Flask dan PostgreSQL. Dirancang untuk berbagai kebutuhan — dari blog pribadi hingga portal berita nasional dan perusahaan.</p><p>Dibangun dengan filosofi modular, keamanan tinggi, dan performa optimal.</p>","excerpt":"Tentang LilyOpenCMS","template":"default","is_published":True,"show_in_menu":True,"menu_order":1,"meta_title":"Tentang Kami — LilyOpenCMS","meta_description":"Pelajari lebih lanjut tentang LilyOpenCMS."},
                {"title":"Kebijakan Privasi","slug":"kebijakan-privasi","content":"<h2>Kebijakan Privasi</h2><p>Kami menghargai privasi Anda. Halaman ini menjelaskan bagaimana kami mengumpulkan, melindungi, dan menggunakan data pribadi Anda.</p>","excerpt":"Kebijakan privasi","template":"default","is_published":True,"show_in_menu":True,"menu_order":2,"meta_title":"Kebijakan Privasi — LilyOpenCMS","meta_description":"Kebijakan privasi LilyOpenCMS."},
                {"title":"Syarat & Ketentuan","slug":"syarat-ketentuan","content":"<h2>Syarat & Ketentuan</h2><p>Dengan menggunakan LilyOpenCMS, Anda menyetujui syarat dan ketentuan berikut.</p>","excerpt":"Syarat dan ketentuan","template":"default","is_published":True,"show_in_menu":True,"menu_order":3,"meta_title":"Syarat & Ketentuan — LilyOpenCMS","meta_description":"Syarat dan ketentuan penggunaan LilyOpenCMS."},
                {"title":"Layanan","slug":"layanan","content":"<h2>Layanan Kami</h2><ul><li>Blog Pribadi</li><li>Portal Berita</li><li>Profil Perusahaan</li><li>Toko Online</li></ul>","excerpt":"Layanan LilyOpenCMS","template":"default","is_published":True,"show_in_menu":True,"menu_order":4,"meta_title":"Layanan — LilyOpenCMS","meta_description":"Layanan manajemen konten LilyOpenCMS."},
            ]:
                p = Page(**pdata, author_id=admin.id if admin else None)
                db.session.add(p)
            print("  + 4 pages")
        else:
            print("  ~ pages exist")

        # ═══════════════════════════════════════════════════════════════
        # NAVIGATION
        # ═══════════════════════════════════════════════════════════════
        if NavigationLink.query.count() == 0:
            nav_links = [
                ("Beranda", "/", "navbar", 1),
                ("Berita", "/search", "navbar", 2),
                ("Teknologi", "/search?category=Teknologi", "navbar", 3),
                ("Bisnis", "/search?category=Bisnis", "navbar", 4),
                ("Olahraga", "/search?category=Olahraga", "navbar", 5),
                ("Kontak", "/page/tentang-kami", "navbar", 6),
                ("Tentang", "/page/tentang-kami", "footer", 1),
                ("Kebijakan Privasi", "/page/kebijakan-privasi", "footer", 2),
                ("Syarat & Ketentuan", "/page/syarat-ketentuan", "footer", 3),
                ("Layanan", "/page/layanan", "footer", 4),
            ]
            for name, url, loc, order in nav_links:
                db.session.add(NavigationLink(name=name, url=url, location=loc, order=order, is_active=True))
            print("  + 10 navigation links")
        else:
            print("  ~ nav links exist")

        # ═══════════════════════════════════════════════════════════════
        # SOCIAL MEDIA
        # ═══════════════════════════════════════════════════════════════
        if SocialMedia.query.count() == 0:
            for name, url in [
                ("Twitter", "https://twitter.com/lilyopencms"),
                ("Facebook", "https://facebook.com/lilyopencms"),
                ("Instagram", "https://instagram.com/lilyopencms"),
                ("YouTube", "https://youtube.com/@lilyopencms"),
                ("GitHub", "https://github.com/1999AZZAR"),
            ]:
                db.session.add(SocialMedia(name=name, url=url, created_by=admin.id if admin else None))
            print("  + 5 social media")
        else:
            print("  ~ social media exist")

        # ═══════════════════════════════════════════════════════════════
        # TEAM MEMBERS
        # ═══════════════════════════════════════════════════════════════
        if TeamMember.query.count() == 0:
            for name, title, group, order in [
                ("Azzar Budiyanto", "Founder & CEO", "leadership", 1),
                ("Admin User", "Editor in Chief", "editorial", 2),
                ("Budi Santoso", "Senior Journalist", "news", 3),
                ("Siti Rahayu", "Content Writer", "news", 4),
                ("Rina Wijaya", "Video Producer", "video", 5),
            ]:
                db.session.add(TeamMember(name=name, title=title, group=group, member_order=order, is_active=True))
            print("  + 5 team members")
        else:
            print("  ~ team exists")

        # ═══════════════════════════════════════════════════════════════
        # CONTACT DETAILS
        # ═══════════════════════════════════════════════════════════════
        if ContactDetail.query.count() == 0:
            for title, content, icon, link, order in [
                ("Email", "hello@lilyopencms.com", "envelope", "mailto:hello@lilyopencms.com", 1),
                ("Telepon", "+62 812 3456 7890", "phone", "tel:+6281234567890", 2),
                ("Alamat", "Jl. Merdeka No. 123, Jakarta Pusat", "location-dot", None, 3),
                ("Jam Kerja", "Senin - Jumat, 09:00 - 17:00 WIB", "clock", None, 4),
            ]:
                db.session.add(ContactDetail(title=title, content=content, icon_class=icon, link=link, section_order=order, is_active=True))
            print("  + 4 contact details")
        else:
            print("  ~ contacts exist")

        db.session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    seed()
