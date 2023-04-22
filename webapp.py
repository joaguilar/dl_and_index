import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json
from elasticsearch import Elasticsearch
from nltk.tokenize import sent_tokenize 
from sentence_transformers import SentenceTransformer

def get_vector(q):
    sentences =[]
    sentences.append(q)
    # print (sentences)

    # api_url = "http://localhost:5000/v1/models/gtr-t5-base/versions/1:predict"

    # body = {
    #     "data": sentences
    # }
    # headers =  {"Content-Type":"application/json"}
    # response = requests.post(api_url,data=json.dumps(body),headers=headers)

    
    model = SentenceTransformer("gtr-t5-base")
    vector = model.encode(sentences)

    # response_dict = response.json()
    # result_list = response_dict.get("result")
    # vector = result_list[0]['vector']
    # print(vector)
    return vector

def query_elastic(index, query, vector):
    es = Elasticsearch(hosts=["http://localhost:9200"])

    qs = {
            "script_score": {
            "query": {
                "match": {
                "sentence": query
                }
            },
            "script": {
                "source": """
                double value = doc['sentence-vector'].size() == 0 ? 0 : dotProduct(params.query_vector, 'sentence-vector');
                return sigmoid(1, Math.E, -value); 
                """,
                "params": {"query_vector":vector}}
                }
    }  

    r = es.search(
        index=index,
        query=qs,
    )

    return r

def query_elastic_articles(index, query, vector):
    es = Elasticsearch(hosts=["http://localhost:9200"])

    qs = {

        "has_child": {
            "type": "sentence",
            "score_mode": "max", 
            "query": {
                "script_score": {
                "query": {
                    "match": {
                    "sentence":{
                        "query": query,  
                        "boost":0.1
                    }
                    
                    }
                },
                "script": {
                    "source": """
                        double value = doc['sentence-vector'].size() == 0 ? 0 : dotProduct(params.query_vector, 'sentence-vector');
                        return sigmoid(1, Math.E, -value); 
                        """,
                    "params": {
                    "query_vector": vector
                    }
                }
                }
            }, "inner_hits": {
        "_source": ["sentence"], 
        "size": 2, 
        "highlight": {
          "fields": {
            "sentence":{}
          },
          "boundary_scanner": "sentence",
          "pre_tags": [""],
          "post_tags": [""]
        }
      }
        }        
    }  

    r = es.search(
        index=index,
        query=qs,
    )

    return r

def vector_as_text(vector, size):
    vector_text = "["
    for i,v in enumerate(vector):
        if (i % 3 == 0):
            vector_text = vector_text +'\n'
        vector_text = vector_text + str(v) + ", "
        if (i > size):
            vector_text = vector_text + "..., "
            break

    vector_text += "]"
    return vector_text

st.title('Semantic Search Demo')
with st.form('query', clear_on_submit=False):
    query = st.text_input('Query', 'What is the air-speed velocity of an unladen swallow?')
    st.markdown("""
        Some example queries:
        * *do we consider sustainability in every project*?
        * *What is the air-speed velocity of an unladen swallow?*
        * *why does the compressibility transformation fail to correlate the high speed data for helium and air*
    """)
    index = st.selectbox("Select Index",('articles-esggtrt5','articles-esg','articles-cran','articles-python'))
    individual_sentences = st.checkbox("Return Individual Sentences?", value=True)
    submitted = st.form_submit_button(label="Query")
if not submitted:
    st.stop()

## Temp:
test_sentences = sent_tokenize(query,language="english")
print("#\t","Sentence")
for i, s in enumerate(test_sentences):
    print(str(i),"\t",s)

vector = get_vector(query)


vector_text = vector_as_text(vector,27)

st.markdown("## Query Vector")
st.text(str(vector_text))
r = {}
if individual_sentences:
    r = query_elastic(index, query, vector)
else:
    r = query_elastic_articles(index, query, vector)

# st.text(r)
results = []
if individual_sentences:
    for i,hit in enumerate(r['hits']['hits']):
        result = {}
        result['Id'] = hit['_source']['my_id']
        result['Title'] = hit['_source']['title']
        result['Score'] = hit['_score']
        result['sentence'] = hit['_source']['sentence']
        av = hit['_source']['sentence-vector']
        # print(hit['_source'])
        result['sentence-vector'] = vector_as_text(av,10)
        results.append(result)
else:
    for i,hit in enumerate(r['hits']['hits']):
        result = {}
        result['Id'] = hit['_source']['my_id']
        result['Title'] = hit['_source']['title']
        result['Score'] = hit['_score']
        content = hit['_source']['content']

        # Inner hits:
        inner_hit = hit["inner_hits"]["sentence"]["hits"]["hits"][0]
        sentence = inner_hit["_source"]["sentence"]
        # print("Sentence: "+sentence)
        content = content.replace(sentence,"<b> *"+sentence+"* </b>")
        # result['Content'] = hit['_source']['content']
        result['Content'] = content
        results.append(result)


df = pd.DataFrame.from_dict(results)
st.markdown("## Results")
st.table(df)
st.markdown("### Results (Raw)")
st.text(json.dumps(r,indent=4))
