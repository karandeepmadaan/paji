import inchlib_clust
import csv
import numpy


def select_filters(c) :
    #section for selection of colomn on which filter has to be applied
    print "COLOUMNS AVAILABLE FOR FILTERING"
    
    header_dict = {};
    for i in range(0, len(c.header)):
        print i + 1, ' ',
        print c.header[i]
        temp = {c.header[i]:i}
        header_dict.update(temp)
    print        
    
    
    print "TOTAL NUMBER OF COLUMNS ", len(c.header)
    #print "                     ******************************************************"
    print "ENTER NUMBER OF COLOUMNS ON WHICH YOU WANT TO APPLY FILTERS"
    no_of_col = int(raw_input()) # var that holds total number of coloumns on which we wantr to apply filters

    #print "                     ******************************************************"
    #section for slection of filter
    print "AVAILABLE FILTERS FOR THESE COLUMNS"
    avail_operations = {'>' : 0, '<' : 1, '>=':2 , '<=' : 3}; #dictonary holding the values and operations
    
    print avail_operations.keys(); #printing all keys of avail_operations
    '''for i in range(1, len(avail_operations) + 1) :
        print i , ' ', 
        print avail_operations[i]'''
    print

    #print "                     ******************************************************"
    print "ENTER THE NUMBER OF COLUMN , FILTERING OPERATION AND VALUE FOR FILTRERING"
    print"ORDER OF ENTRY"
    print "COLOUMN NAME"  
    print"FILTER NAME"  
    print"VALUE OF FILTER" 

    filter_matrix = [[0 for x in range(0, 3)] for x in range (0, no_of_col)]
    
    i = 0
    while i  < (no_of_col) :
        col_name = raw_input() #name of column
        if(header_dict.has_key(col_name) == False) :
            print "ALERT !! you have entered wrong column name : try again with following choices"
            print header_dict.keys()
            continue
        oper_name = raw_input() #value of operation
        if(avail_operations.has_key(oper_name) == False) :
            print "ALERT !! you have entered wrong filter name : try again with following filters"
            print avail_operations.keys() 
            continue
        value = float(raw_input()) #value of operation
                 

        print "FILTER ", i + 1
        print col_name," ", oper_name, " ", value
        filter_matrix[i][0] = header_dict[col_name]
        filter_matrix[i][1] = avail_operations[oper_name]
        filter_matrix[i][2] = value
        i = i + 1

    return filter_matrix


LINKAGES = ["single", "complete", "average", "centroid", "ward", "median", "weighted"]
RAW_LINKAGES = ["ward", "centroid"]

DISTANCES = {"numeric": ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", "euclidean", "mahalanobis", "minkowski", "seuclidean", "sqeuclidean"],
              "binary": ["dice","hamming","jaccard","kulsinski","matching","rogerstanimoto","russellrao","sokalmichener","sokalsneath","yule"]}


#section for the selection of linkage type in dandrogram while clustering
print "AVAILABLE CHOICES FOR LINKAGE "
print 
print
for i in range(0, len(LINKAGES)):
    print i + 1, '  ',  
    print LINKAGES[i]
print
print "SELECT INDEX OF YOUR LINKAGE CHOICE ",
index_lin = int(raw_input()) - 1  #var which hold the index of linkage
print
print


#section for selection of method for clustering
print "AVAILABLE CHOICES FOR CLUSTERING"
print
for i in range(0, len(DISTANCES["numeric"])) :
    print i + 1, '  ',
    print DISTANCES["numeric"][i]

print 
print "SELECT INDEX OF YOUR CHOICE OF CLUSTERING ",
index_clust = int(raw_input()) - 1 #var which hold the index for clustering
print 
print
 

#instantiate the Cluster object
c = inchlib_clust.Cluster()


# read csv data file with specified delimiter, also specify whether there is a header row, the type of the data (numeric/binary) and the #string representation of missing/unknown values
c.read_csv(filename="z_my_data.csv", delimiter=",", header=bool, missing_value=False, datatype="numeric/binary")
#print c.filename


print "                     ******************************************************"

print "FOR FILTERING DISSIMILARITY MATRIX ALONG ROWS"
matrix_row = select_filters(c)

print

print "                     ******************************************************"
print "FOR FILTERING DISSIMILARITY MATRIX ALONG COLUMNS"
matrix_col = select_filters(c)
for i in range (0, len(matrix_col)):
    matrix_row.append(matrix_col[i])
print matrix_row
c.read_csv_2(matrix_row, matrix_col, filename="z_my_data.csv", delimiter="," ,header=bool, missing_value=False, datatype="numeric/binary")
# c.read_data(data, header=bool, missing_value=str/False, datatype="numeric/binary") use read_data() for list of lists instead of a data file

#c.intermediate_file("z_first_inetermediate_file")

#c.write_csv("z_first_file.csv", delimete = ",")

# normalize data to (0,1) scale, but after clustering write the original data to the heatmap
c.normalize_data(feature_range=(0, 1), write_original=bool)

#print "**************data_names*************"
## cluster data according to the parameters
c.cluster_data(c.data_names,filename = "z_yulesq.csv", row_distance= DISTANCES["numeric"][index_clust] , row_linkage=LINKAGES[index_lin], axis="row", column_distance="yule", column_linkage="ward")

print c.clustering


# instantiate the Dendrogram class with the Cluster instance as an input
d = inchlib_clust.Dendrogram(c)

# create the cluster heatmap representation and define whether you want to compress the data by defining the maximum number of heatmap rows,# #the resulted value of compressed (merged) rows and whether you want to write the features
d.create_cluster_heatmap(compress=int, compressed_value="median", write_data=bool)

#read metadata file with specified delimiter, also specify whether there is a header row
#d.add_metadata_from_file(metadata_file="example_metadata.csv", delimiter=",", header=bool, metadata_compressed_value="frequency")

# read column metadata file with specified delimiter, also specify whether there is a 'header' column
#d.add_column_metadata_from_file(column_metadata_file="example_column_metadata.csv", delimiter=",", header=bool)

# export the cluster heatmap on the standard output or to the file if filename specified
d.export_cluster_heatmap_as_json("z_cluster_api_file6.json")
#d.export_cluster_heatmap_as_html("/path/to/directory") function exports simple HTML page with embedded cluster heatmap and dependencies to #given directory 
