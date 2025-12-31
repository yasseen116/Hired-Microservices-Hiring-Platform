const API = "";  // Same origin - no CORS issues
const UPLOADS_BASE = `${API}/api/uploads`;
const JOB_UPLOADS_BASE = `${API}/api/job-uploads`;
const APP_UPLOADS_BASE = `${API}/api/app-uploads`;

const resolveUploadUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('data:') || path.startsWith('blob:')) {
        return path;
    }
    if (path.startsWith('http://') || path.startsWith('https://')) {
        try {
            const url = new URL(path);
            if (url.pathname.startsWith('/uploads/')) {
                return `${UPLOADS_BASE}${url.pathname.slice('/uploads'.length)}`;
            }
        } catch (error) {
            return path;
        }
        return path;
    }
    if (path.startsWith('/uploads/')) {
        return `${UPLOADS_BASE}${path.slice('/uploads'.length)}`;
    }
    return path;
};

const resolveJobUploadUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('data:') || path.startsWith('blob:')) {
        return path;
    }
    if (path.startsWith('http://') || path.startsWith('https://')) {
        try {
            const url = new URL(path);
            if (url.pathname.startsWith('/uploads/')) {
                return `${JOB_UPLOADS_BASE}${url.pathname.slice('/uploads'.length)}`;
            }
        } catch (error) {
            return path;
        }
        return path;
    }
    if (path.startsWith('/uploads/')) {
        return `${JOB_UPLOADS_BASE}${path.slice('/uploads'.length)}`;
    }
    return path;
};

const resolveAppUploadUrl = (path) => {
    if (!path) return null;
    if (path.startsWith('data:') || path.startsWith('blob:')) {
        return path;
    }
    if (path.startsWith('http://') || path.startsWith('https://')) {
        try {
            const url = new URL(path);
            if (url.pathname.startsWith('/uploads/')) {
                return `${APP_UPLOADS_BASE}${url.pathname.slice('/uploads'.length)}`;
            }
        } catch (error) {
            return path;
        }
        return path;
    }
    if (path.startsWith('/uploads/')) {
        return `${APP_UPLOADS_BASE}${path.slice('/uploads'.length)}`;
    }
    return path;
};

const normalizeJob = (job) => {
    if (!job) return job;
    const rawLogoUrl = job.logo_url || job.logoUrl || null;
    return {
        ...job,
        logoUrl: resolveJobUploadUrl(rawLogoUrl),
        logoUrlRaw: rawLogoUrl
    };
};

// ========== JOB MODEL ==========
const JobModel = {
    async getAll(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${API}/api/jobs?${params}`);
        if (!response.ok) throw new Error('Failed to fetch jobs');
        const data = await response.json();
        return Array.isArray(data) ? data.map(normalizeJob) : [];
    },

    async getById(id) {
        const response = await fetch(`${API}/api/jobs/${id}`);
        if (!response.ok) throw new Error("Job not found");
        return normalizeJob(await response.json());
    },

    async getSimilar(id) {
        const response = await fetch(`${API}/api/jobs/${id}/similar`);
        if (!response.ok) return [];
        const data = await response.json();
        return Array.isArray(data) ? data.map(normalizeJob) : [];
    },

    async create(formData) {
        const response = await fetch(`${API}/api/jobs`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Failed to create job');
        return normalizeJob(await response.json());
    },

    async update(id, data) {
        const response = await fetch(`${API}/api/jobs/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Failed to update job');
        return normalizeJob(await response.json());
    },

    async delete(id) {
        const response = await fetch(`${API}/api/jobs/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete job');
        return response.json();
    }
};

// ========== AUTH MODEL ==========
const AuthModel = {
    async login(email, password) {
        const form = new FormData();
        form.append('email', email);
        form.append('password', password);
        const response = await fetch(`${API}/api/auth/login`, {
            method: 'POST',
            body: form
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        return response.json();
    },

    async signup(email, password, name, role = "seeker", companyName = null) {
        const form = new FormData();
        form.append('email', email);
        form.append('password', password);
        form.append('name', name);
        form.append('role', role);
        if (companyName) form.append('company_name', companyName);
        const response = await fetch(`${API}/api/auth/signup`, {
            method: 'POST',
            body: form
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Signup failed');
        }
        return response.json();
    },

    async getProfile() {
        const response = await fetch(`${API}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${this.getToken()}` }
        });
        if (!response.ok) throw new Error('Session expired');
        return response.json();
    },

    async updateProfile(data) {
        const form = new FormData();
        if (data.job_title) form.append('job_title', data.job_title);
        if (data.skills) form.append('skills', JSON.stringify(data.skills));
        if (data.phone) form.append('phone', data.phone);
        if (data.location) form.append('location', data.location);
        if (data.about) form.append('about', data.about);
        if (data.experience) form.append('experience', JSON.stringify(data.experience));
        if (data.education) form.append('education', JSON.stringify(data.education));

        const response = await fetch(`${API}/api/auth/profile`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${this.getToken()}` },
            body: form
        });
        if (!response.ok) throw new Error('Failed to update profile');
        return response.json();
    },

    async uploadPhoto(file) {
        const form = new FormData();
        form.append('file', file);
        const response = await fetch(`${API}/api/auth/profile/photo`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.getToken()}` },
            body: form
        });
        if (!response.ok) throw new Error('Failed to upload photo');
        return response.json();
    },

    async deletePhoto() {
        const response = await fetch(`${API}/api/auth/profile/photo`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to delete photo');
        return response.json();
    },

    async uploadCV(file) {
        const form = new FormData();
        form.append('file', file);
        const response = await fetch(`${API}/api/auth/profile/cv`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${this.getToken()}` },
            body: form
        });
        if (!response.ok) throw new Error('Failed to upload CV');
        return response.json();
    },

    async deleteCV() {
        const response = await fetch(`${API}/api/auth/profile/cv`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to delete CV');
        return response.json();
    },

    saveSession(data) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
    },

    getToken() {
        return localStorage.getItem('token');
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    logout() {
        localStorage.clear();
        window.location.href = '/login';
    }
};

