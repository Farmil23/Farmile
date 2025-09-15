from app import create_app, db
from app.models import Lesson

# Daftar judul lesson yang kontennya ingin Anda hapus

lessons_to_clear = [
    "Membangun Brand Pribadi sebagai DevOps Engineer",
    "Prinsip Dasar Keamanan Informasi (CIA Triad)",
    "Konsep Jaringan Komputer (OSI & TCP/IP Model)",
    "Protokol Jaringan Umum (HTTP, DNS, FTP, SMTP)",
    "Dasar-dasar Sistem Operasi Linux",
    "Perintah Dasar Linux untuk Keamanan",
    "Pengenalan Virtualisasi & Containers",
    "Pengenalan Kriptografi",
    "Enkripsi Simetris (AES)",
    "Enkripsi Asimetris (RSA) & Public Key Infrastructure (PKI)",
    "Fungsi Hash (SHA-256) & Integritas Data",
    "Digital Signatures & Certificates (SSL/TLS)",
    "Steganografi",
    "Firewall & Tipe-tipenya",
    "Intrusion Detection Systems (IDS) & Intrusion Prevention Systems (IPS)",
    "Virtual Private Networks (VPN)",
    "Network Reconnaissance & Scanning (Nmap)",
    "Network Hardening",
    "Analisis Log Jaringan",
    "Metodologi Penetration Testing",
    "Information Gathering (Passive & Active)",
    "Vulnerability Scanning (Nessus/OpenVAS)",
    "Eksploitasi dengan Metasploit Framework",
    "Password Cracking",
    "Web Application Hacking (OWASP Top 10)",
    "SQL Injection (SQLi)",
    "Cross-Site Scripting (XSS)",
    "Cross-Site Request Forgery (CSRF)",
    "Insecure Deserialization",
    "Security Misconfigurations",
    "Secure Software Development Lifecycle (SSDLC)",
    "Tipe-tipe Malware (Virus, Worm, Trojan, Ransomware)",
    "Analisis Malware Statis",
    "Analisis Malware Dinamis (Sandbox)",
    "Dasar-dasar Reverse Engineering",
    "Pengenalan Assembly Language",
    "Menggunakan Disassembler & Debugger (Ghidra, GDB)",
    "Proses Digital Forensics",
    "Forensik Memori (Volatility)",
    "Forensik Disk (Autopsy)",
    "Incident Response Lifecycle",
    "Threat Intelligence",
    "Membuat Laporan Forensik",
    "Model Layanan Cloud (IaaS, PaaS, SaaS)",
    "Model Tanggung Jawab Bersama (Shared Responsibility Model)",
    "Keamanan AWS: IAM, VPC, Security Groups",
    "Keamanan Azure: Azure AD, NSGs",
    "Keamanan GCP: Cloud IAM, VPC",
    "Container Security di Cloud (Kubernetes Security)",
    "Python untuk Keamanan Siber",
    "Interaksi dengan API untuk Keamanan",
    "Menulis Skrip Nmap dengan Python",
    "Security Orchestration, Automation, and Response (SOAR)",
    "Pengenalan SIEM (Security Information and Event Management)",
    "Menulis Aturan Deteksi (Snort, YARA)",
    "Sertifikasi Keamanan (CompTIA Security+, CEH, OSCP)",
    "Peran-peran dalam Keamanan Siber",
    "Membangun Lab Keamanan Pribadi",
    "Wawancara Teknis Keamanan Siber",
    "Hukum & Etika dalam Keamanan Siber",
    "Menulis Laporan Penetration Testing"
    
]

app = create_app()

with app.app_context():
    # Cari lesson berdasarkan judul di dalam daftar
    lessons = Lesson.query.filter(Lesson.title.in_(lessons_to_clear)).all()
    
    if not lessons:
        print("Tidak ada lesson yang ditemukan dengan judul tersebut.")
    else:
        print(f"Ditemukan {len(lessons)} lesson untuk dihapus kontennya:")
        for lesson in lessons:
            print(f"- Menghapus konten dari: {lesson.title}")
            lesson.content = None  # Setel konten menjadi kosong (None)
        
        db.session.commit()
        print("\n✅ Konten berhasil dihapus dari database.")