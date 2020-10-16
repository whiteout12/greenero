function create_friend_req(userid, username){
  console.log(userid)

  var url = '/relations/request'
  fetch(url,{
    method : 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'      
    },        
    body : JSON.stringify({
      "FriendUserID": userid
    })
  })
  .then(function (response) {

    console.log(response);
    return response.json();
  })
  .then(function (data) {
    console.log(data);
    get_user_relations();
    document.getElementById("user-search").innerHTML +=  "<br>"+data.message
    
  });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function list_users(user_search){
  console.log(user_search)
  if(!user_search){
    user_search = '*'
  }
  console.log(user_search)
  var url = '/users/'
  fetch(url+user_search)
  .then(function (response) {
    
    return response.json();
  })
  .then(function (data) {
    var resultString = "<body><table style=\"text-align:left;\" class=\"table-striped\">"
    if(data.length>0){
      
      for (var i = 0; i < data.length; i++) {
        
        console.log(data[i].username)
        console.log(data[i].userid)
        
        resultString += "<tr><td>"+data[i].username+"<\/td><th><input type=\"button\" class=\"btn btn-sm btn-primary\" onclick=\"create_friend_req("+data[i].userid+",\'"+data[i].username+"\')\" value=\"Friend request\"\/><\/th><th><\/th><\/tr>";

        /*resultString += "<tr><td>"+data[i].username+"<\/td><th><input type=\"button\" class=\"btn btn-sm btn-primary\" onclick=\"build_change_user_window()\" value=\"Friend request\"\/><\/th><th><\/th><\/tr>";
        */
      };

    }else{
      resultString = "no results"
    }
    resultString += "<\/table><\/body>"
    /*document.getElementById("SW").innerHTML +=  `${JSON.stringify(data)}`*/
    document.getElementById("user-search").innerHTML =  resultString
  });
}

function accept_friend_req(userid){
  console.log(userid)

  var url = '/relations/accept'
  fetch(url,{
    method : 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'      
    },        
    body : JSON.stringify({
      "FriendUserID": userid
    })
  })
  .then(function (response) {

    console.log(response);
    return response.json();
  })
  .then(function (data) {
    console.log(data);
    get_user_relations();
    document.getElementById("user-search").innerHTML +=  "<br>"+data.message
  });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function reject_friend_req(userid){
  console.log(userid)

  var url = '/relations/reject'
  fetch(url,{
    method : 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'      
    },        
    body : JSON.stringify({
      "FriendUserID": userid
    })
  })
  .then(function (response) {

    console.log(response);
    return response.json();
  })
  .then(function (data) {
    console.log(data);
    get_user_relations();
    document.getElementById("user-search").innerHTML +=  "<br>"+data.message
  });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function withdraw_friend_req(userid){
  console.log(userid)

  var url = '/relations/withdraw'
  fetch(url,{
    method : 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'      
    },        
    body : JSON.stringify({
      "FriendUserID": userid
    })
  })
  .then(function (response) {

    console.log(response);
    return response.json();
  })
  .then(function (data) {
    console.log(data);
    get_user_relations();
    document.getElementById("user-search").innerHTML +=  "<br>"+data.message
  });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function unfriend(userid){
  console.log(userid)

  var url = '/relations/unfriend'
  fetch(url,{
    method : 'POST',
    headers: {
      'Content-Type': 'application/json;charset=utf-8'      
    },        
    body : JSON.stringify({
      "FriendUserID": userid
    })
  })
  .then(function (response) {

    console.log(response);
    return response.json();
  })
  .then(function (data) {
    console.log(data);
    get_user_relations();
    document.getElementById("user-search").innerHTML +=  "<br>"+data.message
  });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}


function get_user_relations(){
  console.log("get_user_relations")

  var url = '/relations/getrelations'
  fetch(url)
  .then(function (response) {
    
    return response.json();
  })
  .then(function (data) {
    var pending_to_me = "<br><h4>Pending</h4><body><h5>Awaiting your confirmation</h5><table style=\"text-align:left;\" class=\"table-responsive table-striped\">"
    var pending_by_me = "<br><body><h5>Sent friend requests</h5><table style=\"text-align:left;\" class=\"table-responsive table-striped\">"
    var friends = "<br><h4>Friends</h4><body><h5></h5><table style=\"text-align:left;\" class=\"table-responsive table-striped\">"
    console.log(data)
    console.log(data.request_by_me.length)
    
    for (var i = 0; i < data.request_to_me.length; i++) {
      console.log(i)
      
      pending_to_me += "<tr><td>"+data.request_to_me[i].username+"<\/td><th><input type=\"button\" class=\"btn btn-sm btn-success\" onclick=\"accept_friend_req("+data.request_to_me[i].id+")\" value=\"Accept\"\/><\/th><th><input type=\"button\" class=\"btn btn-sm btn-danger\" onclick=\"reject_friend_req("+data.request_to_me[i].id+")\" value=\"Reject\"\/><\/th><\/tr>"; 
    };

    for (var i = 0; i < data.request_by_me.length; i++) {
      console.log(i)
      
      pending_by_me += "<tr><td>"+data.request_by_me[i].username+"<\/td><th><input type=\"button\" class=\"btn btn-sm btn-danger\" onclick=\"withdraw_friend_req("+data.request_by_me[i].id+")\" value=\"Withdraw request\"\/><\/th><th><\/th><\/tr>"; 
    };

    for (var i = 0; i < data.friends.length; i++) {
      console.log(i)
      
      friends += "<tr><td>"+data.friends[i].username+"<\/td><th><input type=\"button\" class=\"btn btn-sm btn-danger\" onclick=\"unfriend("+data.friends[i].id+")\" value=\"Unfriend\"\/><\/th><th><\/th><\/tr>"; 
    };
    
    document.getElementById("pending_friends").innerHTML =  pending_to_me
    document.getElementById("pending_friends").innerHTML +=  pending_by_me
    document.getElementById("list_friends").innerHTML = friends
    

  });
}



