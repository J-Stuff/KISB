window.addEventListener('load', () => {
    const queryString = window.location.search;
    const params = new URLSearchParams(queryString);
    
    params.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });

    const logoutNotice = document.getElementById('session-notice');
    const logoutQS = params.get('loggedout');
        
    
    if (logoutQS === 'true') {
            logoutNotice.innerHTML = 'You have been logged out.';
        }
    else {
        logoutNotice.innerHTML = '';
    }
});
