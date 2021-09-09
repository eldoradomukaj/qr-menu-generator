$(document).ready(() => {
        // ADD CATEGORY FIELDS
        $('.add-category-field').click(function(event){
            event.preventDefault();

            var html = '';
            html += '<div class="row form-group">';
            html += '<div class="col col-md-3">';
            html += '<label class="form-control-label">Category </label>';
            html += '</div>';

            html += '<div class="col-6 col-sm-6">';
            html += '<input id="id_cat_name" class="form-control" type="text" name="cat_name" placeholder="Enter a category">';
            html += '</div><div class="col"><button class="remove-category-field btn btn-danger btn-sm" type="button"><i class="fa fa-minus"></i></button></div>';
            html += '</div>';

            $('.newRow').append(html);
        });

        $(document).on('click', '.remove-category-field', function(){
            $(this).closest('.form-group').remove();
        });

        // CATEGORY TILE POSITION HANDLER
        setButtons();

        $(document).on('click', '#moveDown', function(e){
          e.preventDefault();
  
          var cCard = $(this).closest('.category-card');
          var tCard = cCard.next('.category-card');
  
          cCard.insertAfter(tCard);
          setButtons();
          resetSort();
          
        });
  
        $(document).on('click', '#moveUp', function(e){
          e.preventDefault();
  
          var cCard = $(this).closest('.card');
          var tCard = cCard.prev('.card');
  
          cCard.insertBefore(tCard);
          setButtons();
          resetSort();
          
        });
    
        function setButtons(){
          $('#moveUp, #moveDown').show();
          $('.category-card:first-child #moveUp').hide();
          $('.category-card:last-child #moveDown').hide();
        }
  
        function resetSort(){
          var i = 0;
          $('.category-card').each(function(){
            $(this).attr('data-position', i);
            i++;
  
          });
          
        }

        //CATEGORY CARD POSITION DATABASE HANDLER
        $(document).on('click', '#moveUp, #moveDown', function(e){
            e.preventDefault();
            
            var position = $(this).closest('.category-card').attr('data-position')
            var value = $(this).attr('value')
    
            //var next = $(this).closest('.category-card').next('.category-card')
            var prev = $(this).closest('.category-card').prev('.category-card').attr('data-position')
            var prev_pk = $(this).closest('.category-card').prev('.category-card').attr('value')
            
            var next = $(this).closest('.category-card').next('.category-card').attr('data-position')
            var next_pk = $(this).closest('.category-card').next('.category-card').attr('value')
    
            $.ajax({
              url: updatePosURL.replace('0', value),
              dataType: 'json',
              data: {
                'position': position,
                'pk': value,
                'prev': prev,
                'prev_pk': prev_pk,
                'next': next,
                'next_pk': next_pk
              },
    
              success:function(data){
                console.log()
              },
              error:function(xhr, errmsg, err){
                console.log('something is broken')
              }
            });
    
          });

          
        //DELETE CATEGORY MODAL
        $(document).on('click', '.delete-category-modal', function(event){
            event.preventDefault();

            var modal_value = $(this).data('id');
            var confirm_delete = $('#confirmCatDelete').val(modal_value);
        });

        $('#confirmCatDelete').click(function(){
                $.ajax({
                url: deleteCatItemURL.replace('0', $(this).val()),
                headers: { "X-CSRFToken" : csrf_token },
                type: "POST",
                dataType: "json",
                data: {
                    'value': $(this).val()
                },

                success:function(data){
                    $('.close').click();
                    $('#id_'+data.value).slideUp(300, function(){
                        $(this).remove();
                    });

                },
                error:function(xhr,errmsg,err){
                    console.log('error')
                }
                });
        });
        
        //HIDE UNHIDE CATEGORY 
        $(document).ready(function(){
            $(document).on('change', '.hide-category', function(){
            var checkbox_id = $(this).val()
            var is_checked = $(this).is(':checked')

            $.ajax({
                url: hideCategoryURL,
                type: "POST",
                headers: { "X-CSRFToken" : csrf_token},
                data: {
                'id': checkbox_id,
                'is_checked': is_checked
                },
                succes:function(data){

                },
                error:function(xhr, errmsg, err){
                console.log('an error occured')
                }

            });
            });
        });


        //UPDATE CATEGORY MODAL
        $(document).on('click', '.update-category-modal', function(event){
            event.preventDefault();

            var modal_pk = $(this).data('pk');
            var modal_id = $('#updateCategoryModal').val(modal_pk)

            if(modal_id != ''){
            $('#updateCategoryModal').modal('show');
            }
            
            
        });

        $('#updateCategoryModal').on('show.bs.modal', function(event){ 
            var modal_pk = $(this).val()
            
            $.ajax({
            type: "POST",
            headers: { "X-CSRFToken" : csrf_token},
            data: { 'pk': modal_pk },
            url: updateCategoryURL,
            context: document.body,
            error:function(response, error){
                console.log('error');
            }
            }).done(function(response){
                $('#categoryUpdateContainer').html(response);
                $('#id_cat_img').hide();

                $('#uploadTriggerCategory').click(function(event){
                    event.preventDefault();
                    $('#id_cat_img').click();
                });

                
                    $("#id_cat_img").on('change', function() {
                    //Get count of selected files
                    var countFiles = $(this)[0].files.length;
                    var imgPath = $(this)[0].value;
                    var extn = imgPath.substring(imgPath.lastIndexOf('.') + 1).toLowerCase();
                    var image_holder = $("#category-image-holder");
                    image_holder.empty();
                    if (extn == "gif" || extn == "png" || extn == "jpg" || extn == "jpeg") {
                        if (typeof(FileReader) != "undefined") {
                        //loop for each file selected for uploaded.
                        for (var i = 0; i < countFiles; i++) 
                        {
                            var reader = new FileReader();
                            reader.onload = function(e) {
                            $("<img />", {
                                "src": e.target.result,
                                "class": "thumb-image"
                            }).appendTo(image_holder);
                            }
                            image_holder.show();
                            reader.readAsDataURL($(this)[0].files[i]);
                        }
                        } else {
                        alert("This browser does not support FileReader.");
                        }
                    } else {
                        alert("Please select only images");
                    }
                    });
                

            });
        });


        //Publish Menu Handler
        $('.publish-menu').click(function(){
            var data_pk = $(this).data('pk');
            var is_checked = $(this).is(':checked');

            $.ajax({
                url: publishMenuURL,
                type: 'GET',
                dataType: 'json',
                data: {
                    'pk': data_pk,
                    'is_checked': is_checked
                },
                success: (data) => {
                    
                },
                error: (xhr, errmsg, msg) => {
                    console.log('error');
                }
            });
        });
});