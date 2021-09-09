$(document).ready(() => {
        $("#id_restaurant-rest_logo").hide();

        $('#uploadTrigger').click(function(event){
            console.log('testing')
            event.preventDefault();
            $('#id_restaurant-rest_logo').click();
        });

        $(document).ready(function() {
            $("#id_restaurant-rest_logo").on('change', function() {
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

        //Handles restaurant hours
        $(".input-hours").each(function () {
            var textInput = $(this).find("input[type='text']")
            var oldValue = $(this).find("input[type='text']").val();
    
            $(this).find("input[type='checkbox']").change(function() {
                textInput.prop('disabled', !this.checked);
                if (this.checked) {
                    textInput.val(oldValue);
                } else {
                    textInput.val("Closed");
                }
            });
    
            $(this).find("input[type='checkbox']").trigger("change");
        });
        
        //Remove logo image
        $('.remove-logo').click(function(event) {
            event.preventDefault();
            
            var pk = $(this).data('key');
    
            $.ajax({
                url: removeImageURL,
                type: 'GET',
                dataType: 'json',
                data: {
                    'id': pk
                },
                success: (data) => {
                    $('.rest_img').fadeOut(250, function(){ $(this).remove()});
                    $('.restaurant-logo').append('<p>No logo uploaded</p>');
                },
                error: (xhr, errmsg, err) => {
                    console.log('error');
                }
            });
        });
});