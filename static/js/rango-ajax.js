$(document).ready(function(){

  $('#likes').click(function(event){
    let catid = $(this).attr('data-catid');
    $.get('/rango/like_category/', {category_id: catid}, function(data){
      $('#like_count').html(data);
      $('#likes').hide();
    });
  });

  $('#suggestion').keyup(function(){
    let text = $(this).val();
    $.get('/rango/suggest_category/', {query: text}, function(data){
      $('#cats').html(data)
    });
  });

  $('button.add-page-to-category').click(function(event){
    let cat_slug = $(this).attr('data-slug');
    let page_title = $(this).attr('data-title');
    let page_url = $(this).attr('data-url');
    // alert(cat_slug + "\n" + page_title + "\n" + page_url);
    // $(this).hide();
    let this_ = $(this);
    $.get('/rango/add_page_to_category/', {slug: cat_slug, title: page_title, url: page_url}, function(data) {
      // console.log(data.trim());
      // console.log("=============");
      // console.log($(data));
      // let test = $(data);

      //? proper way of handling this?
      if(data.trim() != "no_new_data") {
        $('#pages').html(data);
        this_.hide();
      }
    });
  });

});
