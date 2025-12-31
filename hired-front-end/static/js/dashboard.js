const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            activeTab: 'post',
            user: {},

            // --- EDIT MODE STATE (New) ---
            isEditing: false,
            editingId: null,

            // --- DROPDOWN STATE ---
            categoryOpen: false,
            typeOpen: false,
            categories: [
                'Development', 'Design', 'Marketing', 'Finance',
                'Engineering', 'Sales', 'Healthcare'
            ],
            jobTypes: ['On-site', 'Remote', 'Hybrid'],

            // Post/Edit Job Form Data
            uploadMode: 'url',
            isSubmitting: false,
            logoFile: null,
            raw: { description: '', responsibilities: '', qualifications: '', soft_skills: '' },
            form: { title: '', company: '', location: '', experience: '', salary: '', type: 'On-site', category: '', logo_url: '' },

            // Manage Jobs State
            myJobs: [],
            showDeleteModal: false,
            jobToDelete: null,

            // Real Applications State
            applications: [],

            // Toasts
            showSuccess: false,
            successMessage: ''
        }
    },

    computed: {
        pendingAppsCount() {
            return this.applications.filter(a => a.status === 'pending').length;
        }
    },

    async mounted() {
        await this.loadUser();
        if (!this.user || this.user.role !== 'provider') {
            return;
        }

        // 2. Load Data
        await this.loadMyJobs();
        await this.loadRealApplications();

        // 3. Add Event Listener for closing dropdowns
        document.addEventListener('click', this.closeDropdowns);

        this.loading = false;
    },

    unmounted() {
        document.removeEventListener('click', this.closeDropdowns);
    },

    methods: {
        async loadUser() {
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
                AuthModel.logout();
                return;
            }

            this.user = {
                ...currentUser,
                photo: resolveUploadUrl(currentUser.photo)
            };
            if (this.user.role !== 'provider') {
                window.location.href = '/';
                return;
            }
            this.form.company = this.user.companyName || '';
        },

        normalizeCompanyName(name) {
            return String(name || '').toLowerCase().replace(/\s+/g, ' ').trim();
        },

        normalizeStatus(status) {
            return String(status || '').toLowerCase();
        },
        formatStatus(status) {
            const normalized = this.normalizeStatus(status);
            if (normalized === 'accepted') return 'Accepted';
            if (normalized === 'rejected') return 'Rejected';
            return 'Pending';
        },
        isPending(status) {
            return this.normalizeStatus(status) === 'pending';
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

        // --- DROPDOWN LOGIC ---
        toggleCategory() {
            this.categoryOpen = !this.categoryOpen;
            this.typeOpen = false;
        },
        selectCategory(option) {
            this.form.category = option;
            this.categoryOpen = false;
        },
        toggleType() {
            this.typeOpen = !this.typeOpen;
            this.categoryOpen = false;
        },
        selectType(option) {
            this.form.type = option;
            this.typeOpen = false;
        },
        closeDropdowns(e) {
            if (!e.target.closest('.custom-select-wrapper')) {
                this.categoryOpen = false;
                this.typeOpen = false;
            }
        },

        // --- MANAGE JOBS LOGIC ---
        async loadMyJobs() {
            try {
                const allJobs = await JobModel.getAll();
                // Use companyName from auth service
                const myCompany = this.normalizeCompanyName(this.user.companyName || this.user.name);
                if (myCompany) {
                    this.myJobs = allJobs.filter(j => this.normalizeCompanyName(j.company).includes(myCompany));
                } else {
                    this.myJobs = [];
                }
            } catch (err) {
                console.error("Failed to load jobs", err);
            }
        },

        // --- EDIT JOB LOGIC (New) ---
        arrayToText(arr) {
            if (!arr || !Array.isArray(arr)) return '';
            return arr.join('\n');
        },

        editJob(job) {
            this.isEditing = true;
            this.editingId = job.id;

            // 1. Populate Basic Fields
            this.form = {
                title: job.title,
                company: job.company,
                location: job.location,
                experience: job.experience,
                salary: job.salary,
                type: job.type || 'On-site',
                category: job.category || '',
                logo_url: job.logoUrlRaw || job.logo_url || ''
            };

            // 2. Populate Text Areas (Convert Arrays -> String)
            this.raw.description = this.arrayToText(job.description);
            this.raw.responsibilities = this.arrayToText(job.responsibilities);
            this.raw.qualifications = this.arrayToText(job.qualifications);
            // Handle snake_case vs camelCase mismatch if present
            this.raw.soft_skills = this.arrayToText(job.softSkills || job.soft_skills);

            // 3. Determine Logo Mode
            if (job.logoUrl && !job.logoUrl.startsWith('blob:') && !job.logoUrl.startsWith('data:')) {
                this.uploadMode = 'url';
            }

            // 4. Switch Tab & Scroll
            this.activeTab = 'post';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },

        cancelEdit() {
            this.resetForm();
        },

        // --- POST / PUT JOB LOGIC ---
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) this.logoFile = file;
        },
        textToArray(text) {
            if (!text) return [];
            return text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        },

        async submitJob() {
            this.isSubmitting = true;
            try {
                const wasEditing = this.isEditing;
                // 1. Prepare Arrays
                const descriptionArr = this.textToArray(this.raw.description);
                const responsibilitiesArr = this.textToArray(this.raw.responsibilities);
                const qualificationsArr = this.textToArray(this.raw.qualifications);
                const softSkillsArr = this.textToArray(this.raw.soft_skills);

                let result;

                if (this.isEditing) {
                    // UPDATE existing job via PUT
                    const payload = {
                        ...this.form,
                        description: descriptionArr,
                        responsibilities: responsibilitiesArr,
                        qualifications: qualificationsArr,
                        soft_skills: softSkillsArr
                    };
                    result = await JobModel.update(this.editingId, payload);
                } else {
                    // CREATE new job via POST
                    const formData = new FormData();
                    formData.append('title', this.form.title);
                    formData.append('company', this.form.company);
                    formData.append('location', this.form.location);
                    formData.append('experience', this.form.experience);
                    formData.append('salary', this.form.salary);
                    formData.append('type', this.form.type);
                    formData.append('category', this.form.category);

                    descriptionArr.forEach(item => formData.append('description', item));
                    responsibilitiesArr.forEach(item => formData.append('responsibilities', item));
                    qualificationsArr.forEach(item => formData.append('qualifications', item));
                    softSkillsArr.forEach(item => formData.append('soft_skills', item));

                    if (this.uploadMode === 'url' && this.form.logo_url) {
                        formData.append('logo_url', this.form.logo_url);
                    } else if (this.logoFile) {
                        formData.append('logo', this.logoFile);
                    }

                    result = await JobModel.create(formData);
                }

                this.successMessage = this.isEditing ? "Job Updated Successfully!" : "Job Posted Successfully!";
                this.showSuccess = true;

                this.resetForm();
                await this.loadMyJobs();

                if (wasEditing) {
                    this.activeTab = 'manage';
                }

                setTimeout(() => { this.showSuccess = false; }, 3000);

            } catch (error) {
                console.error(error);
                alert("Error: " + error.message);
            } finally {
                this.isSubmitting = false;
            }
        },

        resetForm() {
            // Reset Edit State
            this.isEditing = false;
            this.editingId = null;

            // Reset Fields
            const companyName = this.form.company;
            this.form = {
                title: '', company: companyName, location: '', experience: '',
                salary: '', type: 'On-site', category: '', logo_url: ''
            };
            this.raw = { description: '', responsibilities: '', qualifications: '', soft_skills: '' };
            this.logoFile = null;
        },

        // --- REAL APPLICATIONS LOGIC ---
        async loadRealApplications() {
            try {
                const allApplicationsPromises = this.myJobs.map(async (job) => {
                    try {
                        const apps = await ApplicationModel.getJobApplications(job.id);
                        return apps.map(app => {
                            const normalizedStatus = this.normalizeStatus(app.status);
                            const userId = app.userId || app.user_id;
                            const applicantName = app.applicantName || app.applicant_name || '';
                            return {
                                ...app,
                                jobTitle: job.title,
                                jobId: job.id,
                                applicantName,
                                applicantEmail: app.applicantEmail || app.applicant_email || '',
                                applicantPhone: app.applicantPhone || app.applicant_phone || '',
                                applicantLocation: app.applicantLocation || app.applicant_location || '',
                                applicantJobTitle: app.applicantJobTitle || app.applicant_job_title || '',
                                applicantPhoto: resolveUploadUrl(app.applicantPhoto || app.applicant_photo),
                                applicantLabel: applicantName || (userId ? `Applicant #${userId}` : 'Applicant'),
                                appliedAt: this.formatDate(app.appliedAt || app.applied_at),
                                cvName: app.cvName || app.cv_name || 'View CV',
                                cvUrl: resolveAppUploadUrl(app.cvUrl || app.cv_url),
                                status: normalizedStatus,
                                statusLabel: this.formatStatus(normalizedStatus)
                            };
                        });
                    } catch (e) {
                        console.error(`Failed to load applications for job ${job.id}:`, e);
                        return [];
                    }
                });

                const allApplicationsArrays = await Promise.all(allApplicationsPromises);
                this.applications = allApplicationsArrays.flat().reverse();
            } catch (err) {
                console.error("Failed to load applications", err);
                this.applications = [];
            }
        },

        async updateAppStatus(app, newStatus) {
            try {
                const normalizedStatus = this.normalizeStatus(newStatus);
                await ApplicationModel.updateStatus(app.id, normalizedStatus);
                app.status = normalizedStatus;
                app.statusLabel = this.formatStatus(normalizedStatus);
            } catch (err) {
                console.error('Failed to update application status:', err);
                alert('Failed to update status. Please try again.');
            }
        },

        getStatusClass(status) {
            const normalized = this.normalizeStatus(status);
            if (normalized === 'accepted') return 'badge-accepted';
            if (normalized === 'rejected') return 'badge-rejected';
            return 'badge-pending';
        },

        // --- MANAGE JOBS (Delete/View) ---
        viewJob(id) {
            window.location.href = `/job-details?id=${id}`;
        },

        confirmDeleteJob(id) {
            this.jobToDelete = id;
            this.showDeleteModal = true;
        },

        async deleteJob() {
            if (!this.jobToDelete) return;
            try {
                const response = await fetch(`/api/jobs/${this.jobToDelete}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.successMessage = "Job deleted successfully";
                    this.showSuccess = true;
                    this.myJobs = this.myJobs.filter(j => j.id !== this.jobToDelete);
                    await this.loadRealApplications();
                } else {
                    alert("Failed to delete job.");
                }
            } catch (err) {
                console.error(err);
                alert("Error connecting to server.");
            } finally {
                this.showDeleteModal = false;
                this.jobToDelete = null;
                setTimeout(() => this.showSuccess = false, 3000);
            }
        }
    },
    compilerOptions: { delimiters: ['[[', ']]'] }
}).mount('#dashboard-app');
