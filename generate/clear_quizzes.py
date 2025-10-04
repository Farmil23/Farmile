from app import create_app, db
from app.models import Lesson

# Daftar judul lesson yang kuisnya ingin Anda hapus
lessons_to_clear_quiz = [
    "Pengenalan Jaringan Komputer",
    "Model Referensi OSI & TCP/IP",
    "Perangkat Keras Jaringan (Router, Switch, Hub)",
    "Topologi Jaringan (Bus, Star, Ring, Mesh)",
    "Media Transmisi (Kabel Tembaga, Fiber Optik, Nirkabel)",
    "Pengalamatan IP (IPv4 & Subnetting)",
    "Cara Kerja Switch Layer 2",
    "Virtual LANs (VLANs)",
    "Trunking (802.1Q)",
    "Spanning Tree Protocol (STP)",
    "EtherChannel",
    "Konfigurasi Dasar Switch Cisco",
    "Cara Kerja Router & Routing Table",
    "Static Routing",
    "Dynamic Routing Protocols (RIP, EIGRP, OSPF)",
    "Access Control Lists (ACLs)",
    "Network Address Translation (NAT)",
    "Pengenalan Wide Area Networks (WAN)",
    "Domain Name System (DNS)",
    "Dynamic Host Configuration Protocol (DHCP)",
    "File Transfer Protocol (FTP) & Trivial FTP (TFTP)",
    "Simple Network Management Protocol (SNMP)",
    "Network Time Protocol (NTP)",
    "Syslog",
    "Standar Wi-Fi (802.11a/b/g/n/ac/ax)",
    "Komponen Jaringan Nirkabel (AP, WLC)",
    "Keamanan Nirkabel (WEP, WPA, WPA2, WPA3)",
    "Site Survey Nirkabel",
    "Troubleshooting Masalah Nirkabel",
    "Pengenalan Jaringan Seluler (4G/5G)",
    "Ancaman Keamanan Jaringan Umum",
    "Keamanan Switch (Port Security, DHCP Snooping)",
    "Virtual Private Networks (VPN) Lanjutan (IPSec & SSL)",
    "Next-Generation Firewalls (NGFW) & Unified Threat Management (UTM)",
    "Pengenalan SIEM (Security Information and Event Management)",
    "Network Access Control (NAC)",
    "Border Gateway Protocol (BGP)",
    "Multiprotocol Label Switching (MPLS)",
    "Quality of Service (QoS)",
    "Desain Jaringan Hierarkis (Core, Distribution, Access)",
    "IPv6",
    "Software-Defined Networking (SDN)",
    "Pengenalan Jaringan di Cloud (AWS, Azure, GCP)",
    "Amazon VPC & Subnets",
    "Azure VNet & Subnets",
    "AWS Security Groups & Network ACLs",
    "Menghubungkan Jaringan On-premise ke Cloud (VPN & Direct Connect)",
    "Load Balancing di Cloud",
    "Mengapa Otomatisasi Jaringan Penting?",
    "Dasar-dasar Python untuk Otomatisasi Jaringan",
    "Berinteraksi dengan Perangkat Jaringan via SSH (Paramiko/Netmiko)",
    "Parsing Data Konfigurasi & Operasional",
    "Pengenalan Ansible untuk Otomatisasi Jaringan",
    "REST APIs & Postman untuk Perangkat Jaringan Modern",
    "Sertifikasi Jaringan (CCNA, JNCIA, CompTIA Network+)",
    "Troubleshooting Jaringan: Metodologi Top-Down & Bottom-Up",
    "Menggunakan Alat Diagnostik Jaringan (ping, traceroute, nslookup)",
    "Dokumentasi Jaringan",
    "Wawancara Teknis Insinyur Jaringan",
    "Tren Masa Depan: 5G, IoT, & Edge Computing"
]

app = create_app()

with app.app_context():
    print("Mencari lesson untuk menghapus konten kuis...")
    
    # Cari lesson berdasarkan judul di dalam daftar
    lessons = Lesson.query.filter(Lesson.title.in_(lessons_to_clear_quiz)).all()
    
    if not lessons:
        print("Tidak ada lesson yang ditemukan dengan judul tersebut.")
    else:
        print(f"Ditemukan {len(lessons)} lesson untuk dihapus konten kuisnya:")
        for lesson in lessons:
            print(f"- Menghapus kuis dari: {lesson.title}")
            lesson.quiz = None  # Setel konten kuis menjadi kosong (None)
        
        db.session.commit()
        print("\n✅ Konten kuis berhasil dihapus dari database.")