$(document).ready(() => {

    $('.fav-item').click(function(){
        $('.favorite-button-container').slideDown(250);
    });

    $('.fav-item').click(function(){
            var item_id = $(this).data('id');
            var is_checked = $(this).is(':checked');
            
            $.ajax({
                url: favoritesURL,
                dataType: 'json',
                type: 'GET',
                data: {
                    'id': item_id,
                    'is_checked': is_checked
                },
                success: (data) => {
                    var fav_count = data.fav_count;

                    if(fav_count === 0){
                        $('.favorite-button-container').slideUp(250);
                    }
                },
                error: (xhr, errmsg, err) => {
                    console.log('error');
                }
            });
        });

        $('.remove-fav').click(function(e){
            e.preventDefault();

            var item_id = $(this).data('id');
            var row = $(this).closest('.fav-card')

            $.ajax({
                url: favoritesURL,
                dataType: 'json',
                type: 'GET',
                data: {
                    'id': item_id,
                    'delete': "true"
                },
                success: (data) => {
                    row.slideUp(150);
                },
                error: (xhr, errmsg, err) => {
                    console.log("error");
                }
            });
        });
});