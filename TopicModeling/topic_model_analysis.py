from manage_path import *
from compute_topic import *
from get_data import *

import gensim
import pyLDAvis.gensim
from gensim.corpora import Dictionary

import os
from pathlib import Path

import plotly
import plotly.graph_objs as go
import plotly.io as pio
#from itertools import repeat
from collections import deque

# The model with model_name we want to load
def load_model(model_name,num_topics):
    """Load LDAModel for analysis"""
    print('Loading LDAModel ....')
    topic_name ="_{}topics".format(num_topics)
    file_name = model_name + topic_name
    LDAModel_directory = get_LDAModel_directory()
    load_path = LDAModel_directory / "{}/{}".format(file_name,file_name)
    load_path = str(load_path)
    lda = gensim.models.ldamulticore.LdaMulticore.load(load_path)
    print('LDAModel loaded!!!')
    return lda

def document_topic_distribution(corpus,matrix_object,model,model_name,num_topics,minimum_probability=0.10):
    print('caculating document_topic_distribution ...')
    # minimum_probability is our threshold
    document_topics = model.get_document_topics(corpus,minimum_probability=minimum_probability)
    # convert document_topics, which is a gesim corpus, to numpy array
    document_topic_distribution_numpy = gensim.matutils.corpus2dense(document_topics,num_terms=int(num_topics))
    # need to transpose it because gensim represents documents on columns token on index
    document_topic_distribution_numpy = np.transpose(document_topic_distribution_numpy)
    # combine document_topic_distribution with index from matrix and columns represents gensim topics
    document_topic_distribution_pandas = pd.DataFrame(data=document_topic_distribution_numpy,index=matrix_object.index,columns=np.arange(int(num_topics)))
    # Only get the top three topics per document
    document_topic_distribution_pandas = document_topic_distribution_pandas[document_topic_distribution_pandas.rank(axis=1,method='max',ascending=False) <= 3]
    print('caculating document_topic_distribution done!!!')
    # Save the dataframe to csv
    print('saving document_topic_distribution...')
    result_directory = get_result_directory()
    if not result_directory.is_dir():
        create_directory(result_directory)
    file_name = result_directory / '{}_{}topics.csv'.format(model_name,num_topics)
    document_topic_distribution_pandas.to_csv(file_name)
    print('document_topic_distribution saved!!!')
    
def get_document_topic_distribution(model_name,num_topics):
    result_directory = get_result_directory()
    file_name = result_directory / '{}_{}topics.csv'.format(model_name,num_topics)
    return file_name
    
def save_pyldavis2html(model,corpus,dictionary,model_name,num_topics):
    print('preparing pyLDAvis ...')
    vis = pyLDAvis.gensim.prepare(model, corpus, dictionary, sort_topics=False)
    print('pyLDAvis done!!!')
    print('saving pyLDAvis to html ...')
    result_directory = get_result_directory()
    if not result_directory.is_dir():
        create_directory(result_directory)
    file_name = result_directory / '{}_{}topics.html'.format(model_name,num_topics)
    # Save visualization
    pyLDAvis.save_html(vis, str(file_name))
    print('pyLDAvis to html saved!!!')

def get_document_item(document,position):
    return str(document).split(',')[position]

def topicXtime_vusualize(topic_matrix,model_name):
    def get_dealer_by_ID(matrix,dealer_id,model_name):
        result = matrix.loc[matrix['dealer'] == dealer_id].copy().drop(labels='dealer',axis=1)
        return (result,dealer_id,model_name)
    
    def topicXtime(dealer_data):
        dealer_data,dealer_id,model_name = dealer_data[0],dealer_data[1],dealer_data[2]

        heatmap_data = [
            go.Heatmap(
                z=dealer_data.values.tolist(),
                zmin=0,
                zmax=1,
                x=dealer_data.columns,
                y=dealer_data.index,
                colorscale='Jet',
            )
        ]

        layout = go.Layout(
            title='{} Dealer {}: Topic-Time'.format(model_name,dealer_id),
        )

        fig = go.Figure(data=heatmap_data, layout=layout)

        image_directory = get_image_directory() / '{}'.format(model_name)
        if not image_directory.is_dir():
            create_directory(image_directory)
        file_path = image_directory / '{}_dealer{}_topic_time.svg'.format(model_name,dealer_id)
        pio.write_image(fig, str(file_path))
    
    dealer_df_list = list(map(lambda x: get_dealer_by_ID(topic_matrix,x,model_name),list(topic_matrix['dealer'].unique())))
    deque(map(topicXtime,dealer_df_list))
    
def main():
    model_name = str(sys.argv[1])
    num_topics = int(sys.argv[2])
    # Fro visualization
    corpus = load_corpus(model_name)
    id2word = load_id2word(model_name)
    dictionary = Dictionary.from_corpus(corpus,id2word=id2word)
    # Load LDAModel
    model = load_model(model_name,num_topics)
    save_pyldavis2html(model, corpus, dictionary,model_name,num_topics)

    # Load data to caculate matrix
    data = load_data()
    if (model_name=='Dc_v1'):
        matrix_object = compute_Dc_v1(data)
    if (model_name=='Dc_v2'):
        matrix_object = compute_Dc_v2(data)
    if (model_name=='Dc_v3'):
        matrix_object = compute_Dc_v3(data)
    if (model_name=='Tc_v1'):
        matrix_object = compute_Tc_v1(data)
	# Save document_topic_distribution
    document_topic_distribution(corpus,matrix_object,model,model_name,num_topics)

if __name__ == "__main__":
    main()