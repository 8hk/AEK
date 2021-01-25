function searchWikidata() {
    $.ajax({
        url: "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search=" + $('#livesearchInputId').val(),
        type: "get",
        cache: 'false',
        dataType: "jsonp",
        async: 'false',
        timeout: 1000,

        success: function (response) {   // Successful at adding a relation.
            console.log("Search request in Wikidata is successful.");
            console.log(response);
            let search_results_list = document.createElement('ul');
            search_results_list.setAttribute("id", "searchResultsId");
            search_results_list.style.border="1px solid #A5ACB2";
            if (response["search"]) {
                let results = response["search"];
                for(let idx_result = 0; idx_result < results.length; idx_result ++) {
                    let result = document.createElement('li');
                    result.innerHTML = "<a href='" + results[idx_result]["concepturi"] + "'>" + results[idx_result]["label"] + "</a>";
                    search_results_list.appendChild(result);
                }
                let old_results = document.getElementById("searchResultsId");
                document.getElementById("wikidataSearchResultsId").replaceChild(search_results_list, old_results);
            }
        },
        error: function (response) {
            console.log("Search request in Wikidata is unsuccessful.");
        }
    });
}
