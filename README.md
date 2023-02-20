#Download and Index

dl_and_index

Script to download a test collection of documents and queries, and index them into an elasticsearch index.

Right now only works with the Cran collection.


Elasticsearch index templates are in the index_profiles subfolder.

(WIP)

#Running

To execute it, have an elasticsearch instance running on your environment.
Then configure the elasticsearch connection in the following files:

File: indexers\baseindexer.py
In the initElasticSearch() method.

File: get_search_metrics.py
In the initElasticSearch() method.

With those two configured, run them in this order:

1. dl_and_index.py
2. get_search_metrics.py

It will output the metrics for the queries in the cran dataset, precision, recall, F1 and DCG.

##Environment

To set it up create an environment. With Conda use:
```
conda create --prefix ./dl_and_index python=3.10
```
The activate it:
```
conda activate ./dl_and_index
```
And install the necessary dependencies:

```
pip install -r requirements.txt
```

When you are done, don't forget to deactivate it!

```
conda deactivate
```