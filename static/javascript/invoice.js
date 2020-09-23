function get_user_invoices(){

var url = '/invoice/getinvoices'
fetch(url)
    .then(function (response) {
        
        return response.json();
    })
    .then(function (data) {
      var sent = "<br><h4>Claims</h4><h5>Pending</h5><body><table class=\"table-striped\"><tr><th>Invoice<\/th><th>The sad<\/th><th>Description<\/th><th>How much<\/th><th><\/th><th><\/th><\/tr>"
      var sent_rejected = "<br><h4></h4><h5>Rejected</h5><body><table class=\"table-striped\"><tr><th>Invoice<\/th><th>The sad<\/th><th>Description<\/th><th>How much<\/th><th>Reason<\/th><th><\/th><th><\/th><\/tr>"
      var sent_history = "<br><h5>History/Claimed</h5><body><table style=\"text-align:right\" class=\"table-striped\"><tr><th>Invoice<\/th><th>The sad<\/th><th>Description<\/th><th>How much<\/th><th><\/th><th><\/th><\/tr>"
      var received_pend = "<br><h4>Debts</h4><h5>Pending</h5><body><h5></h4><table style=\"text-align:right\" class=\"table-striped\"><tr><th>Invoice<\/th><th>The happy<\/th><th>Description<\/th><th>How much<\/th><th><\/th><th><\/th><\/tr>"
      var received_history = "<br><h5>History/Paid</h5><body><h5></h4><table style=\"text-align:right;\" class=\"table-striped\"><tr><th>Invoice<\/th><th>The happy<\/th><th>Description<\/th><th>How much<\/th><th><\/th><th><\/th><\/tr>"
      console.log(data)
      console.log(data.sent.length)
      console.log(data.received.length)
      var rejected = 0
      for (var i = 0; i < data.sent.length; i++) {

        if(data.sent[i].invoicestatus==1){
      
        sent += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].receiver+"<\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td><input type=\"button\" class=\"btn btn-sm btn-warning\" onclick=\"change("+data.sent[i].invoiceid+")\" value=\"Change\"\/><\/td><td><input type=\"button\" class=\"btn btn-sm btn-danger\" value=\"Delete\" onclick=\"remove("+data.sent[i].invoiceid+")\"><\/td><\/tr>"; 

        }
        if(data.sent[i].invoicestatus==3){
        sent_rejected += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].receiver+"<\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td>"+data.sent[i].message+"<\/td><td><input type=\"button\" class=\"btn btn-sm btn-warning\" onclick=\"change("+data.sent[i].invoiceid+")\" value=\"Change\"\/><\/td><td><input type=\"button\" class=\"btn btn-sm btn-danger\" value=\"Delete\" onclick=\"remove("+data.sent[i].invoiceid+")\"><\/td><\/tr>"; 
        rejected++;
        }
        if(data.sent[i].invoicestatus==2){
        sent_history += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].receiver+"<\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td><input type=\"button\" class=\"btn btn-sm btn-primary\" onclick=\"withdraw_friend_req("+data.sent[i].amount+")\" value=\"Reopen\"\/><\/td><\/tr>"; 
        }
        };
      
      for (var i = 0; i < data.received.length; i++) {
      
        if(data.received[i].invoicestatus==1){
          received_pend += "<tr><td><a onclick=\"openInvoice("+data.received[i].invoiceid+")\" href=\"#\">invoice"+data.received[i].invoiceid+"<\/><\/td><td>"+data.received[i].sender+"<\/td><td>"+data.received[i].description+"<\/td><td>"+data.received[i].amount+"<\/td><td><input type=\"button\" class=\"btn btn-sm btn-warning\" onclick=\"reject("+data.received[i].invoiceid+")\" value=\"Reject\"\/><\/td><td><input type=\"button\" class=\"btn btn-sm btn-success\" onclick=\"pay("+data.received[i].invoiceid+")\" value=\"Confirm pay\"\/><\/td><\/tr>"; 
          }
       
       if(data.received[i].invoicestatus==2){
          received_history += "<tr><td><a onclick=\"openInvoice("+data.received[i].invoiceid+")\" href=\"#\">invoice"+data.received[i].invoiceid+"<\/><\/td><td>"+data.received[i].sender+"<\/td><td>"+data.received[i].description+"<\/td><td>"+data.received[i].amount+"<\/td><td>Payed\"\/><\/td><\/tr>"; 
          }
          };
     
      console.log(rejected)
      document.getElementById("claims-pending").innerHTML =  sent
      if(rejected>0){
        document.getElementById("claims-rejected").innerHTML =  sent_rejected
      }
      document.getElementById("claims-history").innerHTML =  sent_history
      document.getElementById("debts").innerHTML = received_pend
      document.getElementById("debts-history").innerHTML = received_history
      /*document.getElementById("myModal").innerHTML += script*/
      

    });
}

