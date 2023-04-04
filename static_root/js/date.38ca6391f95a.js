const dateValue = [... document.querySelectorAll('.date-time')]
const date = new Date();

let day = date.getDate();
let month = date.getMonth() + 1;
let year = date.getFullYear();


var currentDate = `${day}-${month}-${year}`;


  dateValue.map(function(value){
  value.innerHTML = currentDate;
  })
