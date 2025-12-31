const { createApp } = Vue;

createApp({
    data() {
        return {
            email: '',
            password: '',
            rememberMe: false,
            isLoading: false,
            errorMessage: null
        }
    },

    mounted() {
        // Redirect if already logged in
        const userJson = localStorage.getItem('user');
        if (userJson) {
            const user = JSON.parse(userJson);
            if (user.role === 'provider') {
                window.location.href = '/dashboard';
            } else {
                window.location.href = '/';
            }
        }
    },

    methods: {
        async handleLogin() {
            this.isLoading = true;
            this.errorMessage = null;

            if (!this.email || !this.password) {
                this.errorMessage = "Please fill in all fields.";
                this.isLoading = false;
                return;
            }

            try {
                console.log("Attempting login for:", this.email);

                // Call AuthModel (which calls /api/auth/login)
                const data = await AuthModel.login(this.email, this.password);

                // Save session
                AuthModel.saveSession(data);

                // Redirect based on role
                if (data.user.role === 'provider') {
                    window.location.href = '/dashboard';
                } else {
                    window.location.href = '/';
                }

            } catch (error) {
                console.error(error);
                this.errorMessage = error.message || "Invalid email or password.";
                this.isLoading = false;
            }
        }
    },

    compilerOptions: {
        delimiters: ['[[', ']]']
    }
}).mount('#app');