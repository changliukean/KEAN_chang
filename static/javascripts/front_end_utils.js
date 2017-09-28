


function submit_login_info(){
  // alert('submit!!');
  user_input_email = document.getElementById('inputEmail').value;
  user_input_password = document.getElementById('inputPassword').value;
  // alert(user_input_email)
  // alert(user_input_password);
  $.ajax({
		    type:'GET',
		    url:"/login/",
		    dataType:'json',
		   	data: {'user_input_email': user_input_email, 'user_input_password': user_input_password},
		    success:function(data)
		        {
              // alert('yeah!');
              // var form_div = document.getElementById('login_form');
              // form_div.style.display = 'none';
              // var welcome_div = document.getElementById('welcome_div');
              // welcome_div.style.display = 'block';
              //
              // var welcome_user = document.getElementById('welcome_user');
              //
              // welcome_user.innerHTML = data[0].user_email;

              window.location.replace('/sys_mainpage/'+data[0].user_email);
              

		        },
		    error:function(data)
		    {
		        alert("User email not found.");
		    }
		});
}
