# southwest-properties
Aggregate rental data in Nova Scotia


### Current feature in development
- Add ability to template DAGS based on a config file
    - DAGs for site fetch when the output will be dumped into some object storage will largely be similar. We will be essentially just be scheduling a scrape job and defining an endpoint to dump the data into