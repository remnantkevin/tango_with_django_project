$(document).ready(function() {

  // $('#about-btn').click(function(event) {
  //   alert("You clicked on the JQuery button.");
  // });

  /*
   Here, we are selecting all the p HTML elements, and on hover we are associated two functions, one
   for on hover, and the other for hover off. You can see that we are using another selector called, this ,
   which selects the element in question, and then sets its colour to red or blue respectively. Note that
   the JQuery hover() function takes two functions.
  */
  // $('p').hover(function() {
  //   $(this).css('color', 'red');
  // },
  // function() {
  //   $(this).css('color', 'blue');
  // });

  $('#about-btn').click(function(event){
    msgstr = $('#msg').html();
    msgstr = msgstr + "ooo";
    $('#msg').html(msgstr);
  });

});
