function myFunction()
{
  var email = {
    email:"Niklas.allard96@hotmail.com"
  };
  var xhttp = new XMLHttpRequest();
  request(xhttp, "/test", email);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      response = this.responseText;
      var obj = JSON.parse(response);
      console.dir(response);
      console.dir(obj);
      document.getElementById("content").innerHTML = obj.message;
    //  return "test";
    }
  };
  //console.dir(obj);
  //document.getElementById("content").innerHTML = obj.success;
  /*var obj = {name:"n@hotmail.com", password:"123"};
  document.getElementById("content").innerHTML = request("POST", "/login", obj)*/
};


function request(location, content, callback)
{
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", location, true);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.setRequestHeader('Token', "123");
  var obj = JSON.stringify(content);
  xhttp.send(obj);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      response = this.responseText;
      var obj = JSON.parse(response);
      callback(obj);
    }
  };
};


function getName() {
    request("/test", "hej", function(obj){
     alert(obj.success); });
};

/*var elements = document.getElementsByClassName("formVal");
var formData = new FormData();
for(var i=0; i<elements.length; i++)
{
    formData.append(elements[i].name, elements[i].value);
}*//*
var params = 'password=ipsum&username=binny';

//BEHÖVS HEADER ?
var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function()
    {
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
        {
              document.getElementById("content").innerHTML = this.responseText;
        }
    }
    xmlHttp.open("POST", "/login",true);
    xmlHttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xmlHttp.send(params);*/
