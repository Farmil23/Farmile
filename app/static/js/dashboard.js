document.addEventListener('DOMContentLoaded', function() {
    // Skrip lama Anda untuk sidebar mobile (TIDAK DIHAPUS)
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('dashboardSidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose'); // Mungkin null, perlu dicek

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('active');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (mobileMenuToggle && sidebar && sidebarOverlay) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('active')) {
            closeSidebar();
        }
    });
    window.addEventListener('resize', function() {
        if (window.innerWidth > 1024) {
            closeSidebar();
        }
    });

    // Skrip lama Anda untuk menandai nav-link aktif (TIDAK DIHAPUS)
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // --- LOGIKA BARU UNTUK MODAL REVIEWER ---
    const resumeModal = document.getElementById('resumeReviewerModal');
    const openBtn = document.getElementById('openResumeReviewerBtn');
    const reviewBtn = document.getElementById('review-cv-btn');
    const cvInput = document.getElementById('cv-input-text');
    const feedbackOutput = document.getElementById('feedback-output');

    if (openBtn && resumeModal) {
        openBtn.addEventListener('click', () => resumeModal.classList.add('visible'));
        resumeModal.addEventListener('click', (e) => {
            if (e.target === resumeModal || e.target.closest('.modal-close-btn')) {
                resumeModal.classList.remove('visible');
            }
        });

        reviewBtn.addEventListener('click', async () => {
            const cv_text = cvInput.value.trim();
            if (!cv_text) {
                alert('Teks CV tidak boleh kosong.');
                return;
            }

            reviewBtn.disabled = true;
            reviewBtn.textContent = 'AI sedang menganalisis...';
            feedbackOutput.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';

            try {
                const response = await fetch('/api/ai/review-resume', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cv_text: cv_text })
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Terjadi kesalahan.');

                if (window.marked) {
                    feedbackOutput.innerHTML = marked.parse(data.feedback);
                } else {
                    feedbackOutput.textContent = data.feedback;
                }

            } catch (error) {
                feedbackOutput.innerHTML = `<p style="color: var(--accent-red);">Gagal mendapatkan feedback: ${error.message}</p>`;
            } finally {
                reviewBtn.disabled = false;
                reviewBtn.textContent = 'Dapatkan Feedback AI';
            }
        });
    }
});
