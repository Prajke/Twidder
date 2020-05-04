//Actions occuring when the webpage is loaded/refreshed
window.onload = function() {

  //If no token has been generated, the welcome page will be displayed
  if(localStorage.getItem("token") == null){
    document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    document.getElementById("menu").innerHTML = null;
  }
  //If the user has logged in and received a token a websocket will be created and the profile page will be displayed
  else{

    var ws = new WebSocket("ws://127.0.0.1:5000/init_socket")
    ws.onopen = function (event) {
      var data = {"token": localStorage.getItem("token")};
      ws.send(JSON.stringify(data));
    }
    ws.onmessage = function (msg) {
        var obj = JSON.parse(msg.data);

        if(!obj.success)
        {
          Swal.fire("Your userprofile is used in another session. Logging out.");
          localStorage.removeItem("token");
          localStorage.removeItem("currentView");
          onload();
        }
        /* Used for updating a live graph
        if(obj.message == "Update graph")
        {
            var chartData = JSON.parse(obj.data)
            updateChart(chartData)
        }
        */
    }

    //Prevents the current view to be changed after the webpage is loaded
    if(localStorage.getItem("currentView") == "profileview" ||  localStorage.getItem("currentView") == "passwordview") 
    { 
      changeView("content", localStorage.getItem("currentView"), 2);
    }
    else
    {
      changeView("content", "profileview", 3);
    }
  }
};

//Sends requests based on the method. Also handles the retrieved content based on a callback function.
function request(method, location, content, callback)
{
  var xhttp = new XMLHttpRequest();
  if (method == "POST"){
    xhttp.open(method, location, true);
    xhttp.setRequestHeader('Token', localStorage.getItem("token"));
    xhttp.setRequestHeader('Content-type', 'application/json');
    var obj = JSON.stringify(content);
    xhttp.send(obj);
  }
  else if(method == "GET"){
    xhttp.open(method, location + content, true);
    xhttp.setRequestHeader('Token', localStorage.getItem("token"));
    xhttp.send();
  }

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      response = this.responseText;
      var obj = JSON.parse(response);
      callback(obj);
    }
  };
};

//Changes the current view displayed on the webpage by loading htlm contents from scripts into divs.
function changeView(container, content, setting) {
  document.getElementById(container).innerHTML = document.getElementById(content).innerHTML;

  //Setting 1 or 3 indicates that information shall be retrieved from another userprofile, not from the active user.
  if (setting == 1 || setting ==3 ) {

    //Setting 3 indicates that the email shall be received from local storage "currentView".
    if (setting == 3){
      document.getElementById("menu").innerHTML = document.getElementById("navbar").innerHTML;
      var email = localStorage.getItem("currentView");
    }
    //Setting 1 indicates that the email shall be received from the search input.
    else{
      var email = document.getElementById('searchinput').value.toLowerCase();
    }

    //User data and messages of the userprofile connected with the selected email are retrieved from the database.

    request("GET","/Get_user_data_by_email/", email,function(obj){
      if(obj.success){
        localStorage.setItem("currentView", email)
        loadUser(obj);
      }
      else{
        Swal.fire(obj.message);
        onload();
      }
    });

    request("GET", "/Get_user_messages_by_email/", email, function(obj){
      if(obj.success){
        loadMessage(obj.data);
      }
      else{
        onload();
      }
    });
  }
  //Setting 2 indicates that either the password or profile page shall be displayed
  else if (setting == 2){
    document.getElementById("menu").innerHTML = document.getElementById("navbar").innerHTML;
    localStorage.setItem("currentView", content);
    
    //Only loads information of the active userprofile when the view is changed to the profile page
    if(content == "profileview"){
      //User data and messages of the userprofile connected to the current token, thus identicating the active userprofile, are retrieved from the database,
      request("GET", "/Get_user_data_by_token/", " ", function(obj){
        if(obj.success){
          loadUser(obj);
        }
      });

      request("GET", "/Get_user_messages_by_token/", " ", function(obj){
        loadMessage(obj.data);
      });
    }
  }
}

//Updates the messages of the userprofile currently displayed.
function updateView(){
  request("GET","/Get_user_messages_by_email/", document.getElementById('email'), function(obj){
    if(obj.success){
      loadMessage(obj.data);
    }
    else{
      onload();
    }
  });
}

//Checks if the email and password combination is correct.
function login(email,password){

  var useraccount = {
    email:email.toLowerCase(),
    password:password,
  };

  //If the combination is correct a unique token used for authentication is generated by the server and are set in the local storage. 
  //The token enables the privilege of accessing data from the database.
  request("POST", "/sign_in", useraccount,function(obj){
    if(obj.success){
      localStorage.setItem("token", obj.data);
      localStorage.setItem("currentView", "profileview") 
      onload();
    }
    else{
      Swal.fire(obj.message);
    }
  });
};

