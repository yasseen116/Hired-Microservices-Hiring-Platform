const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            jobs: [],
            searchTerm: '',
            isLoading: true,
            error: null,

            companies: [],
            isTeleporting: false,

            // Modal & Application States
            showApplyModal: false,
            selectedJobForApp: null,
            newCvName: null,
            newCvFile: null,
            showLoginNotification: false,
            isApplying: false,
            showSuccessNotification: false,
            successMessage: ''
        };
    },

    async mounted() {
        // 1. Load Real Jobs from API
        await this.loadJobs();

        // 2. Load Companies using existing Model
        this.companies = CompanyModel.getTopCompanies();

        const originals = CompanyModel.getTopCompanies();
        this.companies = [...originals, ...originals];

        const container = document.querySelector('.companies-grid');
        if (container) {
            container.addEventListener('scroll', this.handleInfiniteScroll);
        }
    },

    computed: {
        filteredJobs() {
            if (!this.jobs) return [];
            if (!this.searchTerm) return this.jobs;
            const term = this.searchTerm.toLowerCase();
            return this.jobs.filter(job =>
                (job.title && job.title.toLowerCase().includes(term)) ||
                (job.company && job.company.toLowerCase().includes(term)) ||
                (job.location && job.location.toLowerCase().includes(term))
            );
        }
    },

    methods: {
        async loadJobs() {
            try {
                this.isLoading = true;

                // Fetch jobs using the JobModel
                this.jobs = await JobModel.getAll();

                console.log("Jobs loaded via MVC Model");
            } catch (err) {
                this.error = "Could not load jobs.";
            } finally {
                this.isLoading = false;
            }
        },

        handleInfiniteScroll(e) {
            const container = e.target;
            if (this.isTeleporting) return;

            const oneSetWidth = container.scrollWidth / 2;

            if (container.scrollLeft >= oneSetWidth) {
                this.isTeleporting = true;
                container.scrollLeft -= oneSetWidth;
                this.isTeleporting = false;
            }
            else if (container.scrollLeft <= 0) {
                this.isTeleporting = true;
                container.scrollLeft += oneSetWidth;
                this.isTeleporting = false;
            }
        },

        scrollCompanies(direction) {
            const container = document.querySelector('.companies-grid');
            const scrollAmount = 165;

            if (direction === 'left') {
                container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            } else {
                container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
        },

        showJobDetails(job) {
            window.location.href = `/job-details?id=${job.id}`;
        },

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

        handleCvUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.newCvName = file.name;
                this.newCvFile = file;
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
});

app.mount('#app');
