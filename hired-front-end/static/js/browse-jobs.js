const { createApp } = Vue;

createApp({
    data() {
        return {
            isLoading: true,
            allJobs: [], // Will now store data from FastAPI
            errorMessage: null, // To show API errors

            // Search & Filters
            searchQuery: '',
            filters: {
                type: [],
                city: [],
                category: [],
                company: [],
                salaryMin: 0,
                salaryMax: 100000
            },

            // Pagination
            page: 1,
            pageSize: 12,

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

    computed: {
        filteredJobs() {
            // Start with all jobs loaded from API
            let result = this.allJobs;

            // 1. SEARCH FILTER
            if (this.searchQuery) {
                const q = this.searchQuery.toLowerCase();
                result = result.filter(job =>
                    job.title.toLowerCase().includes(q) ||
                    job.company.toLowerCase().includes(q)
                );
            }

            // 2. SALARY RANGE FILTER
            const min = this.filters.salaryMin;
            const max = this.filters.salaryMax;
            result = result.filter(job => {
                const s = this.parseSalary(job.salary);
                if (s == null) return true; // Include jobs with unparseable salaries
                return s >= min && s <= max;
            });

            // 3. CHECKBOX FILTERS
            // If no checkboxes selected, return current result
            if (this.filters.type.length === 0 &&
                this.filters.city.length === 0 &&
                this.filters.category.length === 0 &&
                this.filters.company.length === 0) {
                return result;
            }

            // Apply Checkbox Logic
            return result.filter(job => {
                // Map API data to Filter categories
                // Note: API might return "On-site", "Hybrid", "Remote" directly.
                const jobType = job.type || 'On-site';

                const matchesWorkplace = this.filters.type.length === 0 || this.filters.type.includes(jobType);
                const matchesCity = this.filters.city.length === 0 || this.filters.city.some(city => job.location.includes(city));
                const matchesCategory = this.filters.category.length === 0 || this.filters.category.some(cat => job.category === cat || job.category.includes(cat));
                const matchesCompany = this.filters.company.length === 0 || this.filters.company.includes(job.company);

                return matchesWorkplace && matchesCity && matchesCategory && matchesCompany;
            });
        },
        totalPages() {
            return Math.max(1, Math.ceil(this.filteredJobs.length / this.pageSize));
        },
        paginatedJobs() {
            const start = (this.page - 1) * this.pageSize;
            return this.filteredJobs.slice(start, start + this.pageSize);
        }
    },

    async mounted() {
        this.fetchJobs();

        // Capture URL Search Parameter
        const urlParams = new URLSearchParams(window.location.search);
        const searchParam = urlParams.get('search');
        if (searchParam) {
            this.searchQuery = searchParam;
        }
    },

    watch: {
        'filters.salaryMin'(val) {
            if (val < 0) this.filters.salaryMin = 0;
            if (val > 100000) this.filters.salaryMin = 100000;
            if (this.filters.salaryMin > this.filters.salaryMax) {
                this.filters.salaryMax = this.filters.salaryMin;
            }
        },
        'filters.salaryMax'(val) {
            if (val < 0) this.filters.salaryMax = 0;
            if (val > 100000) this.filters.salaryMax = 100000;
            if (this.filters.salaryMax < this.filters.salaryMin) {
                this.filters.salaryMin = this.filters.salaryMax;
            }
        },
        filteredJobs() {
            this.page = 1; // Reset to page 1 on filter change
        }
    },

    methods: {
        async fetchJobs() {
            try {
                this.isLoading = true;

                // MVC: Ask the Model for data
                this.allJobs = await JobModel.getAll();

                // Debugging
                console.log("Browse Jobs loaded via Model:", this.jobs);
            } catch (err) {
                console.error(err);
                this.error = "Could not load jobs.";
            } finally {
                this.isLoading = false;
            }
        },

        // --- EXISTING HELPER METHODS ---
        parseSalary(salaryText) {
            if (!salaryText) return null;
            try {
                let text = String(salaryText).toLowerCase();
                text = text.replace(/egp|\$|usd|eur|sar|aed|per\s*month|\/month|per\s*year|\/year|net|gross/g, '');
                text = text.replace(/[,\s]+/g, '');

                const rangeMatch = text.match(/(\d+(?:\.\d+)?[km]?)-(\d+(?:\.\d+)?[km]?)/);
                if (rangeMatch) {
                    const a = this._toNumber(rangeMatch[1]);
                    const b = this._toNumber(rangeMatch[2]);
                    return Math.min(a, b);
                }
                const singleMatch = text.match(/(\d+(?:\.\d+)?[km]?)/);
                if (singleMatch) {
                    return this._toNumber(singleMatch[1]);
                }
                return null;
            } catch { return null; }
        },
        _toNumber(val) {
            if (typeof val !== 'string') val = String(val);
            const lower = val.toLowerCase();
            if (lower.endsWith('m')) { return parseFloat(lower.slice(0, -1)) * 1_000_000; }
            if (lower.endsWith('k')) { return parseFloat(lower.slice(0, -1)) * 1_000; }
            return parseFloat(lower);
        },
        formatCurrency(n) {
            const num = Number(n) || 0;
            return new Intl.NumberFormat('en-EG', { style: 'currency', currency: 'EGP', maximumFractionDigits: 0 }).format(num);
        },

        goToDetails(jobId) {
            // Update URL to match backend ID
            window.location.href = `/job-details?id=${jobId}`;
        },

        // --- MODAL LOGIC (Kept as is, but logic will need backend update later) ---
        openApplyModal(job) {
            if (!AuthModel.isLoggedIn()) {
                this.showLoginNotification = true;
                setTimeout(() => { window.location.href = '/login'; }, 2000);
                return;
            }
            this.selectedJobForApp = job;
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
                this.handleApplicationResult({
                    success: true,
                    message: `Application sent to ${this.selectedJobForApp.company}!`
                });
            } catch (error) {
                this.handleApplicationResult({
                    success: false,
                    message: error.message || 'Failed to submit application.'
                });
            } finally {
                this.isApplying = false;
            }
        },

        async applyWithNew() {
            if (!this.newCvFile) return;
            this.isApplying = true;
            try {
                await ApplicationModel.submit(this.selectedJobForApp.id, this.newCvFile);
                this.handleApplicationResult({
                    success: true,
                    message: `Application sent to ${this.selectedJobForApp.company}!`
                });
            } catch (error) {
                this.handleApplicationResult({
                    success: false,
                    message: error.message || 'Failed to submit application.'
                });
            } finally {
                this.isApplying = false;
            }
        },

        handleApplicationResult(response) {
            if (response.success) {
                this.closeModal();
                this.successMessage = response.message;
                this.showSuccessNotification = true;
                setTimeout(() => { this.showSuccessNotification = false; }, 3000);
            } else {
                alert(response.message);
            }
        },
        scrollToTop() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },
        setPage(p) {
            const target = Math.min(Math.max(1, p), this.totalPages);
            if (target === this.page) return;
            this.page = target;
            this.scrollToTop();
        },
        nextPage() { this.setPage(this.page + 1); },
        prevPage() { this.setPage(this.page - 1); },
    },

    compilerOptions: {
        delimiters: ['[[', ']]']
    }
}).mount('#app');
