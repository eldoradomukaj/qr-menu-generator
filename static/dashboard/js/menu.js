$(document).ready(() => {
        // HIDE AND UNHIDE MENU ITEMS
        $(document).ready(function(){
            var $delete = $('.delete-btn').hide(),
            $chkbx = $('input[name="menu-items"]').click(function(){
                $delete.toggle($chkbx.is(":checked"));
            });
        });
        
        $(document).ready(function(){

            $('.hider').change(function(){
              console.log($(this).val())

                $.ajax({
                    
                    url : toggleMenuURL.replace('0', $(this).val()),
                    
                    type: $(this).attr('method'),
                    data: $(this).serialize(),

                    success:function(data){
                        
                    },
                    error:function(xhr,errmsg,err){
                        console.log('An error occurred')
                    }
                });
              });
        });


        // SHOW/HIDE CUSTOM UNIT FIELD
        $(document).ready(function(){
      
            $('#id_custom_unit').hide();
    
            $("#id_units").change(function(){
              
    
              if ($(this).val() === "OT") {
                  $("#id_custom_unit").show();
              } else {
                  $("#id_custom_unit").hide();
                  //$("#id_custom_unit").val("");
              }
          });
        });

        // reset form data and remove uploaded image if user cancels or closes modal
        $('.close, #cancelButton').click(function(){
            $('#formReset').click();
            $('.thumb-image').removeAttr('src');
        });

        //MENU ITEM UPDATE MODAL
        $(".menu-item-edit").click(function(event){
            
            event.preventDefault();
            var pk = $(this).data('pid');
            
            var pid = $('#updateMenuModal').data('pid', pk);
            
            if (pid != ''){
                $('#updateMenuModal').modal('show');
            }
        });  

        $('#updateMenuModal').on('show.bs.modal', function(event){
        
        var modal = $(this)
        var pk = $(this).data('pid')

        $.ajax({
            type: "POST",
            headers: { "X-CSRFToken" : csrf_token },
            data: { 'pk': pk },
            url: loadMenuItemURL,
            context: document.body,
            error:function(response, error){
                console.log("error")
            }
            }).done(function(response){
                
                $('#something').html(response)

                if ($(this).val() === "OT") {
                $('input[name="custom_unit"]').show();
                } else {
                $('input[name="custom_unit"]').hide();
                }
                
                $('select[name="units"]').change(function(){
                if ($(this).val() === "OT") {
                    $('input[name="custom_unit"]').show();
                } else  {
                    $('input[name="custom_unit"]').hide();
                }
                });

                $('#uploadTriggerMenuUpdate').click(function(event){
                    event.preventDefault();
                    $('#id_image.update-menu').click();
                });

                $("#id_image.update-menu").on('change', function() {
                    //Get count of selected files
                    var countFiles = $(this)[0].files.length;
                    var imgPath = $(this)[0].value;
                    var extn = imgPath.substring(imgPath.lastIndexOf('.') + 1).toLowerCase();
                    var image_holder = $("#menuitem-image-holder");
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
                            "class": "thumb-update-image"
                            }).appendTo(image_holder);
                            $('<p><a href="#" class="remove-update-upload">Remove</p>').appendTo(image_holder);
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

                //Delete the update modal image selected for upload
                $(document).on('click', '.remove-update-upload', function(event){
                    event.preventDefault();

                    $('.thumb-update-image').remove();
                    $(this).remove();
                });


            });
        });


        // DELETE MENU ITEM MODAL
        $(document).on("click", ".confirm-menu-delete", function(event){
            event.preventDefault();
    
            var modalVal = $(this).data('id');
            
            var idValue = $("#confirmDelete").val(modalVal);
        });
    
        $('#confirmDelete').click(function(){
                $.ajax({
                url: deleteMenuItemURL.replace('0', $(this).val()),
                headers: { "X-CSRFToken" : csrf_token},
                type: 'POST',
                dataType: 'json',
                data: {
                    'value': $(this).val()
                },
    
                success:function(data){
                    $('.close').click();
                    
                    $('.card-'+data.value).closest('.col-md-3').hide('fade');
                },
                error:function(xhr, errmsg, err){
                    console.log('an error')
                }
                });
            });


        // IMAGE UPLOAD AND PREVIEW HANDLER
        $('#uploadTrigger').click(function(event){
            event.preventDefault();
            $('#id_image').click();
        });
        $("#id_image").on('change', function() {
            //Get count of selected files
            var countFiles = $(this)[0].files.length;
            var imgPath = $(this)[0].value;
            var extn = imgPath.substring(imgPath.lastIndexOf('.') + 1).toLowerCase();
            var image_holder = $("#image-holder");
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
                    $('<p><a href="#" class="remove-upload">Remove</p>').appendTo(image_holder);
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

        //delete upload image for new menu item
        $(document).on('click', '.remove-upload', function(event){
            event.preventDefault();

            $('.thumb-image').remove();
            $(this).remove();
        });

        $(document).on('click', '.remove-image', function(event){
            event.preventDefault();
            var data_id = $(this).data('key'); 

            $.ajax({
                url: deleteMenuItemImageURL,
                type: 'GET',
                dataType: 'json',
                data: {
                    'id': data_id,
                },
                success: (data) => {
                    $('#menuitem-image-holder').empty();
                },
                error: (xhr, errmsg, err) => {
                    console.log('error');
                }
            });
        });

});