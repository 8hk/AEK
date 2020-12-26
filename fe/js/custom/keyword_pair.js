import * as c from "./Chart.min.js"

class Pair {
    constructor(data) {
        var keywords = JSON.parse(data);
        var cards=""
        for (let key in keywords.keyword_pairs) {
            this.create_card(keywords.keyword_pairs[key],key);
        }

    }

    create_card(pair,index){
        var keyword_pair =
            // "<div class=\"card-deck mb-3 text-center\">\n" +
            "        <div class=\"card box-shadow\">\n" +
            "          <div class=\"card-header\">\n" +
            "            <h4 class=\"my-0 font-weight-normal\">"+pair.value+"</h4>\n" +
            "          </div>\n" +
            "          <div class=\"card-body\">\n" +
            "            <h2 class=\"card-title pricing-card-title\">Papers Number</h2>\n" +
            "            <ul class=\"list-unstyled mt-3 mb-4\">\n" +
            "              <li>" +pair.papers_number+"</li>\n" +
            "            </ul>\n" +
            "            <h2 class=\"card-title pricing-card-title\">Top Authors</h2>\n" +
            "            <ul class=\"list-unstyled mt-3 mb-4\">\n" +
            "              <li>" +pair.top_authors[0]+"</li>\n" +
            "              <li>" +pair.top_authors[1]+"</li>\n" +
            "              <li>" +pair.top_authors[2]+"</li>\n" +
            "            </ul>\n" +
            "            <h2 class=\"card-title pricing-card-title\">Top Keywords</h2>\n" +
            "            <ul class=\"list-unstyled mt-3 mb-4\">\n" +
            "              <li>" +pair.top_keywords[0]+"</li>\n" +
            "              <li>" +pair.top_keywords[1]+"</li>\n" +
            "              <li>" +pair.top_keywords[2]+"</li>\n" +
            "            </ul>\n" +
            "              <div class=\"papers-by-year\" style=\"position: relative; height:(600/index)px; width:(600/index)px\">\n" +
            "              <canvas id=\"myChart"+index+"\" width=\"400\" height=\"400\"></canvas>\n" +
            "          </div>\n" +
            "            <button type=\"button\" class=\"btn btn-lg btn-block btn-primary\">Go To</button>\n" +
            "          </div>\n"
            "\n"+
            "        </div>";
        // return keyword_pair;


        $("#keyword-pair-container").append(keyword_pair);
        this.create_chart(pair.publication_year,pair.publication_year_values,index);
    }


    create_chart(publication_year,year_values,index) {
        var ctx = document.getElementById('myChart'+index);
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: publication_year,
                datasets: [{
                    label: '# of Papers',
                    data: year_values,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }
}

export {Pair};