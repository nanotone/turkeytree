$(document).ready(function(){
	$('#loginButton').click(function(e){
		e.preventDefault();
		$('#loginFormContainer').show();
		$('#registerForm').hide();
	});

	$('#registerButton').click(function(e){
		e.preventDefault();

		if($('#registerForm').length == 0) {
			$.get('/register', function(data){
				$('#loginRegister').append(data);
			});
		}
		else {
			$('#registerForm').show();
		}

		$('#loginFormContainer').hide();
	});

	$('#loginForm').submit(function(e) {
		e.preventDefault();
		$.post('/login', $(this).serialize(), function(data) {
			if (data == 'ok') {
				window.location.href = '/';
			}
			else {
				$('#loginWrong').show();
			}
		});
	});

	$('.close-button').click(function(e){
		e.preventDefault();

		$(this).parent().hide();
	});
});
