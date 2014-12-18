#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()
import os, stat
import sys

sys.path.insert(0, '/Users/Shared')

# Load in the string that contains the HTML and places to 
# substitute data and query strings
from area_page_string import page_string

sys.path.insert(0, '/Users/emonson/Programming/Titan_git/Titan/build/lib')
sys.path.insert(0,'/Users/emonson/Programming/Titan_git/Titan/build/TPL/VTK/Wrapping/Python')

import vtk
from titan.TextAnalysis import vtkTokenization
from titan.Trilinos import vtkTrilinosLSAProjection
from titan.DataAnalysis import vtkCosineSimilarityTable

import json

form = cgi.FieldStorage()

query_string = form.getvalue('query','books')

lsa_data_path = '/Users/Shared'

fd_reader = vtk.vtkTableReader()
fd_reader.SetFileName(os.path.join(lsa_data_path,"CH_FeatureDictionary.vtk"))

fw_reader = vtk.vtkArrayReader()
fw_reader.SetFileName(os.path.join(lsa_data_path,"CH_FeatureWeighting.txt"))

lsv_reader = vtk.vtkArrayReader()
lsv_reader.SetFileName(os.path.join(lsa_data_path,"CH_LeftSingularVectors.txt"))

rsv_reader = vtk.vtkArrayReader()
rsv_reader.SetFileName(os.path.join(lsa_data_path,"CH_RightSingularVectors.txt"))

sv_reader = vtk.vtkArrayReader()
sv_reader.SetFileName(os.path.join(lsa_data_path,"CH_SingluarValues.txt"))

power_weighting = vtk.vtkPowerWeighting()
power_weighting.SetInputConnection(0, sv_reader.GetOutputPort())
power_weighting.SetPower(-0.5)

# Setup the query pipeline ...
query_document_array = vtk.vtkIdTypeArray()
query_document_array.SetName("document")

query_text_array = vtk.vtkUnicodeStringArray()
query_text_array.SetName("text")

query_document_array.InsertNextValue(query_document_array.GetNumberOfTuples())
query_text_array.InsertNextValue(unicode(query_string))

query_document_table = vtk.vtkTable()
query_document_table.AddColumn(query_document_array)
query_document_table.AddColumn(query_text_array)

query_document_reader = vtk.vtkPassThrough()
query_document_reader.SetInputConnection(0, query_document_table.GetProducerPort())

query_tokens = vtkTokenization()
query_tokens.SetInputConnection(0, query_document_reader.GetOutputPort())

query_projection = vtkTrilinosLSAProjection()
query_projection.SetInputConnection(0, query_document_reader.GetOutputPort())
query_projection.SetInputConnection(1, query_tokens.GetOutputPort())
query_projection.SetInputConnection(2, fd_reader.GetOutputPort())
query_projection.SetInputConnection(3, fw_reader.GetOutputPort())
query_projection.SetInputConnection(4, lsv_reader.GetOutputPort())

similarity_table = vtkCosineSimilarityTable()
similarity_table.SetInputConnection(0, query_projection.GetOutputPort())
similarity_table.SetInputConnection(1, rsv_reader.GetOutputPort())
similarity_table.SetInputConnection(2, power_weighting.GetOutputPort())
similarity_table.SetVectorDimension(1)
similarity_table.SetSecondFirst(False)
similarity_table.SetMinimumThreshold(0)
similarity_table.SetMinimumCount(0)
similarity_table.SetMaximumCount(100)		# Default = 10

# Execute the pipeline ...
similarity_table.Update()

sim_table = similarity_table.GetOutput()
ids = sim_table.GetColumnByName('target')
sims = sim_table.GetColumnByName('similarity')

num_docs = rsv_reader.GetOutput().GetArray(0).GetExtent(1).GetEnd()
sim_list = [0.0]*num_docs
for ii in range(ids.GetNumberOfTuples()):
	sim_list[ids.GetValue(ii)] = sims.GetValue(ii)

sim_data = []
for ii in range(len(sim_list)):
	tmp_dict = {}
	tmp_dict['x'] = ii
	tmp_dict['y'] = sim_list[ii]
	sim_data.append(tmp_dict)
	
# Get set of terms for later comparison with query
features_array = fd_reader.GetOutput().GetColumnByName('text')
features_set = set()
for ii in range(features_array.GetNumberOfTuples()):
    features_set.add(features_array.GetValue(ii))

terms = query_tokens.GetTokens().GetColumnByName('text')
num_terms = terms.GetNumberOfTuples()
term_list = []
for ii in range(num_terms):
	term_list.append(terms.GetValue(ii))

term_set = set(term_list)
used_terms_list = list(features_set.intersection(term_set))

term_string = ' '.join(used_terms_list)
data_string = 'var data = ' + json.dumps(sim_data) + ';\n\n'

pg_string = page_string()
pg_string = pg_string.replace('QUERY_TERMS_GO_HERE', term_string)
pg_string = pg_string.replace('SVD_RANK_GOES_HERE', str(sv_reader.GetOutput().GetArray(0).GetSize()))
pg_string = pg_string.replace('POWER_WEIGHT_GOES_HERE', str(power_weighting.GetPower()))
pg_string = pg_string.replace('DATA_GOES_HERE', data_string)

print "Content-type:text/html\r\n\r\n"
print pg_string
