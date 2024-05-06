# southwest-properties

Aggregate rental data in Nova Scotia

### Features in development

- Updating scraping for `444rent.com` and `apartments.com`. Listings will be aggregated into a single table for viewing, rather than individual tables for each site.

### Changes

- Add ability to template DAGS based on a config file

  - DAGs can now be created by added a `.yaml` file to the dag_factory directory.

- Create generic operators

  - RedisToPostgres
    - This operator is used to save the raw data to postgres. This way we can have a record of the raw data as it was scraped over the lifecycle of the scraper.
  - Transform
    - This operator allows the user to apply a specified transform function on the most recently scraped data. Specify the function name and where it is and the operator will do the rest.
  - Load
    - This operator takes care of inserting the processed data into the tables. It has three main functions.
      - Archive: The operator finds records that were not scraped but are still listed as active and archives them.
      - Adding new: The operator finds new records and inserts them
      - Update Existing: The operator finds existing records and compares them to the scraped ones. If there are any changes, it keeps track of them, and then updates the the main record.

- Better table structure
  - Now have separate tables to keep tracked of scraped records, active records, archived records, the records themself, and changes. See `sql/application_schemas.sql` for the first revision.
  - Currently creating a master listings table with core fields for the lsiting to have. Extra information that is unique to the listing providers (some sites offer different information) is then aggregated in a unique table for that listing source. See `sql/listings_schemas.sql` and  `sql/444rent_schemas` for current iteration. 

### Application Sources

- Current
  - [halifax.ca](https://www.halifax.ca/business/planning-development/applications)
- Planned
  - [halifaxdevelopments.ca](https://halifaxdevelopments.ca/)

### Rental Sources