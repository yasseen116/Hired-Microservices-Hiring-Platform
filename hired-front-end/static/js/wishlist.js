const { createApp } = Vue;

createApp({
    data() {
        return {
            isLoading: true,
            savedJobs: [],

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
        await this.loadWishlist();
    },

    methods: {
        async loadWishlist() {
            try {
                const wishlistIds = JSON.parse(localStorage.getItem('my_wishlist')) || [];

                if (wishlistIds.length === 0) {
                    this.savedJobs = [];
                    this.isLoading = false;
                    return;
                }

                const allJobs = await JobModel.getAll();

                this.savedJobs = allJobs.filter(job => wishlistIds.includes(String(job.id)));

            } catch (error) {
                console.error("Error loading wishlist:", error);
            } finally {
                this.isLoading = false;
            }
        },

        removeFromWishlist(jobId) {
            const idToRemove = String(jobId);

            let list = JSON.parse(localStorage.getItem('my_wishlist')) || [];
            list = list.filter(id => id !== idToRemove);
            localStorage.setItem('my_wishlist', JSON.stringify(list));

            this.savedJobs = this.savedJobs.filter(job => String(job.id) !== idToRemove);
        },

        goToDetails(jobId) {
            window.location.href = `/job-details?id=${jobId}`;
        },

        openApplyModal(job) {
            if (!AuthModel.isLoggedIn()) {
                this.showLoginNotification = true;

                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);

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
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
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
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
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
}).mount('#wishlist-app');