function pay(invoiceid){
console.log(invoiceid)

var url = '/invoice/pay'
fetch(url,{
            method : 'POST',
      headers: {
            'Content-Type': 'application/json;charset=utf-8'      
          },        
          body : JSON.stringify({
            "InvoiceID" : invoiceid
        })
    })
    .then(function (response) {

      console.log(response);
        return response.json();
    })
    .then(function (data) {
      console.log(data);
      get_user_invoices();
      document.getElementById("invoice_overview").innerHTML +=  "<br>"+data.message
    });

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function change(invoiceid){
console.log(invoiceid)


        //$("#invoice_quick").load("/invoice/create?embedded=True");
        $("#invoice_quick").load("/invoice/change"+invoiceid);
        
      

/*document.getElementById("pending_friends").innerHTML +=  "<br>"+"friend request sent to: "+username
*/

}

function remove(invoiceid){
console.log(invoiceid)
           var r=confirm("Are you sure you want to remove this invoice?");
if (r==true){

var url = '/invoice/remove'
fetch(url,{
            method : 'POST',
      headers: {
            'Content-Type': 'application/json;charset=utf-8'      
          },        
          body : JSON.stringify({
            "InvoiceID" : invoiceid,
            
        })
    })
    .then(function (response) {

      console.log(response);
        return response.json();
    })
    .then(function (data) {
      console.log(data);
      get_user_invoices();
      document.getElementById("invoice_overview").innerHTML +=  "<br>"+data.message
    });
  }else{
    return;
  }
}

function reject(invoiceid){
console.log(invoiceid)
               var input_message = prompt("Enter reason for rejection", "");
               
if (input_message === null) {
        return; //break out of the function early
    }
var url = '/invoice/reject'
fetch(url,{
            method : 'POST',
      headers: {
            'Content-Type': 'application/json;charset=utf-8'      
          },        
          body : JSON.stringify({
            "InvoiceID" : invoiceid,
            "message" : input_message
        })
    })
    .then(function (response) {

      console.log(response);
        return response.json();
    })
    .then(function (data) {
      console.log(data);
      get_user_invoices();
      document.getElementById("invoice_overview").innerHTML +=  "<br>"+data.message
    });
}

function openInvoice(invoiceid){
console.log(invoice)
var invoice_modal_header = '<h5>invoice'+invoiceid+'</h5>'
var invoice_modal_body = [
    '<p>Invoice'+invoiceid+'shwon by bjorn</p>',
    '<p>thrse mpre...</p>'
  ].join("\n");

var invoice_modal_footer = '<h5><input type=\"button\" class=\"btn btn-sm btn-warning\" onclick=\"change('+invoiceid+')\" value=\"Change\"\/></h5>'

document.getElementById("invoice-modal-header").innerHTML = invoice_modal_header
document.getElementById("invoice-modal-body").innerHTML = invoice_modal_body
document.getElementById("invoice-modal-footer").innerHTML = invoice_modal_footer
modal.style.display = "block";

}

