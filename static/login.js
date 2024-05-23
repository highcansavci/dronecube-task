window.addEventListener("DOMContentLoaded", (event) => {
	const container = document.getElementById('container');
    const signUpButton = document.getElementById('signUp');
    if (signUpButton) {
      signUpButton.addEventListener('click', () => {
		  container.classList.add("right-panel-active");
	  });
    }
	const signInButton = document.getElementById('signIn');
	if (signUpButton) {
      signInButton.addEventListener('click', () => {
		  container.classList.remove("right-panel-active");
	  });
    }
});



