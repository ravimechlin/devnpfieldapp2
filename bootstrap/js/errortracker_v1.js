window.onerror = function(error_message, url, line_number, column, error_object)
{
    if(error_object != null)
    {
    	stack_trace = JSON.stringify(error_object);
    }
    else
    {
	stack_trace = "N/A";
    }
    $.ajax({
	type: "POST",
	url: "./data",
	data: {
	    "fn": "np_client_error_logger", 
	    "error_message": error_message, 
	    "line_number": line_number, 
	    "url": url, 
	    "column": column,
	    "stack_trace": stack_trace 
	},
	async: true,
    });
    return true;
}
