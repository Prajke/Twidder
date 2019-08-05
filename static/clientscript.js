
window.onload = function() {

  if(localStorage.getItem("token") == null){
    document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    document.getElementById("menu").innerHTML = null;
  }
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
          Swal.fire("Another user has logged in. Logging out.");
          localStorage.removeItem("token");
          localStorage.removeItem("currentView");
          onload();
        }
        if(obj.message == "Update graph")
        {
            var chartData = JSON.parse(obj.data)
            updateChart(chartData)
        }
    }

    if(localStorage.getItem("currentView") == null ||  localStorage.getItem("currentView") == "homeview") {
      changeView("content", "homeview", 2);
    }
    else
    {
      changeView("content", "homeview", 3);
    }
  }
};

function request(method, location, content, callback)//function
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

function changeView(container, content, setting) {
  document.getElementById(container).innerHTML = document.getElementById(content).innerHTML;
  if(content == "homeview"){
    if (setting == 1 || setting ==3 ) {

      if (setting == 3){
        document.getElementById("menu").innerHTML = document.getElementById("menuview").innerHTML;
        var email = localStorage.getItem("currentView");
      }
      else{
        var email = document.getElementById('searchinput').value.toLowerCase();
      }


      request("GET","/Get_user_data_by_email/", email,function(obj){
        if(obj.success){
          localStorage.setItem("currentView", email)
          loadUser(obj);
        }
        else{
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
    else if (setting == 2){
      document.getElementById("menu").innerHTML = document.getElementById("menuview").innerHTML;
      localStorage.setItem("currentView", "homeview");

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
};

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

function login(email,password){

  var useraccount = {
    email:email.toLowerCase(),
    password:password,
  };

  request("POST", "/sign_in", useraccount,function(obj){
    if(obj.success){
      localStorage.setItem("token", obj.data);
      onload();
    }
    else{
      Swal.fire(obj.message);
    }
  });
};

function logout(){
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
};

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

function changePassword(form){
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

function loadUser(person){

    document.getElementById("email").innerHTML = person.data.email;
    document.getElementById("firstname").innerHTML = person.data.firstname + " " + person.data.familyname;
    //document.getElementById("familyname").innerHTML = person.data.familyname;
    //document.getElementById("gender").innerHTML = person.data.gender;
    document.getElementById("country").innerHTML = person.data.country +" , " + person.data.city;
    //document.getElementById("city").innerHTML = person.data.city;

    request("GET","/update_graph/"," ", function(obj){
      console.dir(obj.message);
    });
}

function loadMessage(messages){
    messages.reverse();
    document.getElementById("wallMessages").innerHTML = " ";
    for (var i =0; i < messages.length; i++) {
          formatMessage(JSON.parse(messages[i]));
    }
}

function formatMessage(message){
    document.getElementById("wallMessages").innerHTML += "<li><h1>"+message.sender + "</h1></br><p>"+ message.message + "</p><hr></li>";
}

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
