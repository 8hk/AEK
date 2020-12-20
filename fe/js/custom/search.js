function addDimension() {
    console.log("Adding a new dimension...");

    // Allow for new dimension only if the "Add dimension" button is not disabled.
    if(document.getElementById("addDimensionsButtonId").getAttribute("disabled") == null) {

        // Allow for new dimension only if the max dimensions limit will not be exceeded.
        var numOfDimensions = $("#dimensionsContainerId").children().length;
        if(numOfDimensions < 6) {

            // For unique dimension id, convert random number to base 36 and pick the first 9 characters following decimal.
            var id = '_' + Math.random().toString(36).substr(2, 9);
            console.log("New dimension id: dimensionContainerId", (id + 1));

            var newDimension = "\n" +
                "        <div class=\"container-fluid search-bar\" id=\"dimensionContainerId" + (id + 1) + "\">\n" +
                "            <!-- Search form -->\n" +
                "            <div class=\"search-form input-group-sm mb-3\">\n" +
                "                <!--<label for=\"dimension1\">Enter search terms... Tab for each term.</label>-->\n" +
                "                <input class=\"form-control\" id=\"dimension" + (id + 1) + "\" type=\"text\" data-role=\"tagsinput\" placeholder=\"Enter search terms... Tab after each term.\" aria-label=\"Search\">\n" +
                "            </div>\n" +
                "            <!-- Remove dimension button -->\n" +
                "            <div class=\"search-button text-center\">\n" +
                "                <a class=\"btn btn-default btn-sm\" id=\"removeDimension" + (id + 1) + "Id\" onclick=\"removeDimension(dimensionContainerId" + (id + 1) + ")\">\n" +
                "                    <span class=\"glyphicon glyphicon-minus\"></span> Remove dimension\n" +
                "                </a>\n" +
                "            </div>\n" +
                "        </div>";
            $("#dimensionsContainerId").append(newDimension);


            $('input[id^="dimension"]').tagsinput({
                maxTags: 6,  // Maximum number of search terms within a dimension
                maxChars: 20
            });

            // Disable "Add dimension" button.
            if (numOfDimensions + 1 == 6) {
                console.log("max");
                document.getElementById("addDimensionsButtonId").setAttribute("disabled", "disabled");
            }

        } else {
            console.log("Maximum number of dimensions is 6.");
        }
    } else {
        console.log("Adding dimension is disabled.");
    }
}

function removeDimension(dimensionId) {
    console.log("Removing dimension: ", dimensionId , "...");
    $(dimensionId).remove();

    // Enable "Add dimension" button.
    document.getElementById("addDimensionsButtonId").removeAttribute("disabled");
}
