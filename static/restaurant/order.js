$(document).ready(() => {
    $(".item-row").each(function (rowIdx) {
        var rowThis = this;
        var rowQuantity = $(this).find(".quantity");
        
        $(this).find(".remove-item").click(function () {
            $.ajax({
                url: removeItemURL,
                type: "GET",
                data: {
                    'item_name': $(rowThis).find(".item-name").data('item-id'),
                },
                success: (data) => {
                    console.log(`Deleted ${ $(rowThis).find(".item-name").data('item-id') }`);

                    $(rowThis).remove();
                    if ($(".item-row").length === 0) {
                        $("#checkout-stuff").remove();
                        $(".container").append("<p>You haven't added any items!</p>");
                    } else {
                        // this forces the total price to update
                        $(".quantity").trigger("change");
                    }
                },
                error: (xhr, errmsg, err) => {
                    console.log("Something went wrong when deleting an item. Error info below:");
                    console.log(errmsg);
                    console.log(err);
                    
                },
            });
        });

        $(this).find(".quantity").change(function() {
            var quantity = parseFloat($(this).val());

            $.ajax({
                url: modifyItemQuantity,
                dataType: "json",
                data: {
                    'item_name': $(rowThis).find(".item-name").text(),
                    'new_quantity': quantity,
                },
                success: (data) => {
                    console.log(`Updated ${ $(rowThis).find(".item-name").text() }'s quantity`);

                    $(rowThis).find(".computed-price").text("$" + data.newPrice);
            
                    // update page's total price
                    var pageTotalPrice = 0.0;
                    $(".computed-price").each(function (i) {
                        pageTotalPrice += parseFloat($(this).text().slice(1));
                    });
                    $("#total-price").text("$" + pageTotalPrice.toFixed(2));
                },
                error: (xhr, errmsg, err) => {
                    console.log("Something went wrong when updating an item's quantity. Error info below:");
                    console.log(errmsg);
                    console.log(err);
                },
            });
        });

        $(this).find(".quantity-up").click(function() {
            var quantityObj = $(rowThis).find(".quantity");
            var oldQuantity = parseFloat(quantityObj.val());
            if ($(rowQuantity).attr('step') == "1") {
                quantityObj.val((oldQuantity + 1).toFixed(0));
            } else {
                quantityObj.val((oldQuantity + 0.1).toFixed(1));
            }
            // .change() doesn't trigger when we modify values
            // using .val(), so we have to trigger it manually
            quantityObj.trigger("change");
        });
    
        $(this).find(".quantity-down").click(function() {
            var quantityObj = $(rowThis).find(".quantity").first();
            var oldQuantity = parseFloat(quantityObj.val());
            if ($(rowQuantity).attr('step') == "1") {
                quantityObj.val(Math.max(oldQuantity - 1, 1).toFixed(0));
            } else {
                quantityObj.val(Math.max(oldQuantity - 0.1, 0.1).toFixed(1));
            }
            // .change() doesn't trigger when we modify values
            // using .val(), so we have to trigger it manually
            quantityObj.trigger("change");
        });
    });
});
