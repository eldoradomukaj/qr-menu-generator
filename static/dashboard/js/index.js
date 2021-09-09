function getChartColor(itemIdx, numItems) {
    var delta = itemIdx / (numItems - 1);
    var r = Math.round(234 - (delta * 211));
    var g = Math.round(121 + (delta * 40));
    var b = Math.round(185 + (delta * 37));
    return `rgba(${r}, ${g}, ${b}, 1)`;
}
    
$(document).ready(function() {
    const chartOptions = {
        responsive: true,
        title: {
            display: false,
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
        xAxes: [{
            type: 'time',
            ticks: {
                autoSkipPadding: 12,
            },
            time: {
                isoWeekday: true,
                unit: 'day',
            },
        }],
        yAxes: [{
            display: true,
            scaleLabel: {
                display: true,
                labelString: 'Views'
            },
            ticks: {
                suggestedMax: 10.0,
                stepSize: 1.0,
            }
        }]
    }};

    var ctx1 = $("#itemsChart");
    var itemsChart = new Chart(ctx1, {
        type: 'line',
        data: {},
        options: chartOptions,
    });

    var ctx2 = $("#categoriesChart");
    var categoriesChart = new Chart(ctx2, {
        type: 'line',
        data: {},
        options: chartOptions,
    });

    function updateItemsChart() {
        $.ajax({
            url: analyticsAjaxURL,
            type: "GET",
            data: {
                "type": "items",
                "range": $("#items-range-select").find(":selected").val(),
                "category": $("#items-cat-select").find(":selected").val(),
            },
            success: function (data) {
                // setup category selector
                if ("categories" in data) {
                    var selector = $("#items-cat-select");
                    $(selector).empty();
                    $(selector).append('<option value="Any" selected>(Any category)</option>');
                    data.categories.forEach((i) => {
                        $(selector).append(`<option value="${i}">${i}</option>`);
                    });
                }

                itemsChart.data = data;
                itemsChart.options.scales.yAxes[0].ticks = data.options;
                if (data.options.weekLabels) {
                    itemsChart.options.tooltips.callbacks.title = (tooltipItems, data) => "Week of " + tooltipItems[0].label;
                } else {
                    itemsChart.options.tooltips.callbacks.title = (tooltipItems, data) => tooltipItems[0].label;
                }
                if (data.options.hiding) {
                    $(".analytics-hiding").show();
                } else {
                    $(".analytics-hiding").hide();
                }
                itemsChart.update();
            },
            error: function () {
                console.log("error when fetching items data");
            },
        });
    }

    function updateCategoriesChart() {
        $.ajax({
            url: analyticsAjaxURL,
            type: "GET",
            data: {
                "type": "categories",
                "range": $("#cats-range-select").find(":selected").val(),
            },
            success: function (data) {
                categoriesChart.data = data;
                categoriesChart.options.scales.yAxes[0].ticks = data.options;
                if (data.options.weekLabels) {
                    categoriesChart.options.tooltips.callbacks.title = (tooltipItems, data) => "Week of " + tooltipItems[0].label;
                } else {
                    categoriesChart.options.tooltips.callbacks.title = (tooltipItems, data) => tooltipItems[0].label;
                }
                categoriesChart.update();
            },
            error: function () {
                console.log("error when fetching items data");
            },
        });
    }

    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
        if ($(e.target).attr("id") === "analyticsItemsTab") {
            updateItemsChart();
        } else {  // #analyticsCategoriesTab
            updateCategoriesChart();
        }
    });

    $('#analyticsItemsTab').trigger('show.bs.tab');

    $("#items-cat-select").change(updateItemsChart);
    $("#items-range-select").change(updateItemsChart);
    $("#cats-range-select").change(updateCategoriesChart);
});