//Signs out the user by removing the token, thus disabling the privilege of accessing data.
function logout(){
  Swal.fire({
    title: 'Are you sure you want to sign out?',
    text: "",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Yes'
  }).then((result) => {
    if (result.value) {
      Swal.fire(
        'Signing out!',
        'You have been signed out.',
        'success'
      )
      var currenttoken = localStorage.getItem("token");

      var token = {
        token:currenttoken
      };
      
      request("POST", "/sign_out", token, function(obj){
        if(obj.success){
          localStorage.removeItem("token");
          localStorage.removeItem("currentView");
          onload();
        }
        else{
          console.dir(obj.message);
        }
      });
    }
  })
  
};

//Creates account based on the information specified in the form.
function createAccount(form){
  if(form.password.value != form.confirmpassword.value) {
    form.confirmpassword.setCustomValidity("Passwords Don't Match");
  }
  else {
    var useraccount = {
      email:form.email.value.toLowerCase(),
      password:form.password.value,
      firstname:form.firstname.value,
      familyname:form.lastname.value,
      gender: form.gender.value,
      city:form.city.value,
      country:form.country.value
    };
    console.dir(useraccount);

    //If a account is created successfully, the created userprofile is automatically logged in.
    request("POST", "/sign_up", useraccount, function(obj){
      if(obj.success){
        Swal.fire(obj.message);
        login(form.email.value.toLowerCase(), form.password.value);
      }
      else{
        Swal.fire(obj.message);
      }
    });
  }
};

//Changes the password of the active userprofile based on the information in a specific form.
function changePassword(form){

  //Verifies that the password specified matches with the currently active password.
  if(form.newpassword.value != form.confirmpassword.value) {
    form.confirmpassword.setCustomValidity("Passwords Don't Match");
  }
  else {
    var useraccount = {
      oldPassword:form.oldpassword.value,
      newPassword:form.newpassword.value
    };

    var xhttp = new XMLHttpRequest();
    request(xhttp, "POST", "/Change_password", useraccount, function(obj){
      if(obj.success){
        Swal.fire(obj.message);
        onload();
      }
      else{
        Swal.fire(obj.message);
      }
    });
  }
}

//Displays a specific userprofile by loading information to certain elements in the html.
function loadUser(user){

    document.getElementById("email").innerHTML = user.data.email;
    document.getElementById("fullname").innerHTML = user.data.firstname + " " + user.data.familyname;
    //document.getElementById("familyname").innerHTML = user.data.familyname;
    //document.getElementById("gender").innerHTML = user.data.gender;
   // document.getElementById("country").innerHTML = user.data.country +" , " + user.data.city;
    //document.getElementById("city").innerHTML = user.data.city;

    request("GET","/update_graph/"," ", function(obj){
      console.dir(obj.message);
    });
}

//Displays the messages by loading the information of each message to certain elements in the html.
function loadMessage(messages){
    messages.reverse();
    document.getElementById("wallMessages").innerHTML = " ";
    for (var i =0; i < messages.length; i++) {
          formatMessage(JSON.parse(messages[i]));
    }
}

//Format and loads the information of each message to certain elements in the html.
function formatMessage(message){
   document.getElementById("wallMessages").innerHTML +=  document.getElementById("postformat").innerHTML 
   document.getElementById("sender").innerHTML = message.sender
   document.getElementById("message").innerHTML = message.message
   document.getElementById("sender").removeAttribute("id");
   document.getElementById("message").removeAttribute("id");
}

//Create a message for a specific userprofile and updates the currently displayed messages.
function postMessage(form){
  var useraccount = {
    toEmail: document.getElementById('email').innerHTML,
    content: form.wallinput.value
  };

  request("POST", "/Post_message", useraccount, function(obj){
    if(obj.success){
      console.dir(obj.message);
      updateView();
    }
    else{
      console.dir(obj.message);
    }
  });
}


//OLD function
function updateChart(data)
{
    var myChart = document.getElementById('myChart').getContext('2d');

    var newChart = new Chart(myChart, {
      type:'horizontalBar',
      data:{
        labels:['Total users','Online users','Male users', 'Female users'],
        datasets:[{
          data:[
            data.users,
            data.activeusers,
            data.males,
            data.females
          ],
          backgroundColor:'green',
          borderWidth:0,
          borderColor:'black',
          hoverBorderWidth:1,
          hoverBorderColor:'black'
        }],
        options: {
          responsive: true,
          maintainAspectRatio: false,
          title: {
            display: false
          },
          scales: {
            yAxes: [{
              display: true,
      	       ticks: {
        	        beginAtZero: true
                }
              }]
            }
          }
      }
    })
};
