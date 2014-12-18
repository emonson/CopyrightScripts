#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()
import os, stat

from area_script_string import script_string

# Trying to add to PYTHONPATH
import sys
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
	
terms = query_tokens.GetTokens().GetColumnByName('text')
num_terms = terms.GetNumberOfTuples()
term_list = []
for ii in range(num_terms):
	term_list.append(terms.GetValue(ii))

f = open(os.path.join(lsa_data_path,'sim_data.json'),'w')
f.write(json.dumps(sim_data, indent=2))
f.close()

os.chmod(os.path.join(lsa_data_path,'sim_data.json'), stat.S_IMODE(0o0666))

print "Content-type:text/html"
print
print "<p>Query terms retained: <b>%s</b></p>" % (' '.join(term_list),)
