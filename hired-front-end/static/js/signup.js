const { createApp } = Vue;

createApp({
    data() {
        return {
            fullname: '',
            email: '',
            password: '',
            confirmPassword: '',
            role: 'seeker',
            companyName: '',
            isLoading: false,
            errorMessage: null,
        }
    },

    methods: {
        async handleSignup() {
            this.isLoading = true;
            this.errorMessage = null;

            // Validation
            if (this.password !== this.confirmPassword) {
                this.errorMessage = "Passwords do not match!";
                this.isLoading = false;
                return;
            }

            if (this.password.length < 6) {
                this.errorMessage = "Password must be at least 6 characters!";
                this.isLoading = false;
                return;
            }

            if (this.role === 'provider' && !this.companyName.trim()) {
                this.errorMessage = "Company name is required for providers!";
                this.isLoading = false;
                return;
            }

            try {
                console.log("Attempting signup for:", this.email, "as", this.role);

                // Call AuthModel with role and company
                const data = await AuthModel.signup(
                    this.email,
                    this.password,
                    this.fullname,
                    this.role,
                    this.role === 'provider' ? this.companyName : null
                );

                // Save session
                AuthModel.saveSession(data);

                // Redirect based on role
                if (this.role === 'provider') {
                    window.location.href = '/dashboard';
                } else {
                    window.location.href = '/profile';
                }

            } catch (error) {
                console.error(error);
                this.errorMessage = error.message || "Something went wrong during signup.";
                this.isLoading = false;
            }
        }
    },

    compilerOptions: {
        delimiters: ['[[', ']]']
    }
}).mount('#app');