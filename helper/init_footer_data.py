import sys
import os

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

from models import db, PrivacyPolicy, MediaGuideline, VisiMisi, Penyangkalan, PedomanHak
from datetime import datetime

# Import app from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app


def init_privacy_policy():
    # Clear existing data
    PrivacyPolicy.query.delete()

    privacy_sections = [
        {
            "title": "Jenis Informasi yang Kami Kumpulkan",
            "content": """Kami mengumpulkan dua jenis informasi utama sebagai berikut:
● Informasi Pribadi:
- Informasi yang Anda berikan secara sukarela, seperti nama, alamat email, nomor telepon, alamat rumah, dan data lainnya saat Anda mendaftar, berinteraksi dengan layanan kami, mengirimkan komentar, berpartisipasi dalam survei, atau mendaftar untuk menerima pembaruan atau newsletter dari kami.
● Informasi Teknologi:
- Informasi yang dikumpulkan secara otomatis, termasuk alamat IP, jenis perangkat yang digunakan, informasi browser, data lokasi, serta aktivitas Anda di situs web kami. Kami menggunakan teknologi seperti cookies untuk mengumpulkan informasi ini.""",
            "section_order": 1,
        },
        {
            "title": "Tujuan Pengumpulan Data",
            "content": """Kami mengumpulkan data pribadi Anda untuk beberapa tujuan, di antaranya:
● Memberikan Layanan: Untuk memberikan konten, layanan, dan informasi yang relevan bagi Anda, serta memastikan fungsionalitas dan keamanan situs web kami.
● Personalisasi Pengalaman: Untuk menyesuaikan pengalaman Anda di situs kami dengan preferensi yang Anda pilih dan meningkatkan interaksi Anda.
● Komunikasi: Mengirimkan pembaruan, informasi penting, dan materi pemasaran atau promosi jika Anda memilih untuk menerima komunikasi tersebut.
● Analisis dan Peningkatan Layanan: Menggunakan data analitik untuk memahami bagaimana pengunjung berinteraksi dengan situs kami dan meningkatkan kualitas konten serta layanan yang kami tawarkan.
● Kepatuhan Hukum: Untuk mematuhi kewajiban hukum dan peraturan yang berlaku.""",
            "section_order": 2,
        },
        {
            "title": "Kebijakan Cookie",
            "content": """LilyOpenCMS menggunakan cookies untuk meningkatkan pengalaman Anda saat mengunjungi situs kami. Cookies adalah file kecil yang disimpan di perangkat Anda dan digunakan untuk mengingat preferensi pengguna serta aktivitas yang Anda lakukan di situs kami.

Jenis cookie yang kami gunakan meliputi:
● Cookies Fungsional: Untuk mengingat preferensi pengguna dan meningkatkan pengalaman penggunaan situs.
● Cookies Analitik: Untuk menganalisis cara pengunjung berinteraksi dengan situs kami dan mengidentifikasi area yang perlu ditingkatkan.
● Cookies Iklan: Untuk menayangkan iklan yang relevan dengan preferensi Anda.""",
            "section_order": 3,
        },
        {
            "title": "Penggunaan dan Pembagian Data Pribadi",
            "content": """Kami berkomitmen untuk tidak menjual, menyewakan, atau memberikan data pribadi Anda kepada pihak ketiga tanpa persetujuan Anda, kecuali jika diperlukan untuk tujuan tertentu berikut:
● Penyedia Layanan Pihak Ketiga: Kami dapat bekerja sama dengan penyedia layanan yang membantu kami mengelola situs web, analitik, atau komunikasi pemasaran, yang mungkin memerlukan akses ke data pribadi Anda.
● Kepatuhan Hukum: Kami dapat mengungkapkan data pribadi Anda jika diwajibkan oleh hukum atau jika diperlukan untuk melindungi hak-hak kami, keamanan situs web, atau untuk memenuhi kewajiban hukum.""",
            "section_order": 4,
        },
        {
            "title": "Hak Pengguna terhadap Data Pribadi",
            "content": """Sesuai dengan regulasi yang berlaku, Anda memiliki hak-hak berikut terkait data pribadi Anda:
● Hak untuk mengakses: Anda berhak meminta salinan informasi pribadi yang kami miliki tentang Anda.
● Hak untuk memperbaiki: Anda berhak meminta kami untuk memperbaiki data pribadi yang tidak akurat atau tidak lengkap.
● Hak untuk menghapus: Anda dapat meminta kami untuk menghapus data pribadi Anda dari sistem kami.
● Hak untuk menolak atau membatasi pengolahan: Anda dapat memilih untuk menolak atau membatasi penggunaan data pribadi Anda untuk tujuan tertentu.""",
            "section_order": 5,
        },
    ]

    for section in privacy_sections:
        policy = PrivacyPolicy(
            title=section["title"],
            content=section["content"],
            section_order=section["section_order"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(policy)


def init_media_guidelines():
    # Clear existing data
    MediaGuideline.query.delete()

    guideline_sections = [
        {
            "title": "Ruang Lingkup",
            "content": """Media siber adalah segala bentuk media yang menggunakan wahana internet dan melaksanakan kegiatan jurnalistik, serta memenuhi persyaratan Undang-Undang Pers dan Standar Perusahaan Pers yang ditetapkan Dewan Pers.

Isi Buatan Pengguna (User Generated Content) adalah segala isi yang dibuat dan dipublikasikan oleh pengguna media siber, antara lain artikel, gambar, komentar, suara, video, dan berbagai bentuk unggahan yang melekat pada media siber, seperti blog, forum, komentar pembaca atau pemirsa, dan bentuk lain.""",
            "section_order": 1,
        },
        {
            "title": "Verifikasi dan Keberimbangan Berita",
            "content": """Setiap berita harus melalui proses verifikasi. Berita yang dapat merugikan pihak lain memerlukan verifikasi lebih lanjut untuk memenuhi prinsip akurasi dan keberimbangan.

Ketentuan ini dapat dikecualikan dengan syarat-syarat berikut:
● Berita mengandung kepentingan publik yang bersifat mendesak.
● Sumber berita pertama adalah sumber yang jelas, kredibel, dan kompeten.
● Subjek berita yang harus dikonfirmasi tidak dapat ditemukan atau diwawancarai.
● Media harus memberikan penjelasan bahwa berita tersebut masih memerlukan verifikasi lebih lanjut.""",
            "section_order": 2,
        },
        {
            "title": "Isi Buatan Pengguna",
            "content": """Media siber wajib mencantumkan syarat dan ketentuan mengenai Isi Buatan Pengguna yang tidak bertentangan dengan Undang-Undang No. 40 tahun 1999 tentang Pers dan Kode Etik Jurnalistik.

Media siber mewajibkan setiap pengguna untuk melakukan registrasi keanggotaan dan melakukan proses log-in sebelum mempublikasikan Isi Buatan Pengguna.

Pengguna harus memberikan persetujuan tertulis bahwa isi yang dipublikasikan tidak mengandung:
● Kebohongan, fitnah, sadisme, atau pornografi.
● Prasangka dan kebencian terkait SARA, serta menganjurkan kekerasan.
● Diskriminasi berdasarkan jenis kelamin, bahasa, atau merendahkan martabat orang lemah, miskin, cacat, atau sakit.""",
            "section_order": 3,
        },
        {
            "title": "Ralat, Koreksi, dan Hak Jawab",
            "content": """Ralat, koreksi, dan hak jawab mengacu pada Undang-Undang Pers, Kode Etik Jurnalistik, dan Pedoman Hak Jawab yang ditetapkan Dewan Pers.

● Ralat, koreksi, dan hak jawab harus ditautkan pada berita yang diralat, dikoreksi, atau yang diberi hak jawab.
● Di setiap berita ralat, koreksi, dan hak jawab wajib dicantumkan waktu pemuatan.
● Media yang tidak melakukan koreksi terhadap berita yang telah dikoreksi oleh media asal akan bertanggung jawab penuh atas segala akibat hukum.""",
            "section_order": 4,
        },
        {
            "title": "Pencabutan Berita",
            "content": """Berita yang sudah dipublikasikan tidak dapat dicabut karena alasan penyensoran luar redaksi, kecuali terkait masalah SARA, kesusilaan, masa depan anak, pengalaman traumatik korban, atau alasan khusus lainnya yang ditetapkan Dewan Pers.

● Media siber lain wajib mengikuti pencabutan kutipan berita yang telah dicabut oleh media asal.
● Pencabutan berita wajib disertai alasan yang jelas dan diumumkan kepada publik.""",
            "section_order": 5,
        },
    ]

    for section in guideline_sections:
        guideline = MediaGuideline(
            title=section["title"],
            content=section["content"],
            section_order=section["section_order"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(guideline)


def init_visi_misi():
    # Clear existing data
    VisiMisi.query.delete()

    sections = [
        {
            "title": "Visi",
            "content": "Menjadi platform berita siber terpercaya yang memberikan informasi akurat, independen, dan bermanfaat bagi masyarakat.",
            "section_order": 1,
        },
        {
            "title": "Misi",
            "content": """1. Menyajikan Berita Akurat dan Berimbang: Menghasilkan konten jurnalistik yang terverifikasi, mendalam, dan mematuhi kode etik jurnalistik serta prinsip keberimbangan.
2. Mendorong Literasi Media: Mengedukasi pembaca tentang pentingnya informasi yang kredibel dan cara mengidentifikasi berita palsu atau misinformasi.
3. Menjadi Platform Diskusi Publik: Menyediakan ruang bagi masyarakat untuk berdiskusi secara sehat dan konstruktif mengenai isu-isu penting.
4. Inovasi Teknologi: Memanfaatkan perkembangan teknologi terkini untuk menyajikan berita dengan format yang menarik dan mudah diakses oleh berbagai kalangan.
5. Menjunjung Tinggi Independensi: Menjaga independensi redaksi dari tekanan politik, ekonomi, atau kelompok kepentingan lainnya untuk memastikan objektivitas pemberitaan.""",
            "section_order": 2,
        },
    ]
    for sec in sections:
        record = VisiMisi(
            title=sec["title"],
            content=sec["content"],
            section_order=sec["section_order"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(record)


def init_penyangkalan():
    # Clear existing data
    Penyangkalan.query.delete()

    sections = [
        {
            "title": "Tanggung Jawab Konten",
            "content": "Semua informasi, artikel, berita, dan opini yang dipublikasikan di LilyOpenCMS ditulis oleh tim redaksi atau kontributor terdaftar. Meskipun kami berusaha menyajikan informasi seakurat mungkin, konten tersebut dimaksudkan sebagai informasi umum dan tidak dapat dianggap sebagai nasihat profesional (hukum, keuangan, medis, dll.). Tanggung jawab penuh atas penggunaan informasi ada pada pembaca.",
            "section_order": 1,
        },
        {
            "title": "Konten Buatan Pengguna (User Generated Content)",
            "content": "LilyOpenCMS menyediakan fitur interaktif seperti kolom komentar. Kami tidak bertanggung jawab atas isi komentar, opini, atau unggahan lain yang dibuat oleh pengguna. Komentar sepenuhnya menjadi tanggung jawab individu yang mempublikasikannya. Namun, kami berhak untuk menghapus atau menyunting konten pengguna yang melanggar pedoman komunitas, hukum, atau etika.",
            "section_order": 2,
        },
        {
            "title": "Tautan Eksternal",
            "content": "Situs kami mungkin berisi tautan ke situs web pihak ketiga. Tautan ini disediakan untuk kemudahan referensi. Kami tidak memiliki kontrol atas konten, kebijakan privasi, atau praktik situs web eksternal tersebut dan tidak bertanggung jawab atas kerugian atau kerusakan yang mungkin timbul dari penggunaannya.",
            "section_order": 3,
        },
        {
            "title": "Akurasi dan Perubahan Informasi",
            "content": "Kami berupaya menjaga informasi tetap akurat dan terkini. Namun, informasi dapat berubah seiring waktu. LilyOpenCMS tidak menjamin kelengkapan, keandalan, atau keakuratan mutlak dari semua materi yang disajikan. Kami berhak mengubah atau menghapus konten kapan saja tanpa pemberitahuan sebelumnya.",
            "section_order": 1,
        }
    ]

    for sec in sections:
        record = Penyangkalan(
            title=sec["title"],
            content=sec["content"],
            section_order=sec["section_order"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(record)


def init_pedoman_hak():
    # Clear existing data
    PedomanHak.query.delete()

    sections = [
        {
            "title": "Dasar Hukum dan Prinsip",
            "content": "Pelaksanaan hak jawab, hak koreksi, dan kewajiban ralat di LilyOpenCMS mengacu pada Undang-Undang No. 40 Tahun 1999 tentang Pers, Kode Etik Jurnalistik, dan Pedoman Hak Jawab yang ditetapkan oleh Dewan Pers. Kami berkomitmen untuk menghormati hak individu atau kelompok yang merasa dirugikan oleh pemberitaan.",
            "section_order": 1,
        },
        {
            "title": "Prosedur Pengajuan Hak Jawab",
            "content": """Pihak yang merasa dirugikan oleh pemberitaan dapat mengajukan hak jawab secara tertulis kepada redaksi LilyOpenCMS melalui alamat email atau kontak resmi yang tercantum di situs.
● Surat pengajuan harus jelas menyebutkan berita yang dimaksud (judul, tanggal publikasi, tautan jika ada) dan bagian mana yang dianggap tidak akurat atau merugikan.
● Sertakan data atau fakta pendukung untuk mengklarifikasi informasi.
● Cantumkan identitas pengirim yang jelas dan kontak yang dapat dihubungi.""",
            "section_order": 2,
        },
        {
            "title": "Kewajiban Media",
            "content": """LilyOpenCMS wajib memuat hak jawab secara proporsional pada berita terkait atau sebagai berita tersendiri sesegera mungkin setelah verifikasi.
● Hak jawab dimuat tanpa pemotongan yang mengubah substansi dan tanpa tambahan komentar redaksi yang bersifat polemik.
● Jika berita yang dikoreksi dikutip oleh media lain, media tersebut juga diimbau untuk melakukan koreksi serupa.
● Pelaksanaan hak jawab tidak menghilangkan hak hukum pihak yang dirugikan jika merasa perlu menempuh jalur lain.""",
            "section_order": 3,
        },
        {
            "title": "Ralat dan Koreksi",
            "content": "Redaksi LilyOpenCMS secara proaktif akan melakukan ralat atau koreksi jika menemukan kesalahan faktual dalam pemberitaan, meskipun tanpa ada permintaan hak jawab. Ralat atau koreksi akan dicantumkan secara jelas pada berita yang diperbaiki.",
            "section_order": 1,
        }
    ]

    for sec in sections:
        record = PedomanHak(
            title=sec["title"],
            content=sec["content"],
            section_order=sec["section_order"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(record)


def init_footer_data():
    print("📄 LilyOpenCMS Footer Data Initializer")
    print("=" * 50)
    
    try:
        # Initialize both sets of data
        print("Initializing privacy policy...")
        init_privacy_policy()
        print("Initializing media guidelines...")
        init_media_guidelines()
        print("Initializing visi misi...")
        init_visi_misi()
        print("Initializing penyangkalan...")
        init_penyangkalan()
        print("Initializing pedoman hak...")
        init_pedoman_hak()

        # Commit all changes
        db.session.commit()
        print("-" * 50)
        print("✅ Successfully initialized all footer data!")
        print("   - Privacy Policy")
        print("   - Media Guidelines") 
        print("   - Visi Misi")
        print("   - Penyangkalan")
        print("   - Pedoman Hak")

    except Exception as e:
        print(f"❌ Error initializing data: {str(e)}")
        db.session.rollback()


if __name__ == "__main__":
    with app.app_context():  # Set up the application context
        init_footer_data()  # Call your function within the context