// ========== APPLICATION MODEL ==========
const ApplicationModel = {
    async submit(jobId, cvFile = null) {
        const form = new FormData();
        form.append('job_id', jobId);
        if (cvFile) form.append('cv', cvFile);

        const response = await fetch(`${API}/api/applications`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${AuthModel.getToken()}` },
            body: form
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit application');
        }
        return response.json();
    },
    async submitWithExistingCv(jobId) {
        const profile = await AuthModel.getProfile();
        if (!profile.cvUrl) {
            throw new Error('No CV found in your profile.');
        }
        const cvUrl = resolveUploadUrl(profile.cvUrl);
        const response = await fetch(cvUrl);
        if (!response.ok) {
            throw new Error('Failed to load your CV file.');
        }
        const blob = await response.blob();
        const filename = profile.cvName || 'cv.pdf';
        const file = new File([blob], filename, {
            type: blob.type || 'application/pdf'
        });
        return this.submit(jobId, file);
    },

    async getMyApplications() {
        const response = await fetch(`${API}/api/applications/my`, {
            headers: { 'Authorization': `Bearer ${AuthModel.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to fetch applications');
        return response.json();
    },

    async checkIfApplied(jobId) {
        const response = await fetch(`${API}/api/applications/check/${jobId}`, {
            headers: { 'Authorization': `Bearer ${AuthModel.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to check application status');
        return response.json();
    },

    async getJobApplications(jobId) {
        const response = await fetch(`${API}/api/applications/job/${jobId}`, {
            headers: { 'Authorization': `Bearer ${AuthModel.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to fetch job applications');
        return response.json();
    },

    async updateStatus(appId, status) {
        const response = await fetch(`${API}/api/applications/${appId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AuthModel.getToken()}`
            },
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error('Failed to update status');
        return response.json();
    },

    async withdraw(appId) {
        const response = await fetch(`${API}/api/applications/${appId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${AuthModel.getToken()}` }
        });
        if (!response.ok) throw new Error('Failed to withdraw application');
        return response.json();
    }
};

// ========== COMPANY MODEL (Static Data) ==========
const CompanyModel = {
    getTopCompanies() {
        return [
            { name: "LC Waikiki", logo: "../static/images/companies/lcwaikiki.png" },
            { name: "Elsewedy Electric", logo: "../static/images/companies/elsewedy.png" },
            { name: "Breadfast", logo: "../static/images/companies/breadfast.png" },
            { name: "IBM", logo: "../static/images/companies/ibm.png" },
            { name: "Microsoft", logo: "../static/images/companies/microsoft.png" },
            { name: "Etoile", logo: "../static/images/companies/etoile.webp" },
            { name: "Google", logo: "../static/images/companies/google.png" },
            { name: "ValU", logo: "../static/images/companies/valu.webp" },
            { name: "Juhayna", logo: "../static/images/companies/juhayna.png" },
            { name: "CIB", logo: "../static/images/companies/cib.png" },
            { name: "Orascom", logo: "../static/images/companies/orascom.png" },
            { name: "Fawry", logo: "../static/images/companies/fawry.png" },
            { name: "Palm Hills", logo: "../static/images/companies/palm.png" },
            { name: "Vodafone", logo: "../static/images/companies/vodafone.png" },
            { name: "NBE", logo: "../static/images/companies/nbe.png" },
            { name: "Edita", logo: "../static/images/companies/edita.png" },
            { name: "Etisalat", logo: "../static/images/companies/etisalat.png" },
            { name: "Raya", logo: "../static/images/companies/raya.png" },
            { name: "AstraZeneca", logo: "../static/images/companies/astrazeneca.png" },
            { name: "Mountain View", logo: "../static/images/companies/mountainview.webp" },
            { name: "Tarek Nour", logo: "../static/images/companies/tareknour.png" },
            { name: "British Council", logo: "../static/images/companies/britishcouncil.png" }
        ];
    }
};
