// GANTI SEMUA ISI FILE app/static/js/ai_resume_pro.js DENGAN INI

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

    let currentResumeId = null;
    let currentResumeData = null;

    const showState = (state) => {
        uploadBox.style.display = 'none';
        reviewContainer.style.display = 'none';
        templateSelectionBox.style.display = 'none';
        resumePreviewBox.style.display = 'none';
        loadingSpinner.style.display = 'none';
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
                    <button id="create-resume-btn" class="button-primary">Buat Resume/CV</button>`;
                addReviewActionListeners();
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
        currentResumeId = data.resume_id;
        currentResumeData = data;
        resumeContentEl.textContent = data.resume_content;
        feedbackContentEl.innerHTML = window.marked ? marked.parse(data.feedback) : data.feedback;
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
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Terjadi kesalahan.');
            addResumeToSidebar(data);
            displayResumeData(data);
        } catch (error) {
            alert(`Error: ${error.message}`);
            showState('upload');
        }
    };
    
    const fetchAndDisplayResume = async (resumeId) => {
        showState('loading');
        try {
            const response = await fetch(`/api/resumes/${resumeId}`);
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Gagal memuat.');
            const formattedData = {
                resume_id: data.id, filename: data.filename,
                resume_content: data.resume_content, feedback: data.feedback
            };
            displayResumeData(formattedData);
        } catch (error) {
            alert(error.message);
            showState('upload');
        }
    };
    
    const generateAndShowFinalResume = async (templateName) => {
        showState('loading');
        try {
            const response = await fetch('/api/ai/generate-formatted-resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume_id: currentResumeId, template_name: templateName })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Gagal membuat CV final.');

            const finalResumeData = JSON.parse(data.final_resume_json);
            renderTemplate(templateName, finalResumeData);
            showState('preview');
        } catch (error) {
            alert(`Error: ${error.message}`);
            showState('review');
        }
    };

    const renderTemplate = (templateName, data) => {
        const workExpHTML = (data.work_experience || []).map(job => `
            <div class="item">
                <div class="item-header">
                    <p class="item-title">${job.job_title || ''} | <strong>${job.company_name || ''}</strong></p>
                    <p class="item-date">${job.date_range || ''}</p>
                </div>
                <ul>${(job.responsibilities || []).map(r => `<li>${r}</li>`).join('')}</ul>
            </div>`).join('');
        
        const educationHTML = (data.education || []).map(edu => `
            <div class="item">
                 <div class="item-header">
                    <p class="item-title"><strong>${edu.institution || ''}</strong></p>
                    <p class="item-date">${edu.date_range || ''}</p>
                </div>
                <p class="item-issuer">${edu.degree || ''}</p>
                <p>${edu.description || ''}</p>
            </div>`).join('');
            
        const certsHTML = (data.certifications_and_awards || []).map(cert => `
            <div class="item">
                <div class="item-header">
                    <p class="item-title"><strong>${cert.title || ''}</strong></p>
                    <p class="item-date">${cert.date || ''}</p>
                </div>
                <p class="item-issuer">${cert.issuer || ''}</p>
                <p>${cert.description || ''}</p>
            </div>`).join('');

        let templateHTML = '';
        switch(templateName) {
            case 'classic':
                templateHTML = `
                <div class="resume-template template-classic" id="final-resume-content">
                    <div class="header">
                        <h1>${data.personal_data?.full_name || ''}</h1>
                        <p class="contact-info">${data.contact?.address || ''} &bull; ${data.contact?.phone || ''} &bull; ${data.contact?.email || ''}</p>
                    </div>
                    <div class="section"><h2>Profil</h2><p>${data.profile_summary || ''}</p></div>
                    <div class="section"><h2>Riwayat Pekerjaan</h2>${workExpHTML}</div>
                    <div class="section"><h2>Pendidikan</h2>${educationHTML}</div>
                    <div class="section"><h2>Sertifikat & Penghargaan</h2>${certsHTML}</div>
                    <div class="section"><h2>Keahlian</h2><p>${(data.skills || []).join(', ')}</p></div>
                </div>`;
                break;
            case 'creative':
                 templateHTML = `
                 <div class="resume-template template-creative" id="final-resume-content">
                    <div class="left-column">
                        <div class="photo"></div>
                        <div class="section"><h2>Kontak</h2>
                            <div class="contact-item"><strong>Telepon</strong><span>${data.contact?.phone || ''}</span></div>
                            <div class="contact-item"><strong>Email</strong><span>${data.contact?.email || ''}</span></div>
                            <div class="contact-item"><strong>Alamat</strong><span>${data.contact?.address || ''}</span></div>
                        </div>
                        <div class="section"><h2>Keahlian</h2>
                            ${(data.skills || []).map(s => `<div class="skill-item"><span>${s}</span></div>`).join('')}
                        </div>
                    </div>
                    <div class="right-column">
                        <h1>${data.personal_data?.full_name || ''}</h1>
                        <p class="professional-title">${data.personal_data?.professional_title || ''}</p>
                        <div class="section"><h2>Profil</h2><p>${data.profile_summary || ''}</p></div>
                        <div class="section"><h2>Riwayat Pekerjaan</h2>${workExpHTML}</div>
                        <div class="section"><h2>Pendidikan</h2>${educationHTML}</div>
                        <div class="section"><h2>Sertifikat & Penghargaan</h2>${certsHTML}</div>
                    </div>
                 </div>`;
                break;
            case 'modern':
            default:
                templateHTML = `
                <div class="resume-template template-modern" id="final-resume-content">
                    <div class="header">
                        <h1>${data.personal_data?.full_name || ''}</h1>
                        <p class="professional-title">${data.personal_data?.professional_title || ''}</p>
                        <p class="contact-info">${data.contact?.address || ''} &bull; ${data.contact?.phone || ''} &bull; ${data.contact?.email || ''}</p>
                    </div>
                    <div class="section"><h2>Profil Profesional</h2><p>${data.profile_summary || ''}</p></div>
                    <div class="section"><h2>Riwayat Pekerjaan</h2>${workExpHTML}</div>
                    <div class="section"><h2>Pendidikan</h2>${educationHTML}</div>
                    <div class="section"><h2>Sertifikat & Penghargaan</h2>${certsHTML}</div>
                    <div class="section"><h2>Keahlian</h2><div class="skills-list">${(data.skills || []).map(s => `<span class="skill-item">${s}</span>`).join('')}</div></div>
                </div>`;
                break;
        }
        resumePreviewBox.innerHTML = templateHTML;
    };

    const downloadFinalCV = async () => {
        const resumeEl = document.getElementById('final-resume-content');
        if (!resumeEl) return;
        const btn = document.getElementById('download-final-cv-btn');
        btn.disabled = true;
        btn.textContent = 'Mempersiapkan PDF...';
    
        try {
            const canvas = await html2canvas(resumeEl, {
                scale: 2.5, // Meningkatkan resolusi
                useCORS: true,
                logging: false,
                backgroundColor: '#ffffff'
            });
            
            const imgData = canvas.toDataURL('image/png', 1.0); // Kualitas Penuh
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            pdf.save(`CV - ${currentResumeData.filename.replace('.pdf', '')} - Farmile.pdf`);
        } catch (error) {
            console.error("PDF Generation Error:", error);
            alert("Maaf, terjadi kesalahan saat membuat PDF. Silakan coba lagi.");
        } finally {
            btn.disabled = false;
            btn.textContent = 'Unduh CV Final';
        }
    };
    
    // Sisa fungsi (addReviewActionListeners, deleteResume, dll.) tetap sama
    const deleteResume = async () => {
        if (!currentResumeId || !confirm('Anda yakin ingin menghapus resume ini?')) return;
        try {
            const response = await fetch(`/api/resumes/${currentResumeId}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Gagal menghapus.');
            document.querySelector(`.resume-item[data-id='${currentResumeId}']`)?.remove();
            showState('upload');
        } catch (error) { alert(error.message); }
    };
    function addReviewActionListeners() {
        document.getElementById('delete-btn')?.addEventListener('click', deleteResume);
        document.getElementById('create-resume-btn')?.addEventListener('click', () => showState('template-selection'));
    }
    const addResumeToSidebar = (data) => {
        const list = document.getElementById('saved-resumes-list');
        list.querySelector('.empty-list-text')?.remove();
        const newItem = document.createElement('a');
        newItem.href = "#";
        newItem.className = 'resume-item';
        newItem.dataset.id = data.resume_id;
        newItem.innerHTML = `<span class="filename">${data.filename}</span><span class="timestamp">${data.created_at}</span>`;
        list.prepend(newItem);
        newItem.addEventListener('click', (e) => { e.preventDefault(); fetchAndDisplayResume(data.resume_id); });
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

    // Inisialisasi
    showState('upload');
});