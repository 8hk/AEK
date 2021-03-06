import * as c from "./../chart.js-2.9.4/package/dist/Chart.min.js"

var keywords;

class Pair {

    constructor(data) {
        console.log("data: " + data)
        keywords = JSON.parse(data);
        let keyword_dim_dict = this.get_keyword_dimension_dict(keywords.dimensions)
        var cards = ""

        this.add_to_dimension_list("main query: \"" + keywords.mainquery + "\"");

        for (let b = 0; b < keywords.dimensions.length; b++) {
            let text = "dimension" + b.toString() + " : ";
            for (let c = 0; c < keywords.dimensions[b].keywords.length; c++) {
                text = text + "\"" + keywords.dimensions[b].keywords[c] + "\" ";
            }
            this.add_to_dimension_list(text);
        }

        for (let key in keywords.keyword_pairs) {
            //check each keyword empty or not
            if (!keywords.keyword_pairs[key].empty_result) {
                //if keyword is not empty list
                this.create_card(keywords.keyword_pairs[key], key, keyword_dim_dict, keywords.mainquery);
            } else {
                var combination = ''
                var title = this.get_title(keywords.keyword_pairs[key].value, keyword_dim_dict, keywords.mainquery);
                for (let t = 0; t < title.length; t++) {
                    combination = combination + title[t] + " "
                }
                this.add_to_empty_list(combination)
            }
        }
    }

    add_to_empty_list(text) {
        var empty_list = document.createElement('li');
        empty_list.innerText = text;
        document.getElementById("empty-result-list").style.visibility = "visible"
        document.getElementById("empty-result-list").appendChild(empty_list);
    }

    add_to_dimension_list(text) {
        var dimention_list = document.createElement('li');
        dimention_list.innerText = text;
        document.getElementById("dimension-list").style.visibility = "visible"
        document.getElementById("dimension-list").appendChild(dimention_list);
    }

    get_keyword_dimension_dict(dimensions_list) {
        let keyword_dim_dict = {}
        for (let dim = 0; dim < dimensions_list.length; dim++) {
            let dimension_object = dimensions_list[dim];
            for (let key = 0; key < dimension_object["keywords"].length; key++) {
                if (!keyword_dim_dict.hasOwnProperty(dimension_object["keywords"][key]))
                    keyword_dim_dict[dimension_object["keywords"][key]] = "dimension " + dim.toString();
            }
        }
        return keyword_dim_dict;
    }

