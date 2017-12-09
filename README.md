# azure-omslogs2blob

This code does the following:

* Gets your logfiles from loganalytics based on the defined query
* Get the elements from your json output and create a csv file
* Copy this tmp csv file to your blob storage

Secret values are stored in the variables part of your Azure Automation account and note that for now the Log Analytics python API only supports legacy SQL.
