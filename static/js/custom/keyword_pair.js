import * as c from "./../chart.js-2.9.4/package/dist/Chart.min.js"

var keywords;
/*region remove articles are available
var article = {}
article["id"] = "31488767"
article["title"] = "Bipolar disorders and bipolarity: the notion of the mixing"
article["authors"] = "Giuseppe Tavormina, Aitana García-Estela, Ludovic Samalin, Anabel Martínez-Arán"
article["publication_year"] = "2017"
article["article_types"] = "journal"
article["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"
article["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"

var article2 = {}
article2["id"] = "33422826"
article2["title"] = "Does cognitive impairment in bipolar disorder impact on a SIMPLe app use?"
article2["authors"] = "Caterina Del Mar Bonnín, Brisa Solé, María Reinares"
article2["publication_year"] = "2020"
article2["article_types"] = "Journal of affective disorders"
article2["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/33422826/"
article2["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/33422826/"

var article3 = {}
article3["id"] = "33422825"
article3["title"] = "The risk of anxiety disorders in children of parents with severe psychiatric disorders: a systematic review and meta-analysis."
article3["authors"] = "Getinet Ayano, Kim Betts, Joemer Calderon Maravilla"
article3["publication_year"] = "2017"
article3["article_types"] = "journal"
article3["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/33422825/"
article3["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/33422825/"

var article4 = {}
article4["id"] = "316546567"
article4["title"] = "Bipolar disorders and bipolarity: the notion of the mixing"
article4["authors"] = "James A Karantonis, Susan L Rossell, Michael Berk"
article4["publication_year"] = "2002"
article4["article_types"] = "journal"
article4["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/316546567/"
article4["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/316546567/"

var article5 = {}
article5["id"] = "31488767"
article5["title"] = "The mental health and lifestyle impacts of COVID-19 on bipolar disorder"
article5["authors"] = "Clara S Humpston, Paul Bebbington, Steven Marwaha"
article5["publication_year"] = "2013"
article5["article_types"] = "journal"
article5["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"
article5["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"

var article6 = {}
article6["id"] = "31488767"
article6["title"] = "Bipolar disorder: Prevalence, help-seeking and use of mental health care in England. Findings from the 2014 Adult Psychiatric Morbidity Survey"
article6["authors"] = "Yagmur Kir, Adnan Kusman, Busra Yalcinkaya"
article6["publication_year"] = "2015"
article6["article_types"] = "journal"
article6["pubmed_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"
article6["article_link"] = "https://pubmed.ncbi.nlm.nih.gov/31488767/"
var articles = []
articles = articles.concat(article)
articles = articles.concat(article2)
articles = articles.concat(article3)
articles = articles.concat(article4)
articles = articles.concat(article5)
articles = articles.concat(article6)
articles = articles.concat(article)
articles = articles.concat(article2)
articles = articles.concat(article3)
articles = articles.concat(article4)
articles = articles.concat(article5)
articles = articles.concat(article6)

//endregion*/
class Pair {

    constructor(data) {
        console.log("data: " + data)
        keywords = JSON.parse(data);
        //region remove when articles are available
        /*for (let k in keywords.keyword_pairs) {
            keywords.keyword_pairs[k]["articles"] = []
            for (let i = 0; i < keywords.keyword_pairs[k].papers_number; i++) {
                if (i < articles.length)
                    keywords.keyword_pairs[k]["articles"] = keywords.keyword_pairs[k]["articles"].concat(articles[i])
                else
                    keywords.keyword_pairs[k]["articles"] = keywords.keyword_pairs[k]["articles"].concat(articles[0])
            }
        }*/
        //endregion
        var cards = ""
        for (let key in keywords.keyword_pairs) {
            this.create_card(keywords.keyword_pairs[key], key);
        }
    }

    create_card(pair, index) {
        //region div elements
        var iDiv = document.createElement('div');
        iDiv.id = 'block' + index;
        iDiv.className = 'card box-shadow';

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
                    layout: 'columns-1'
                },
                responsive: true,
                dom: '<"dtsp-verticalContainer"<"dtsp-verticalPanes"P><"dtsp-dataTable"frtip>>',
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