    create_card(pair, index, keyword_dim_dict, main_query) {
        //region div elements
        var iDiv = document.createElement('div');
        iDiv.id = 'block' + index;
        iDiv.className = 'card box-shadow flex-child';

        var iDiv2 = document.createElement('div');
        iDiv2.className = 'card-header';

        var title = this.get_title(pair.value, keyword_dim_dict, main_query)
        for (let t = 0; t < title.length; t++) {
            var h1 = document.createElement('h6');
            h1.className = "my-0 font-weight-normal";
            h1.innerText = title[t];
            iDiv2.appendChild(h1);
        }

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
        h3.innerText = "Top Authors";
        iDiv3.appendChild(h3);
        var list2 = document.createElement('ul');
        list2.className = "list-unstyled mt-3 mb-4";
        var listItem2 = document.createElement('li');
        listItem2.innerText = pair.top_authors[0]
        /*var link2 = document.createElement('a');
        link2.innerText = pair.top_authors[0];
        link2.href = "#";
        listItem2.appendChild(listItem2);*/
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
        h4.innerText = "Top Keywords";
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

            for (let ar = 0; ar < d.length; ar++) {
                let currentArticle = d[ar];
                currentArticle.filtered_authors = []
                let article_counter = 0;
                let author_list = ""
                let filtered_author_list = ""
                while (article_counter < currentArticle.authors.length) {
                    if (author_list == "") {
                        author_list = currentArticle.authors[article_counter];
                    } else {
                        author_list = author_list + ", " + currentArticle.authors[article_counter];
                    }
                    if (article_counter <= 5) {
                        if (filtered_author_list == "") {
                            filtered_author_list = currentArticle.authors[article_counter];
                        } else {
                            filtered_author_list = filtered_author_list + ", " + currentArticle.authors[article_counter];
                        }
                    }
                    article_counter++;
                }
                if (article_counter >= 5) {
                    filtered_author_list = filtered_author_list + ", " + "et al";
                }
                currentArticle.author_list = author_list;
                currentArticle.filtered_author_list = filtered_author_list;
            }

            $('#example').DataTable().destroy();
            $('#example').DataTable({
                data: d,
                searchPanes: {
                    threshold: 1,
                    columns: [2, 4],
                    dtOpts: {
                        dom: "tp",
                        paging: true,
                        pagingType: 'numbers',
                        searching: true,
                    }
                },
                responsive: true,
                dom: 'Plfrtip',
                bLengthChange: false,
                pageLength: 20,
                columns: [
                    {data: 'pm_id'},
                    {data: 'title'},
                    {data: 'author_list',},
                    {data: 'filtered_author_list',},
                    {data: 'article_date'},
                    {data: 'article_type'},
                    {
                        data: 'pubmed_link',
                        fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                            if (oData.pubmed_link) {
                                $(nTd).html("<a href='" + oData.pubmed_link + "'>" + oData.pubmed_link + "</a>");
                            }
                        }
                    },
                    {
                        data: 'article_link',
                        fnCreatedCell: function (nTd, sData, oData, iRow, iCol) {
                            if (oData.article_link) {
                                $(nTd).html("<a href='" + oData.article_link + "'>" + oData.article_link + "</a>");
                            }
                        }
                    }
                ],
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [4]
                    },
                    {
                        searchPanes: {
                            orthogonal: 'sp'
                        },
                        targets: [2, 3],
                        render: function (data, type, row) {
                            if (type === 'sp') {
                                return data.split(', ')
                            }
                            return data;
                        },

                    },
                    {
                        "targets": 2,
                        "visible": false,
                    }
                ]
            });
            document.getElementById("example").style.visibility = "visible"
            document.getElementById("header").style.visibility = "visible"
            document.getElementById("header").innerText = "Articles for query: " + pair.value;

            //scroll to specific div when go to button is clicked
            let target = document.getElementById("example")
            var scrollContainer = target;
            do { //find scroll container
                scrollContainer = scrollContainer.parentNode;
                if (!scrollContainer) return;
                scrollContainer.scrollTop += 1;
            } while (scrollContainer.scrollTop == 0);

            var targetY = 0;
            do { //find the top of target relatively to the container
                if (target == scrollContainer) break;
                targetY += target.offsetTop;
            } while (target = target.offsetParent);

            scroll = function (c, a, b, i) {
                i++;
                if (i > 30) return;
                c.scrollTop = a + (b - a) / 30 * i;
                setTimeout(function () {
                    scroll(c, a, b, i);
                }, 20);
            }
            // start scrolling
            scroll(scrollContainer, scrollContainer.scrollTop, targetY, 0);
        }, false);

        iDiv5.appendChild(button);
        iDiv3.appendChild(iDiv5)
        iDiv.appendChild(iDiv3);
        //endregion

        document.getElementById("keyword-pair-container").appendChild(iDiv);
        this.create_chart(pair.publication_year, pair.publication_year_values, index);
    }

    get_title(value, keyword_dim_dict, main_query) {
        var res = value.split(",");
        var title = []
        title.push("main query : \"" + main_query + "\"")
        for (let r = 1; r < res.length; r++) {
            let dim_info = keyword_dim_dict[res[r]]
            let keyword = res[r]
            title.push(dim_info + " : \"" + keyword + "\"")
        }
        return title
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
                            beginAtZero: true,
                            userCallback: function (label, index, labels) {
                                // when the floored value is the same as the value we have a whole number
                                if (Math.floor(label) === label) {
                                    return label;
                                }
                            },
                            fontSize: 10
                        },
                    }],
                    xAxes: [{
                        ticks: {
                            fontSize: 10
                        }
                    }]
                },
                responsive: true,
                legend: {
                    position: 'bottom',
                    display: true,

                },
                "hover": {
                    "animationDuration": 0
                },
                "animation": {
                    "duration": 1,
                    "onComplete": function () {
                        var chartInstance = this.chart,
                            ctx = chartInstance.ctx;

                        ctx.font = Chart.helpers.fontString(9, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'bottom';
                        this.data.datasets.forEach(function (dataset, i) {
                            var meta = chartInstance.controller.getDatasetMeta(i);
                            meta.data.forEach(function (bar, index) {
                                var data = dataset.data[index];
                                if (data < 20) {
                                    ctx.fillText(data, bar._model.x, bar._model.y - 10);
                                } else {
                                    ctx.fillText(data, bar._model.x, bar._model.y);
                                }
                            });
                        });
                    }
                },
            }
        });
    }
}

export {Pair};