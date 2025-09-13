// File: app/static/js/ai_resume_pro.js

document.addEventListener('DOMContentLoaded', () => {
    // Referensi Elemen
    const uploadInput = document.getElementById('pdf-upload-input');
    const uploadBox = document.getElementById('upload-box');
    const reviewContainer = document.getElementById('review-container');
    const templateSelectionBox = document.getElementById('template-selection-box');
    const resumePreviewBox = document.getElementById('resume-preview-box');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resumeContentEl = document.getElementById('resume-content-text');
    const feedbackContentEl = document.getElementById('feedback-content');
    const mainActions = document.getElementById('main-actions');
    const mainTitle = document.getElementById('main-title');
    const newAnalysisBtn = document.getElementById('new-analysis-btn');

    // Referensi Elemen untuk Job Matcher
    const jobMatcherPanel = document.getElementById('job-matcher-panel');
    const jobDescriptionInput = document.getElementById('job-description-input');
    const matchJobBtn = document.getElementById('match-job-btn');
    const savedAnalysesList = document.getElementById('saved-analyses-list');

    let currentResumeId = null;
    let currentResumeData = null;

    const showState = (state) => {
        uploadBox.style.display = 'none';
        reviewContainer.style.display = 'none';
        templateSelectionBox.style.display = 'none';
        resumePreviewBox.style.display = 'none';
        loadingSpinner.style.display = 'none';
        if (jobMatcherPanel) jobMatcherPanel.style.display = 'none';
        mainActions.innerHTML = '';

        switch (state) {
            case 'upload':
                uploadBox.style.display = 'flex';
                mainTitle.textContent = 'Analisis CV Baru';
                currentResumeId = null;
                currentResumeData = null;
                document.querySelectorAll('.resume-item.active').forEach(el => el.classList.remove('active'));
                break;
            case 'loading':
                loadingSpinner.style.display = 'flex';
                break;
            case 'review':
                reviewContainer.style.display = 'grid';
                mainTitle.textContent = `Hasil Analisis untuk ${currentResumeData.filename}`;
                mainActions.innerHTML = `
                    <button id="delete-btn" class="button-danger">Hapus</button>
                    ${currentResumeData.generated_cv_json ? '<button id="view-generated-btn" class="button-secondary">Lihat CV Jadi</button>' : ''}
                    <button id="create-resume-btn" class="button-primary">${currentResumeData.generated_cv_json ? 'Buat Ulang CV' : 'Buat Resume/CV'}</button>`;
                addReviewActionListeners();
                if (jobMatcherPanel) jobMatcherPanel.style.display = 'block';
                break;
            case 'template-selection':
                templateSelectionBox.style.display = 'block';
                mainTitle.textContent = 'Pilih Template CV';
                mainActions.innerHTML = `<button id="back-to-review-btn" class="button-secondary">Kembali ke Feedback</button>`;
                document.getElementById('back-to-review-btn').addEventListener('click', () => showState('review'));
                break;
            case 'preview':
                resumePreviewBox.style.display = 'block';
                mainTitle.textContent = 'Pratinjau CV Final';
                mainActions.innerHTML = `
                    <button id="back-to-templates-btn" class="button-secondary">Pilih Template Lain</button>
                    <button id="download-final-cv-btn" class="button-primary">Unduh CV Final</button>`;
                document.getElementById('back-to-templates-btn').addEventListener('click', () => showState('template-selection'));
                document.getElementById('download-final-cv-btn').addEventListener('click', downloadFinalCV);
                break;
        }
    };

    const displayResumeData = (data) => {
        currentResumeId = data.id;
        currentResumeData = data;
        resumeContentEl.textContent = data.resume_content;
        feedbackContentEl.innerHTML = window.marked ? marked.parse(data.feedback) : data.feedback;

        jobDescriptionInput.value = '';

        if (savedAnalysesList) {
            savedAnalysesList.innerHTML = '';
            if (data.analyses && data.analyses.length > 0) {
                data.analyses.forEach(analysis => {
                    const analysisItem = document.createElement('div');
                    analysisItem.className = 'saved-analysis-item card';
                    const analysisDate = new Date(analysis.created_at).toLocaleString('id-ID', { dateStyle: 'long', timeStyle: 'short' });
                    
                     // --- PASTIKAN BARIS DI BAWAH INI SEPERTI INI ---
                analysisItem.innerHTML = `
                    <details>
                        <summary>
                            <strong>Analisis pada ${analysisDate}</strong>
                            <p class="text-secondary">${analysis.job_description.substring(0, 100)}...</p>
                        </summary>
                        <div class="analysis-result-content">
                            ${analysis.match_result} 
                        </div>
                    </details>
                `;
                    savedAnalysesList.appendChild(analysisItem);
                });
            } else {
                savedAnalysesList.innerHTML = '<p class="text-secondary" style="text-align: center; padding: 1rem;">Belum ada analisis lowongan untuk CV ini.</p>';
            }
        }

        showState('review');
        document.querySelectorAll('.resume-item').forEach(el => {
            el.classList.toggle('active', el.dataset.id == currentResumeId);
        });
    };

    const processFile = async (file) => {
        showState('loading');
        const formData = new FormData();
        formData.append('resume_pdf', file);
        try {
            const response = await fetch('/api/ai/review-resume-pdf', { method: 'POST', body: formData });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Terjadi kesalahan server.');
            }
            const data = await response.json();
            addResumeToSidebar(data);
            // Panggil fetchAndDisplayResume untuk memuat data lengkap termasuk array 'analyses' kosong
            await fetchAndDisplayResume(data.resume_id);
        } catch (error) {
            alert(`Error: ${error.message}`);
            showState('upload');
        }
    };
    
    const fetchAndDisplayResume = async (resumeId) => {
        showState('loading');
        try {
            const response = await fetch(`/api/resumes/${resumeId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Gagal memuat.');
            }
            const data = await response.json();
            displayResumeData(data);
        } catch (error) {
            alert(error.message);
            showState('upload');
        }
    };
    
    const generateAndShowFinalResume = async (templateName) => {
        // (Fungsi ini tidak perlu diubah, bisa dibiarkan seperti sebelumnya)
    };

    const renderTemplate = (templateName, data) => {
        // (Fungsi ini tidak perlu diubah, bisa dibiarkan seperti sebelumnya)
    };
    
    const downloadFinalCV = async () => {
        // (Fungsi ini tidak perlu diubah, bisa dibiarkan seperti sebelumnya)
    };
    
    const deleteResume = async () => {
        if (!currentResumeId || !confirm('Anda yakin ingin menghapus resume ini?')) return;
        try {
            const response = await fetch(`/api/resumes/${currentResumeId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Gagal menghapus.');
            // Cari wrapper untuk dihapus
            document.querySelector(`.resume-item[data-id='${currentResumeId}']`).closest('.resume-item-wrapper').remove();
            showState('upload');
        } catch (error) { alert(error.message); }
    };

    function addReviewActionListeners() {
        document.getElementById('delete-btn')?.addEventListener('click', deleteResume);
        document.getElementById('create-resume-btn')?.addEventListener('click', () => showState('template-selection'));
        const viewGeneratedBtn = document.getElementById('view-generated-btn');
        if (viewGeneratedBtn) {
            viewGeneratedBtn.addEventListener('click', () => {
                if (currentResumeData && currentResumeData.generated_cv_json) {
                    renderTemplate('modern', JSON.parse(currentResumeData.generated_cv_json));
                    showState('preview');
                }
            });
        }
    }

    const addResumeToSidebar = (data) => {
        const list = document.getElementById('saved-resumes-list');
        list.querySelector('.empty-list-text')?.remove();
        const wrapper = document.createElement('div');
        wrapper.className = 'resume-item-wrapper';
        wrapper.innerHTML = `
            <a href="#" class="resume-item" data-id="${data.resume_id}">
                <span class="filename">${data.filename}</span>
                <span class="timestamp">${data.created_at}</span>
            </a>
            <div class="generated-cv-action" id="action-container-${data.resume_id}"></div>`;
        list.prepend(wrapper);
        wrapper.querySelector('.resume-item').addEventListener('click', (e) => { e.preventDefault(); fetchAndDisplayResume(data.resume_id); });
    };

    const analyzeJobMatch = async () => {
        const jobDescription = jobDescriptionInput.value.trim();
        if (!currentResumeId || !jobDescription) {
            alert('Harap pilih resume dan isi deskripsi pekerjaan.');
            return;
        }

        matchJobBtn.disabled = true;
        matchJobBtn.textContent = 'Menganalisis...';
    
        try {
            const response = await fetch('/api/ai/match-job-description', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resume_id: currentResumeId,
                    job_description: jobDescription
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error');
            }

            // Muat ulang data untuk menampilkan analisis baru di daftar riwayat
            await fetchAndDisplayResume(currentResumeId);

        } catch (error) {
            alert(`Gagal mendapatkan analisis: ${error.message}`);
        } finally {
            matchJobBtn.disabled = false;
            matchJobBtn.textContent = 'Analisis Sekarang';
        }
    };

    // Event Listeners
    uploadInput.addEventListener('change', () => { if (uploadInput.files.length > 0) processFile(uploadInput.files[0]); });
    uploadBox.addEventListener('dragover', (e) => e.preventDefault());
    uploadBox.addEventListener('drop', (e) => { e.preventDefault(); if (e.dataTransfer.files.length > 0) processFile(e.dataTransfer.files[0]); });
    newAnalysisBtn.addEventListener('click', () => showState('upload'));
    document.querySelectorAll('.resume-item').forEach(item => {
        item.addEventListener('click', (e) => { e.preventDefault(); fetchAndDisplayResume(item.dataset.id); });
    });
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => generateAndShowFinalResume(card.dataset.template));
    });
    if (matchJobBtn) {
        matchJobBtn.addEventListener('click', analyzeJobMatch);
    }

    // Inisialisasi
    showState('upload');
});