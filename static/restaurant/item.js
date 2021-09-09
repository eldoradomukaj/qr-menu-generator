$(document).ready(() => {
    var unitPrice = $("#computedPrice").text().substring(1);

    $("#quantity").change(function() {
        var quantity = parseFloat($("#quantity").val());
        $("#computedPrice").text(
            "$" + (unitPrice * quantity).toFixed(2)
        );
    });

    $("#quantity-up").click(function() {
        var oldQuantity = parseFloat($("#quantity").val());
        if ($("#quantity").attr('step') == "1") {
            $("#quantity").val((oldQuantity + 1).toFixed(0));
        } else {
            $("#quantity").val((oldQuantity + 0.1).toFixed(1));
        }
        // .change() doesn't trigger when we modify values
        // using .val(), so we have to trigger it manually
        $("#quantity").trigger("change");
    });

    $("#quantity-down").click(function() {
        var oldQuantity = parseFloat($("#quantity").val());
        if ($("#quantity").attr('step') == "1") {
            $("#quantity").val(Math.max((oldQuantity - 1).toFixed(0), 1));
        } else {
            $("#quantity").val(Math.max((oldQuantity - 0.1).toFixed(1), 0.1));
        }
        // .change() doesn't trigger when we modify values
        // using .val(), so we have to trigger it manually
        $("#quantity").trigger("change");
    });

    $("#add-btn").click(function () {
        $("#add-btn").prop('disabled', true);
        $("#add-btn").addClass('changeColor');

        console.log('item added to cart');
    });
});
