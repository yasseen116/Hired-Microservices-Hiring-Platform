document.addEventListener("DOMContentLoaded", function () {
    const userJson = localStorage.getItem('user');

    // Select the Profile Link from your _base.html
    const profileLink = document.querySelector('.nav-profile-link');

    if (userJson && profileLink) {
        const user = JSON.parse(userJson);

        // If the user is a PROVIDER, change the link to Dashboard
        if (user.role === 'provider') {
            profileLink.href = '/dashboard';
            profileLink.title = "Go to Dashboard";
        }
    }
});