const { createApp } = Vue;

createApp({
    data() {
        return {
            loading: true,
            job: {
                // Initial empty state matching your Schema structure
                description: [],
                responsibilities: [],
                softSkills: [], // Note: API likely sends 'softSkills' (camelCase)
                qualifications: [],
                company: '',
                title: ''
            },
            similarJobs: [],
            error: null,

            // UI States
            isCopied: false,
            isInWishlist: false,
            loginMessage: false,

            // Modal & Notification States
            showApplyModal: false,
            selectedJobForApp: null,
            newCvName: null,
            newCvFile: null,
            showLoginNotification: false,
            isApplying: false,
            showSuccessNotification: false,
            successMessage: ''
        }
    },
    async mounted() {
        // 1. Get Job ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        const jobId = urlParams.get('id');

        if (!jobId) {
            this.error = "No Job ID specified.";
            this.loading = false;
            return;
        }

        try {
            // MVC Step 1: Get Job Details from Model
            this.job = await JobModel.getById(jobId);
            console.log("Job Details loaded:", this.job);

            // MVC Step 2: Get Similar Jobs from Model
            // (The Model now handles the specific API endpoint logic)
            this.similarJobs = await JobModel.getSimilar(jobId);
            console.log("Similar Jobs loaded:", this.similarJobs);

            // 3. Check Wishlist (Local Storage logic)
            this.checkWishlistStatus(jobId);

        } catch (error) {
            console.error("Error loading job details:", error);
            this.error = "Job not found or API is down.";
        } finally {
            this.loading = false;
        }
    },

    methods: {
        async fetchSimilarJobs(currentId) {
            try {
                this.similarJobs = await JobModel.getSimilar(currentId);
                console.log("Similar Jobs from API:", this.similarJobs);
            } catch (err) {
                console.warn("Could not load similar jobs", err);
            }
        },

        async copyLink() {
            try {
                const link = window.location.href;
                await navigator.clipboard.writeText(link);
                this.isCopied = true;
                setTimeout(() => { this.isCopied = false; }, 1250);
            } catch (err) {
                console.error('Failed to copy: ', err);
                alert("Could not copy link automatically.");
            }
        },

        // --- WISHLIST LOGIC (Kept on LocalStorage for now) ---
        checkWishlistStatus(id) {
            if (!localStorage.getItem('user')) return;
            const wishlist = JSON.parse(localStorage.getItem('my_wishlist') || '[]');
            // Ensure we compare strings to strings
            this.isInWishlist = wishlist.includes(String(id));
        },

        toggleWishlist() {
            const user = localStorage.getItem('user');
            if (!user) {
                this.loginMessage = true;
                setTimeout(() => { this.loginMessage = false; }, 2000);
                return;
            }

            const jobId = String(this.job.id);
            let wishlist = JSON.parse(localStorage.getItem('my_wishlist') || '[]');

            if (this.isInWishlist) {
                wishlist = wishlist.filter(id => id !== jobId);
                this.isInWishlist = false;
            } else {
                wishlist.push(jobId);
                this.isInWishlist = true;
            }
            localStorage.setItem('my_wishlist', JSON.stringify(wishlist));
        },

        // --- APPLY MODAL LOGIC ---
        openApplyModal(job) {
            if (!AuthModel.isLoggedIn()) {
                this.showLoginNotification = true;
                setTimeout(() => { window.location.href = '/login'; }, 2000);
                return;
            }
            this.selectedJobForApp = job || this.job;
            this.showApplyModal = true;
            this.newCvName = null;
            this.newCvFile = null;
        },

        closeModal() {
            this.showApplyModal = false;
            this.selectedJobForApp = null;
            this.newCvName = null;
            this.newCvFile = null;
        },

        handleCvUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.newCvName = file.name;
                this.newCvFile = file;
            }
        },

        async applyWithExisting() {
            this.isApplying = true;
            try {
                await ApplicationModel.submitWithExistingCv(this.selectedJobForApp.id);
                this.successMessage = `Application sent to ${this.selectedJobForApp.company}!`;
                this.showSuccessNotification = true;
                this.closeModal();
                setTimeout(() => this.showSuccessNotification = false, 3000);
            } catch (error) {
                alert(error.message || 'Failed to submit application.');
            } finally {
                this.isApplying = false;
            }
        },

        async applyWithNew() {
            if (!this.newCvFile) return;
            this.isApplying = true;
            try {
                await ApplicationModel.submit(this.selectedJobForApp.id, this.newCvFile);
                this.successMessage = `Application sent to ${this.selectedJobForApp.company}!`;
                this.showSuccessNotification = true;
                this.closeModal();
                setTimeout(() => this.showSuccessNotification = false, 3000);
            } catch (error) {
                alert(error.message || 'Failed to submit application.');
            } finally {
                this.isApplying = false;
            }
        }
    },

    compilerOptions: {
        delimiters: ['[[', ']]']
    }
}).mount('#app');
