document.addEventListener('DOMContentLoaded', function() {
    // =======================================================
    // BAGIAN 1: LOGIKA SIDEBAR NAVIGASI
    // =======================================================
    
    // Definisi elemen-elemen sidebar
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('dashboardSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');
    const mainContent = document.querySelector('.dashboard-content');

    // Fungsi terpusat untuk menutup sidebar
    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('active');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Event listener untuk tombol hamburger (buka sidebar)
    if (mobileMenuToggle && sidebar && sidebarOverlay) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    // Event listener untuk tombol 'X' di dalam sidebar
    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }

    // Event listener untuk area gelap di belakang sidebar
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Event listener untuk menutup sidebar saat konten utama diklik
    if (mainContent) {
        mainContent.addEventListener('click', function() {
            if (sidebar && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });
    }

    // Event listener untuk tombol Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });

    // Event listener untuk mengubah ukuran window
    window.addEventListener('resize', function() {
        // Breakpoint harus cocok dengan CSS Anda (768px)
        if (window.innerWidth > 768) { 
            closeSidebar();
        }
    });

    // Skrip untuk menandai nav-link yang aktif
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // =======================================================
    // BAGIAN 2: LOGIKA UNTUK MODAL AI RESUME REVIEWER
    // =======================================================
    
    const resumeModal = document.getElementById('resumeReviewerModal');
    const openBtn = document.getElementById('openResumeReviewerBtn');
    const reviewBtn = document.getElementById('review-cv-btn');
    const cvInput = document.getElementById('cv-input-text');
    const feedbackOutput = document.getElementById('feedback-output');

    if (openBtn && resumeModal) {
        // Event listener untuk membuka modal
        openBtn.addEventListener('click', () => resumeModal.classList.add('visible'));

        // Event listener untuk menutup modal (klik 'X' atau di luar)
        resumeModal.addEventListener('click', (e) => {
            if (e.target === resumeModal || e.target.closest('.modal-close-btn')) {
                resumeModal.classList.remove('visible');
            }
        });

        // Event listener untuk tombol "Dapatkan Feedback AI"
        reviewBtn.addEventListener('click', async () => {
            const cv_text = cvInput.value.trim();
            if (!cv_text) {
                alert('Teks CV tidak boleh kosong.');
                return;
            }

            // Tampilkan status loading
            reviewBtn.disabled = true;
            reviewBtn.textContent = 'AI sedang menganalisis...';
            feedbackOutput.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';

            try {
                // Panggil API backend
                const response = await fetch('/api/ai/review-resume', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cv_text: cv_text })
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Terjadi kesalahan.');

                // Tampilkan hasil feedback yang sudah di-render sebagai Markdown
                if (window.marked) {
                    feedbackOutput.innerHTML = marked.parse(data.feedback);
                } else {
                    // Fallback jika marked.js tidak termuat
                    feedbackOutput.textContent = data.feedback;
                }

            } catch (error) {
                feedbackOutput.innerHTML = `<p style="color: var(--accent-red);">Gagal mendapatkan feedback: ${error.message}</p>`;
            } finally {
                // Kembalikan tombol ke keadaan normal
                reviewBtn.disabled = false;
                reviewBtn.textContent = 'Dapatkan Feedback AI';
            }
        });
    }
});