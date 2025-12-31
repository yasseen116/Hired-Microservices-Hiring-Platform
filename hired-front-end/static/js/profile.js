const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            isSaving: false,

            // User Data
            user: {
                name: '',
                jobTitle: '',
                email: '',
                phone: '',
                location: '',
                about: '',
                photo: null,
                skills: [],
                experience: [],
                education: [],
                cvName: null,
                cvUrl: null
            },
            applications: [],

            // Toasts
            showSuccessNotification: false,
            successMessage: '',
            showErrorNotification: false,
            errorMessage: '',

            // Delete Modal State
            showDeleteModal: false,

            // Cropper state
            showCropModal: false,
            tempImageUrl: null,
            cropper: null
        }
    },
    async mounted() {
        await this.loadProfile();
    },
    methods: {
        applyUserData(rawUser) {
            const skills = Array.isArray(rawUser.skills) && rawUser.skills.length > 0
                ? rawUser.skills.map((skill, index) => ({ id: Date.now() + index, value: skill }))
                : [{ id: Date.now(), value: '' }];

            const experience = Array.isArray(rawUser.experience) && rawUser.experience.length > 0
                ? rawUser.experience.map((exp, index) => ({ id: exp.id || Date.now() + index, ...exp }))
                : [{ id: Date.now(), role: '', company: '', years: '' }];

            const education = Array.isArray(rawUser.education) && rawUser.education.length > 0
                ? rawUser.education.map((edu, index) => ({ id: edu.id || Date.now() + index, ...edu }))
                : [{ id: Date.now(), degree: '', university: '', year: '' }];

            this.user = {
                ...this.user,
                ...rawUser,
                jobTitle: rawUser.jobTitle || rawUser.job_title || '',
                cvName: rawUser.cvName || rawUser.cv_name || null,
                cvUrl: resolveUploadUrl(rawUser.cvUrl || rawUser.cv_url),
                photo: resolveUploadUrl(rawUser.photo),
                skills,
                experience,
                education
            };
        },
        formatDate(value) {
            if (!value) return '';
            const parsed = new Date(value);
            if (Number.isNaN(parsed.getTime())) return value;
            return new Intl.DateTimeFormat('en-US', {
                year: 'numeric',
                month: 'short',
                day: '2-digit'
            }).format(parsed);
        },
        async loadProfile() {
            try {
                // 1. Get User Data
                const storedUser = AuthModel.getUser();
                if (!storedUser || !AuthModel.isLoggedIn()) {
                    window.location.href = '/login';
                    return;
                }

                let currentUser = storedUser;
                try {
                    currentUser = await AuthModel.getProfile();
                    localStorage.setItem('user', JSON.stringify(currentUser));
                } catch (error) {
                    console.error('Failed to refresh profile:', error);
                    if (error.message === 'Session expired') {
                        AuthModel.logout();
                        return;
                    }
                }

                this.applyUserData(currentUser);

                // 5. Get Applications from API
                try {
                    const rawApps = await ApplicationModel.getMyApplications();
                    // Applications from API already have job info enriched
                    this.applications = rawApps.map(app => ({
                        id: app.id,
                        jobId: app.jobId || app.job_id,
                        jobTitle: app.jobTitle || app.job_title || `Job #${app.jobId || app.job_id}`,
                        company: app.company || app.job_company || 'Unknown',
                        appliedAt: this.formatDate(app.appliedAt || app.applied_at),
                        status: app.status
                    })).reverse();
                } catch (e) {
                    console.error('Failed to load applications:', e);
                    this.applications = [];
                }

            } catch (error) {
                console.error(error);
            } finally {
                this.loading = false;
            }
        },

        // --- PHOTO + CROPPER ---
        handlePhotoUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            // Updated size guard: ~5MB max for localStorage safety
            const maxBytes = 5 * 1024 * 1024;
            if (file.size > maxBytes) {
                // Show error toast instead of alert
                this.errorMessage = 'Selected image is too large. Please choose an image under 5MB.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => {
                this.tempImageUrl = e.target.result;
                this.showCropModal = true;
                this.$nextTick(() => {
                    const imgEl = this.$refs.cropperImage;
                    if (!imgEl) return;
                    // Destroy previous cropper if exists
                    if (this.cropper) { this.cropper.destroy(); this.cropper = null; }
                    // Initialize Cropper.js with square aspect ratio
                    this.cropper = new Cropper(imgEl, {
                        aspectRatio: 1,
                        viewMode: 1,
                        autoCropArea: 1,
                        dragMode: 'move',
                        background: false,
                        responsive: true,
                        movable: true,
                        zoomable: true,
                        minCropBoxWidth: 100,
                        minCropBoxHeight: 100
                    });
                });
            };
            reader.readAsDataURL(file);
        },
        closeCropper() {
            if (this.cropper) { this.cropper.destroy(); this.cropper = null; }
            this.showCropModal = false;
            this.tempImageUrl = null;
        },
        async confirmCrop() {
            if (!this.cropper) { this.closeCropper(); return; }
            try {
                const canvas = this.cropper.getCroppedCanvas({ width: 512, height: 512, imageSmoothingQuality: 'high' });

                // Convert canvas to blob then to file
                canvas.toBlob(async (blob) => {
                    try {
                        const file = new File([blob], "profile.png", { type: "image/png" });

                        // Upload to API
                        await AuthModel.uploadPhoto(file);

                        // Refresh user data
                        const updatedUser = await AuthModel.getProfile();
                        localStorage.setItem('user', JSON.stringify(updatedUser));
                        this.applyUserData(updatedUser);

                        this.successMessage = 'Profile photo updated.';
                        this.showSuccessNotification = true;
                        setTimeout(() => { this.showSuccessNotification = false; }, 3000);
                    } catch (error) {
                        console.error('Failed to upload photo:', error);
                        this.errorMessage = error.message || 'Failed to upload photo.';
                        this.showErrorNotification = true;
                        setTimeout(() => { this.showErrorNotification = false; }, 3000);
                    }
                }, 'image/png');
            } catch (e) {
                this.errorMessage = 'Could not crop the image. Please try another file.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
            } finally {
                this.closeCropper();
            }
        },
        async removePhoto() {
            try {
                await AuthModel.deletePhoto();
                const updatedUser = await AuthModel.getProfile();
                localStorage.setItem('user', JSON.stringify(updatedUser));
                this.applyUserData(updatedUser);
                this.successMessage = 'Profile photo removed.';
                this.showSuccessNotification = true;
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
            } catch (error) {
                console.error('Failed to remove photo:', error);
                this.errorMessage = error.message || 'Failed to remove photo.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
            }
        },

        // --- SKILLS ---
        addSkill() { this.user.skills.push({ id: Date.now(), value: '' }); },
        removeSkill(index) { this.user.skills.splice(index, 1); },

        // --- EXPERIENCE ---
        addExperience() { this.user.experience.push({ id: Date.now(), role: '', company: '', years: '' }); },
        removeExperience(index) { this.user.experience.splice(index, 1); },

        // --- EDUCATION ---
        addEducation() { this.user.education.push({ id: Date.now(), degree: '', university: '', year: '' }); },
        removeEducation(index) { this.user.education.splice(index, 1); },

        // --- CV ---
        async handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            try {
                // Upload CV to API
                await AuthModel.uploadCV(file);

                // Refresh user data
                const updatedUser = await AuthModel.getProfile();
                localStorage.setItem('user', JSON.stringify(updatedUser));
                this.applyUserData(updatedUser);

                this.successMessage = 'CV uploaded successfully!';
                this.showSuccessNotification = true;
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
            } catch (error) {
                console.error('Failed to upload CV:', error);
                this.errorMessage = error.message || 'Failed to upload CV.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
            }
        },

        previewCv() {
            if (!this.user.cvUrl) {
                this.errorMessage = 'No CV available to preview.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
                return;
            }
            window.open(this.user.cvUrl, '_blank', 'noopener');
        },

        // --- UPDATED: Delete Logic ---
        removeCv() {
            this.showDeleteModal = true;
        },

        async confirmDeleteCv() {
            try {
                await AuthModel.deleteCV();
                const updatedUser = await AuthModel.getProfile();
                localStorage.setItem('user', JSON.stringify(updatedUser));
                this.applyUserData(updatedUser);
                this.showDeleteModal = false;

                this.successMessage = "Resume removed successfully.";
                this.showSuccessNotification = true;
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
            } catch (error) {
                console.error('Failed to remove CV:', error);
                this.errorMessage = error.message || 'Failed to remove CV.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
            }
        },

        closeDeleteModal() {
            this.showDeleteModal = false;
        },

        // --- SAVE ---
        async saveProfile() {
            this.isSaving = true;

            try {
                const cleanSkills = this.user.skills.map(s => s.value).filter(v => v.trim() !== "");
                const cleanExp = this.user.experience.filter(e => e.role.trim() !== "");
                const cleanEdu = this.user.education.filter(e => e.degree.trim() !== "");

                const profileData = {
                    job_title: this.user.jobTitle,
                    skills: cleanSkills,
                    phone: this.user.phone,
                    location: this.user.location,
                    about: this.user.about,
                    experience: cleanExp,
                    education: cleanEdu
                };

                await AuthModel.updateProfile(profileData);
                const updatedUser = await AuthModel.getProfile();
                localStorage.setItem('user', JSON.stringify(updatedUser));
                this.applyUserData(updatedUser);

                this.successMessage = "Profile saved successfully!";
                this.showSuccessNotification = true;
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
            } catch (error) {
                console.error('Failed to save profile:', error);
                this.errorMessage = error.message || 'Failed to save profile.';
                this.showErrorNotification = true;
                setTimeout(() => { this.showErrorNotification = false; }, 3000);
            } finally {
                this.isSaving = false;
            }
        },

        getStatusClass(status) {
            const normalized = String(status || '').toLowerCase();
            if (normalized === 'accepted') return 'badge-accepted';
            if (normalized === 'rejected') return 'badge-rejected';
            return 'badge-pending';
        }
    },
    compilerOptions: { delimiters: ['[[', ']]'] }
}).mount('#app');
