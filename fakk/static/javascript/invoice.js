function get_user_invoices(){

var url = '/invoice/getinvoices'
fetch(url)
    .then(function (response) {
        
        return response.json();
    })
    .then(function (data) {
      var sent = "<br><h4>Claims</h4><h5>Pending</h5><body><table class=\"table-responsive table-striped\" style=\"white-space:nowrap;\"><tr><th style=\" width:80px\">Invoice<\/th><th style=\" width:120px\">Description<\/th><th>Amount<\/th><th><\/th><\/tr>"
      var sent_rejected = "<br><h4></h4><h5>Rejected</h5><body><table class=\"table-responsive table-striped\" style=\"white-space:nowrap;\"><tr><th style=\" width:80px\">Invoice<\/th><th style=\" width:120px\">Description<\/th><th>Amount<\/th><th>Reason<\/th><th><\/th><\/tr>"
      var sent_history = "<br><h5>History/Claimed</h5><body><table style=\"text-align:left\"class=\" table-responsive table-striped\" style=\"white-space:nowrap;\"><tr><th style=\" width:120px\">Invoice<\/th><th style=\" width:100px\">Description<\/th><th>Amount<\/th><th><\/th><th><\/th><\/tr>"
      var received_pend = "<br><h4>Debts</h4><h5>Pending</h5><body><h5></h4><table class=\"table-responsive table-striped\" style=\"white-space:nowrap;\"><tr><th style=\" width:80px\">Invoice<\/th><th style=\" width:120px\">Description<\/th><th>Amount<\/th><th><\/th><\/tr>"
      var received_history = "<br><h5>History/Paid</h5><body><h5></h4><table class=\"table-responsive table-striped\" style=\"white-space:nowrap;\"><tr><th style=\" width:80px\">Invoice<\/th><th style=\" width:120px\">Description<\/th><th>Amount<\/th><th><\/th><th><\/th><\/tr>"
      console.log(data)
      console.log(data.sent.length)
      console.log(data.received.length)
      var rejected = 0
      for (var i = 0; i < data.sent.length; i++) {

        if(data.sent[i].invoicestatus==1){
      
        sent += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td><input type=\"button\" style=\"margin-right:5px;\" class=\"btn btn-sm btn-warning\" onclick=\"change("+data.sent[i].invoiceid+")\" value=\"Change\"\/><input type=\"button\" class=\"btn btn-sm btn-danger\" value=\"Delete\" onclick=\"remove("+data.sent[i].invoiceid+")\"><\/td><\/tr>"; 

        }
        if(data.sent[i].invoicestatus==3){
        sent_rejected += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td><b style=\"color:red\">"+data.sent[i].message+"<b><\/td><td><input type=\"button\" style=\"margin-right:5px;\" class=\"btn btn-sm btn-warning\" onclick=\"change("+data.sent[i].invoiceid+")\" value=\"Change\"\/><input type=\"button\" class=\"btn btn-sm btn-danger\" value=\"Delete\" onclick=\"remove("+data.sent[i].invoiceid+")\"><\/td><\/tr>"; 
        rejected++;
        }
        if(data.sent[i].invoicestatus==2){
        sent_history += "<tr><td><a onclick=\"openInvoice("+data.sent[i].invoiceid+")\" href=\"#\">invoice"+data.sent[i].invoiceid+"<\/><\/td><td>"+data.sent[i].description+"<\/td><td>"+data.sent[i].amount+"<\/td><td><input type=\"button\" class=\"btn btn-sm btn-primary\" onclick=\"withdraw_friend_req("+data.sent[i].amount+")\" value=\"Reopen\"\/><\/td><\/tr>"; 
        }
        };
      
      for (var i = 0; i < data.received.length; i++) {
      
        if(data.received[i].invoicestatus==1){
          received_pend += "<tr><td><a onclick=\"openInvoice("+data.received[i].invoiceid+")\" href=\"#\">invoice"+data.received[i].invoiceid+"<\/><\/td><td>"+data.received[i].description+"<\/td><td>"+data.received[i].amount+"<\/td><td><input type=\"button\" style=\"margin-right:5px;\" class=\"btn btn-sm btn-warning\" onclick=\"reject("+data.received[i].invoiceid+")\" value=\"Reject\"\/><input type=\"button\" class=\"btn btn-sm btn-success\" onclick=\"pay("+data.received[i].invoiceid+")\" value=\"Confirm pay\"\/><\/td><\/tr>"; 
          }
       
       if(data.received[i].invoicestatus==2){
          received_history += "<tr><td><a onclick=\"openInvoice("+data.received[i].invoiceid+")\" href=\"#\">invoice"+data.received[i].invoiceid+"<\/><\/td><td>"+data.received[i].description+"<\/td><td>"+data.received[i].amount+"<\/td><td>Payed<\/td><\/tr>"; 
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

function getOneInvoice(invoiceid){

var url = '/invoice/getinvoice'+invoiceid
console.log('url', url)
fetch(url)
    .then(function (response) {
        
        return response.json();
    })
    .then(function (data) {
      console.log('gotten invoce', data)
      
    })
return data;
}

function emailInvoice(invoiceid){

var url = '/invoices/email/'+invoiceid
console.log('url', url)
fetch(url)
    .then(function (response) {
        
        return response.json();
    })
    .then(function (data) {
      console.log('email status', data.message)
      document.getElementById("invoice-modal-footer").innerHTML +=  "<br>"+data.message


    })

}


function openInvoice(invoiceid){
console.log(invoiceid)


var url = '/invoice/getinvoice'+invoiceid
console.log('url', url)
fetch(url)
    .then(function (response) {
        
        return response.json();
    })
    .then(function (data) {
      console.log(data.invoice.createddate);
      const created_date = new Date(data.invoice.createddate);
      const due_date = new Date(data.invoice.duedate);

      date_created = new Date(data.invoice.createddate).toLocaleString('en-us', {year: 'numeric', month: '2-digit', day: '2-digit'}).replace(/(\d+)\/(\d+)\/(\d+)/, '$3-$1-$2')+" "+created_date.getHours()+":"+created_date.getMinutes();
      console.log(date_created)
      date_due = new Date(data.invoice.duedate).toLocaleString('en-us', {year: 'numeric', month: '2-digit', day: '2-digit'}).replace(/(\d+)\/(\d+)\/(\d+)/, '$3-$1-$2')+" "+due_date.getHours()+":"+due_date.getMinutes();
      console.log(date_due)

  var invoice_modal_header = '<h5>invoice'+invoiceid+'</h5>'
  var invoice_modal_body = [
    '<p>Invoice details</p>',
    '<p><table class=\"table-striped\">',
    '<tr><th style="text-align:left; width:120px\"">Description</td><td style="text-align:left">'+data.invoice.description+'</td></tr>',
    '<tr><th style="text-align:left">Sender</td><td style="text-align:left">'+data.invoice.sender+'</td></tr>',
    '<tr><th style="text-align:left">Payee</td><td style="text-align:left">'+data.invoice.receiver+'</td></tr>',
    '<tr><th style="text-align:left">Amount</td><td style="text-align:left">'+data.invoice.amount+'</td></tr>',
    '<tr><th style="text-align:left">Created</td><td style="text-align:left">'+date_created+'</td></tr>',
    '<tr><th style="text-align:left">Due</td><td style="text-align:left">'+date_due+'</td></tr>',
    '<tr><th style="text-align:left">Version</td><td style="text-align:left">'+data.invoice.version+'</td></tr></p>'
  ].join("\n");

  var invoice_modal_footer = '<tr><td><h5><a href="/invoices/renderpdf/'+invoiceid+'" style=\"margin-right:5px;\" class="btn btn-sm btn-primary">Download PDF</a><\/td><td><input type=\"button\" style=\"margin-right:5px;\" class=\"btn btn-sm btn-primary\" onclick=\"emailInvoice('+invoiceid+')\" value=\"Email invoice\"\/></h5><\/td><\/tr>'
  document.getElementById("invoice-modal-header").innerHTML = invoice_modal_header
  document.getElementById("invoice-modal-body").innerHTML = invoice_modal_body
  document.getElementById("invoice-modal-footer").innerHTML = invoice_modal_footer
  modal.style.display = "block";

    })



}

function swish(payee,amount,message){
  console.log(payee)
  console.log(amount)
  console.log(message)
  var json = JSON.stringify({
        "version":1,
        "payee":{
        "value": payee
        },
        "amount":{
        "value":amount
        },
        "message":{
        "value":message,
        "editable":true
        } })
  console.log(json)
  var url = "swish://payment?data="+json
  var urlshort = "swish://payment?data=<URL_encoded_JSON_payload>"
  open(url);
  }

