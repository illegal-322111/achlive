// Close the dropdown if the user clicks outside of it
/*
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      for (var i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.style.display === 'block') {
          openDropdown.style.display = 'none';
        }
      }
    }
  }
  */

  function copyText() {
    var copyText = document.getElementById("myInput");
    copyText.select();
    document.execCommand("copy");
    alert("Copied the text: " + copyText.value);
  }
  
  function showPopup(){
    var popup = document.getElementById("exampleModalLong");
    popup.style.display = "block";
  }
  function closeFunc(){
    var popup = document.getElementById("exampleModalLong");
    popup.style.display = "none"
};
  
  