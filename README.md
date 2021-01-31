# Mentis Parchment
This project created for BOUN SWE 574 Course at Fall 2020. We are assigned as Team #2. 
Our [team members](https://github.com/8hk/AEK/wiki/Crew) are currently working as software engineers from different companies at Istanbul/Turkey. 

Project aims to search keywords provided by user at [PubMed](https://pubmed.ncbi.nlm.nih.gov) with using [Entrez API](https://www.ncbi.nlm.nih.gov/books/NBK25497/) and harvest the Entrez API result with using [Web Annotation Model](https://www.w3.org/TR/annotation-model/) and [UMLS API](https://documentation.uts.nlm.nih.gov/rest/search/index.html) to provide more reliable and intelligent search experience.

During the project we will document the project details under the [Wiki](https://github.com/8hk/AEK/wiki) section. If you have any question related to the project, please do not hesitate to contact a team member!

This project uses the following open source libraries:
- [jQuery 3.5.1](https://github.com/jquery/jquery/tree/3.5.1) with [MIT License](https://github.com/jquery/jquery/blob/3.5.1/LICENSE.txt)
- [Bootstrap v3.4.1](https://github.com/twbs/bootstrap/tree/v3.4.1) with [MIT License](https://github.com/twbs/bootstrap/blob/v3.4.1/LICENSE)
- [Bootstrap Tags Input](https://github.com/bootstrap-tagsinput/bootstrap-tagsinput/tree/0.8.0) with [MIT License](https://github.com/bootstrap-tagsinput/bootstrap-tagsinput/blob/0.8.0/LICENSE)
- [Chart.js](https://github.com/chartjs/Chart.js/) with [MIT License](hhttps://github.com/chartjs/Chart.js/blob/master/LICENSE.md)
- [Popper.js](https://github.com/popperjs/popper-core) with [MIT License](https://github.com/popperjs/popper-core/blob/master/LICENSE.md)
- [Holderjs](https://github.com/imsky/holder) with [MIT License](https://github.com/imsky/holder/blob/master/LICENSE)

##Tests
Run unit tests inside the "djangoapp" Docker container: `./manage.py test`

#### Coverage
Current code coverage can be seen in "coverage_report.txt".

In order to run the test coverage tool:

1. Run the tests as follows: `coverage run --omit=*/venv/*,*/migrations/*,*/__init__.py,*/settings.py,*/urls.py,*/tests.py,*/manage.py ./manage.py test`

2. View the coverage report via: `coverage report`