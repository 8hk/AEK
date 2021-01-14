import * as c from "./../chart.js-2.9.4/package/dist/Chart.min.js"

var keywords;

class Pair {

    constructor(data) {
        console.log("data: " + data)
        keywords = JSON.parse(data);
        var cards = ""
        for (let key in keywords.keyword_pairs) {
            this.create_card(keywords.keyword_pairs[key], key);
        }
    }

    create_card(pair, index) {
        //region div elements
        var iDiv = document.createElement('div');
        iDiv.id = 'block' + index;
        iDiv.className = 'card box-shadow flex-child';

        var iDiv2 = document.createElement('div');
        iDiv2.className = 'card-header';
        var h1 = document.createElement('h6');
        h1.className = "my-0 font-weight-normal";
        h1.innerText = pair.value;
        iDiv2.appendChild(h1);
        iDiv.appendChild(iDiv2);

        var iDiv3 = document.createElement('div');
        iDiv3.className = 'card-body';
        var h2 = document.createElement('h6');
        h2.className = "card-title pricing-card-title";
        h2.innerText = "Papers Number";
        iDiv3.appendChild(h2);
        var list = document.createElement('ul');
        list.className = "list-unstyled mt-3 mb-4";
        var listItem = document.createElement('li');
        listItem.innerText = pair.papers_number
        list.appendChild(listItem)
        iDiv3.appendChild(list)

        var h3 = document.createElement('h6');
        h3.className = "card-title pricing-card-title";
        h3.innerText = "Top Keywords";
        iDiv3.appendChild(h3);
        var list2 = document.createElement('ul');
        list2.className = "list-unstyled mt-3 mb-4";
        var listItem2 = document.createElement('li');
        listItem2.innerText = pair.top_authors[0]
        list2.appendChild(listItem2)
        var listItem3 = document.createElement('li');
        listItem3.innerText = pair.top_authors[1]
        list2.appendChild(listItem3)
        var listItem4 = document.createElement('li');
        listItem4.innerText = pair.top_authors[2]
        list2.appendChild(listItem4)
        iDiv3.appendChild(list2)

        var h4 = document.createElement('h6');
        h4.className = "card-title pricing-card-title";
        h4.innerText = "Top Authors";
        iDiv3.appendChild(h4);
        var list3 = document.createElement('ul');
        list3.className = "list-unstyled mt-3 mb-4";
        var listItem5 = document.createElement('li');
        listItem5.innerText = pair.top_keywords[0]
        list3.appendChild(listItem5)
        var listItem6 = document.createElement('li');
        listItem6.innerText = pair.top_keywords[1]
        list3.appendChild(listItem6)
        var listItem7 = document.createElement('li');
        listItem7.innerText = pair.top_keywords[2]
        list3.appendChild(listItem7)
        iDiv3.appendChild(list3)

        var iDiv4 = document.createElement('div');
        iDiv4.className = "papers-by-years"
        iDiv4.style = "position: relative; height:(300/index)px; width:(300/index)px"
        var canvas = document.createElement('canvas')
        canvas.id = "myChart" + index
        canvas.width = "100"
        canvas.height = "100"
        iDiv4.appendChild(canvas)
        iDiv3.appendChild(iDiv4)
        //endregion
        //region button
        var iDiv5 = document.createElement('div');
        var button = document.createElement('button')
        button.type = "button"
        button.className = "btn btn-lg btn-block btn-primary"
        button.innerText = "Go To";
        button.id = "buttonx" + index

        button.addEventListener('click', function () {
            console.log('pair index: ' + button.id)
            let index = button.id.slice(-1)
            var d = keywords.keyword_pairs[index]["articles"]
            $('#example').DataTable().destroy();
            $('#example').DataTable({
                data: d,
                searchPanes: {
                    layout: 'columns-1',
                    threshold: 1
                },
                responsive: true,
                dom: '<"dtsp-verticalContainer"<"dtsp-verticalPanes"P>l<"dtsp-dataTable"frtip>>',
                pageLength: 20,
                columns: [
                    {data: 'pm_id'},
                    {data: 'title'},
                    {data: 'authors'},
                    {data: 'article_date'},
                    {data: 'article_type'},
                    {data: 'pubmed_link'},
                    {data: 'article_link'}
                ]
            });
            document.getElementById("example").style.visibility = "visible"
            document.getElementById("header").style.visibility = "visible"
            document.getElementById("header").innerText = "Articles for query: " + pair.value;

        }, false);

        iDiv5.appendChild(button);
        iDiv3.appendChild(iDiv5)
        iDiv.appendChild(iDiv3);
        //endregion

        document.getElementById("keyword-pair-container").appendChild(iDiv);
        this.create_chart(pair.publication_year, pair.publication_year_values, index);
    }

    create_chart(publication_year, year_values, index) {
        var ctx = document.getElementById('myChart' + index);
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