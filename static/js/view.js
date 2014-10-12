PPP_UGO.sm_cursor = '';
PPP_UGO.a_cursor = '';
PPP_UGO.sm_data = [];
PPP_UGO.a_data = [];
PPP_UGO.startedPoll = false;
PPP_UGO.chartOpts = {
    clickable: true,
    hoverable: true,
    series: {
        lines: { show: true },
        points: { show: true }
    },
    xaxis: { 
        mode: "time",
        timeformat: "%m/%d/%y %H:%M",
        //tickSize: [1, "hour"]
    },
    grid: {
        clickable: true,
        hoverable: true,
        autoHighlight: true,
        mouseActiveRadius: 5
    },
    interaction: {
        redrawOverlayInterval: 1
    },
    selection: {
        mode: "x"
    }
}

function getRecentStats(productKey) {

    $('#sm-chart').bind("plotselected", function (event, ranges) {
	
	    plot = $.plot($('#sm-chart'),
	        [PPP_UGO.sm_data], $.extend(true, {}, PPP_UGO.smChartOpts, {
		    xaxis: {
			    min: ranges.xaxis.from,
			    max: ranges.xaxis.to
		    }
	    }));
    });
	    
	$.getJSON('/ajax?action=getstats&key=' + productKey +
	    '&sm_cursor=' + PPP_UGO.sm_cursor +
	    '&a_cursor=' + PPP_UGO.a_cursor, {
        cache:false
    })
    .done(function(jsonData) {
    
        if (!PPP_UGO.startedPoll) {
            $('#report-body').empty();
            PPP_UGO.startedPoll = true;
        }
    	$("#sm").appendTo("#report-body");
    	$("#a").appendTo("#report-body");
    	$('section#sm').css('display', 'block');
    	$('section#a').css('display', 'block');
    	var productName = $('#p-name').text();
    	
    	// Get cursors for next fetch
    	PPP_UGO.sm_cursor = jsonData.sm_cursor;
    	PPP_UGO.a_cursor = jsonData.a_cursor;
    	
    	if (jsonData.sm_mentions.length != 0) {
			// Plot graph
			PPP_UGO.sm_data = PPP_UGO.sm_data.concat(jsonData.sm_mentions);
			var plot = $.plot("#sm-chart", [PPP_UGO.sm_data], PPP_UGO.chartOpts);
    	}
    	
    	if (jsonData.a_mentions.length != 0) {
			// Plot graph
			PPP_UGO.a_data = PPP_UGO.a_data.concat(jsonData.a_mentions);
			console.log(jsonData.a_mentions);
			var plot = $.plot("#a-chart", [PPP_UGO.a_data], PPP_UGO.chartOpts);
    	}
    	
		
		// If data was previously fetched, fetch again
		/* TODO: This keeps polling server for one or the other, even though
		   one may already be complete. It runs like shit.
		 */
		if (jsonData.sm_mentions.length != 0 || jsonData.a_mentions .length != 0) {
			setTimeout(function(){ getRecentStats(productKey) }, 3000);
		}
	    
	    $('#sm-clear-zoom').click(function() {
	        plot = $.plot("#sm-chart", [PPP_UGO.sm_data], PPP_UGO.chartOpts);
	    });
    })
    .fail(function() {

    })
    .always(function() {});
}

$(document).ready(function(){
    var productKey = $('#product-name').attr('data-product-key');
    getRecentStats(productKey);
});
