$(document).ready(function(){
	$('#loginButton').click(function(e){
		e.preventDefault();

		if($('#loginForm').length == 0) {
			$.get('/login', function(data){
				$('#loginRegister').append(data);
			});
		}
		else {
			$('#loginForm').show();
		}
		
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

		$('#loginForm').hide();
	});

	$('.close-button').click(function(e){
		e.preventDefault();

		$(this).parent().hide();
	});
});