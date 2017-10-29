# itf-web-scraper
A simple python script that scrapes the http://www.itftennis.com/home.aspx to automate the retrieval of relevant recruiting data. 
Note: The current version has only the minimal features needed. Version 2 will use pandas (http://pandas.pydata.org) for more complicated data analysis and dataframe storage. Version 3 will cross reference historic junior data and collegiate rankings; the end goal for this version is to build a machine learning predictor of a junior players future results. This will look at a given junior players highest ranking, record, number of tournaments played, etc. and their success in college. 
* Uses PhantomJS and selenium to access itf website in headless mode
* Retrieves and parses list of junior tournaments in specified date range
* Loads each tournament page and results (ajax call)
* Parses and retrieves only the results needed by coaches based on tournament grade (i.e. only quarterfinalists for Grade 2 ITFs)
* Converts tournament data to CSV
* Uploads CSV to Dropbox folder shared with coaches via Dropbox API
