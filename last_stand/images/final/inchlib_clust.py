#coding: utf-8
from __future__ import print_function

import csv, json, copy, re, argparse, os, urllib2

import numpy, scipy, fastcluster, sklearn
import scipy.cluster.hierarchy as hcluster
from sklearn import preprocessing
from scipy import spatial

LINKAGES = ["single", "complete", "average", "centroid", "ward", "median", "weighted"]
RAW_LINKAGES = ["ward", "centroid"]
DISTANCES = {"numeric": ["braycurtis", "canberra", "chebyshev", "cityblock", "correlation", "cosine", "euclidean", "mahalanobis", "minkowski", "seuclidean", "sqeuclidean"],
              "binary": ["dice","hamming","jaccard","kulsinski","matching","rogerstanimoto","russellrao","sokalmichener","sokalsneath","yule"]}

class Dendrogram():
    """Class which handles the generation of cluster heatmap format of clustered data. 
    As an input it takes a Cluster instance with clustered data."""

    def __init__(self, clustering):
        self.cluster_object = clustering
	#print("clustering_data ->", clustering.clustering) clustered data = [[1, 0, 3, 4],[2, 21,3,4]]
        self.datatype = clustering.datatype #binary/numeric
	#print("cluster_datatype ->",clustering.datatype)
        self.axis = clustering.clustering_axis # axis = rowise, column_wise, both
        self.clustering = clustering.clustering #clustered data
        self.tree = hcluster.to_tree(self.clustering)
	#print ("tree",self.tree) ??
        self.data = clustering.data #holds row wise data given in csv file
	#print("data ->", self.data)
        self.data_names = clustering.data_names #id_values of each row
	#print("data names",self.data_names) 
        self.header = clustering.header #column header
        #self.header.insert(0,"id")
	#print("self_header ->", self.header)
        self.dendrogram = False


##############################################
    #this function creates the dandrogram tree by using all info provided by the cluster object
    def __get_cluster_heatmap__(self, write_data):
	#here we require clustering instance to make dendrogam tree
        root, nodes = hcluster.to_tree(self.clustering, rd=True) # ask working of this func
	#print ("node-> ", hcluster.to_tree(self.clustering, True))
        node_id2node = {}
        dendrogram = {"nodes":{}}

        for node in nodes:	
	#providing id to a given node
            node_id = node.id
	    #print("printid-", node_id)
	#node_count = number of childrens if no_of _children == 1 then its a leaf
            if node.count == 1:
                node_id2node[node_id] = {"count":1, "distance":0}
	#if node is not leaf then assign left and right node value to it
            else:
		#print ("parent node", node_id)
                node_left_child = node.get_left().id
                node_right_child = node.get_right().id
		#now update id2node adequetly where count = no of nodes in a current node and distance = distance of current node
                node_id2node[node_id] = {"count":node.count, "distance":round(node.dist, 3), "left_child": node_left_child, "right_child": node_right_child}

	#assigning parent to to all child nodes of a given node where n is id of cur node
        for n, node in node_id2node.items():
	    #if there are more than one node in a given node
	    #print("node_id2 ->", node_id2node.items())
            if node["count"] != 1:
                node_id2node[node["left_child"]]["parent"] = n
                node_id2node[node["right_child"]]["parent"] = n

        for n, node in node_id2node.items(): #n is node_id i.e node number in the tree
	    #if node is leaf node
	    #print("count -> ", "count")
            if node["count"] == 1:
                data = self.data[n]  #contains column data per column
		#print("data ->", data)
                node["objects"] = [self.data_names[n]]
		#finding wheteher the given node is left child or right child of its parent and assigning quivalent node_id to it
                if node_id2node[node["parent"]]["left_child"] == n:
                    node_id2node[node["parent"]]["left_child"] = n
                else:
                    node_id2node[node["parent"]]["right_child"] = n

                if not write_data:
                    data = []

                node["features"] = data #assign a row data to the dendrogram
                dendrogram["nodes"][n] = node #assigning dendrogram thze node required node

	#if the given node is not a leaf node then assign the value of node to the dendrogram
        for n in node_id2node:
	     #print("n->", n, node_id2node[n]) 
             if node_id2node[n]["count"] != 1:
                dendrogram["nodes"][n] = node_id2node[n] #node_id2node contains the whole info a node in the tree
		print (dendrogram["nodes"][n])

     ###################################################### (self edited)
     # loop to find out the node_id using dendrogram_count 
     # if count == 1 the the current node must be a leaf node
        #dendrogram["feature_names"].append("id")
        for n in dendrogram["nodes"] :
            if dendrogram["nodes"][n]["count"] == 1:
                #print("id of node in dendrogram ->", dendrogram["nodes"][n]["objects"])
                dendrogram["nodes"][n]["features"].insert(0,dendrogram["nodes"][n]["objects"])
        #return the formed dandrogram         
        return dendrogram


###################################################3
    def __get_column_dendrogram__(self):
	#root and nodes have the coloumn clustered data
        root, nodes = hcluster.to_tree(self.cluster_object.column_clustering, rd=True)
	#node_id2node is a list
        node_id2node = {}
	#dendogram is a graph having node as starting address and a list followed by every node
        dendrogram = {"nodes":{}}
	
	#iterate through all nodes
        for node in nodes:
	    print ("id is:", id)
            node_id = node.id
	    # if node is leaf node
            if node.count == 1:
                node_id2node[node_id] = {"count":1, "distance":0}

            else:
	    # assign left and right child in form of graph to a node_id2
                node_left_child = node.get_left().id
                node_right_child = node.get_right().id
                node_id2node[node_id] = {"count":node.count, "distance":round(node.dist, 3), "left_child": node_left_child, "right_child": node_right_child}

	#assigning parent as the number of node in id2node
        for n in node_id2node:
            node = node_id2node[n]
            if node["count"] != 1:
                node_id2node[node["left_child"]]["parent"] = n
                node_id2node[node["right_child"]]["parent"] = n

	#if array list of nodes is not present in the dandrogram
        for n in node_id2node:
             if not n in dendrogram["nodes"]:
                dendrogram["nodes"][n] = node_id2node[n]

        return dendrogram


    # calling statement - d.create_cluster_heatmap(compress=int, compressed_value="median", write_data=bool)
    def create_cluster_heatmap(self, compress=False, compressed_value="median", write_data=True):
        """Creates cluster heatmap representation in inchlib format. By setting compress parameter to True you can
        cut the dendrogram in a distance to decrease the row size of the heatmap to specified count. 
        When compressing the type of the resulted value of merged rows is given by the compressed_value parameter (median, mean).
        When the metadata are nominal (text values) the most frequent is the result after compression.
        By setting write_data to False the data features won't be present in the resulting format."""
        self.dendrogram = {"data": self.__get_cluster_heatmap__(write_data)} #here dandrogram has been created in form of tree
	#print("dendrogram ->", self.dendrogram)
        self.compress = compress
        self.compressed_value = compressed_value
        self.compress_cluster_treshold = 0
	#check whether the data is to be compressed or not
        if self.compress and self.compress >= 0:
            self.compress_cluster_treshold = self.__get_distance_treshold__(compress)
            print("Distance treshold for compression:", self.compress_cluster_treshold)
            if self.compress_cluster_treshold >= 0:
                self.__compress_data__()
        else:
            self.compress = False

        if self.header and write_data:
            self.dendrogram["data"]["feature_names"] = [h for h in self.header]
        elif self.header and not write_data:
            self.dendrogram["data"]["feature_names"] = []
        
	#if axis == both then we have to do clustering along with row and coloumn
        if self.axis == "both" and len(self.cluster_object.column_clustering):
            column_dendrogram = hcluster.to_tree(self.cluster_object.column_clustering)            
            self.dendrogram["column_dendrogram"] = self.__get_column_dendrogram__()


    # as we already have clustered data in yules 
    def __compress_data__(self):
        nodes = {}
        to_remove = set()

        compressed_value2fnc = {
            "median": lambda values: [round(numpy.median(value), 3) for value in values],
            "mean": lambda values: [round(numpy.average(value), 3) for value in values],
        }
        
        for n in self.dendrogram["data"]["nodes"]:
            node = self.dendrogram["data"]["nodes"][n]

            if node["count"] == 1:
                objects = node["objects"]
                data = node["features"]
                node_id = n

                while self.dendrogram["data"]["nodes"][node["parent"]]["distance"] <= self.compress_cluster_treshold:
                    to_remove.add(node_id)
                    node_id = node["parent"]
                    node = self.dendrogram["data"]["nodes"][node_id]

                if node["count"] != 1:

                    if not "objects" in self.dendrogram["data"]["nodes"][node_id]:
                        self.dendrogram["data"]["nodes"][node_id]["objects"] = []
                        self.dendrogram["data"]["nodes"][node_id]["features"] = []
                    
                    self.dendrogram["data"]["nodes"][node_id]["objects"].extend(objects)
			
                    if data:
                        self.dendrogram["data"]["nodes"][node_id]["features"].append(data)

        for node in to_remove:
            self.dendrogram["data"]["nodes"].pop(node)

        for k in self.dendrogram["data"]["nodes"]:
            node = self.dendrogram["data"]["nodes"][k]
            if "objects" in node and node["count"] != 1:
                self.dendrogram["data"]["nodes"][k]["distance"] = 0
                self.dendrogram["data"]["nodes"][k]["count"] = 1
                self.dendrogram["data"]["nodes"][k].pop("left_child")
                self.dendrogram["data"]["nodes"][k].pop("right_child")
                rows = zip(*self.dendrogram["data"]["nodes"][k]["features"])
                self.dendrogram["data"]["nodes"][k]["features"] = compressed_value2fnc[self.compressed_value](rows)

        self.__adjust_node_counts__()

    #adjusting all the leaf node
    def __adjust_node_counts__(self):
	#an array to hold leafes
        leaves = []
	
	#if a node in dendrogram has a count less than 1 , i.e 0 then append it to leaves
        for n in self.dendrogram["data"]["nodes"]:
            if self.dendrogram["data"]["nodes"][n]["count"] > 1:
                self.dendrogram["data"]["nodes"][n]["count"] = 0
            else:
                leaves.append(n)
	
	#from a leaf go up to the dandrogram tree and increase the count for parent id by 1 for each node having parent parent_id
        for n in leaves:
            node = self.dendrogram["data"]["nodes"][n]
            parent_id = node["parent"]
	    #climbing up in the dendrogram tree from leaf to head
            while parent_id:
                node = self.dendrogram["data"]["nodes"][parent_id]
                self.dendrogram["data"]["nodes"][parent_id]["count"] += 1
                parent_id = False
                if "parent" in node:
                    parent_id = node["parent"]
    
    
    def __get_distance_treshold__(self, cluster_count):
        print("Calculating distance treshold for cluster compression...")
        if cluster_count >= self.tree.count:
            return -1
        
        i = 0
        count = cluster_count + 1
        test_step = self.tree.dist/2

        while test_step >= 0.1:
            count = len(set([c for c in hcluster.fcluster(self.clustering, i, "distance")]))
            if count < cluster_count:
                if i == 0:
                    return 0
                i = i - test_step
                test_step = test_step/2
            elif count == cluster_count:
                return i
            else:
                i += test_step

        return i+test_step*2

   #writing the whole dendrogram to the json file 
    def export_cluster_heatmap_as_json(self, filename=None):
        """Returns cluster heatmap in a JSON format or exports it to the file specified by the filename parameter."""
        dendrogram_json = json.dumps(self.dendrogram, indent=4)
        if filename:
            #open file and write dendrogram data into it
            output = open(filename, "w")
            output.write(dendrogram_json)
        return dendrogram_json


    #code for importing heatmap in html. make seperate html file and import this code to make dandrogram
    def export_cluster_heatmap_as_html(self, htmldir="."):
        """Export simple HTML page with embedded cluster heatmap and dependencies to given directory."""
        if not os.path.exists(htmldir):
            os.makedirs(htmldir)
        dendrogram_json = json.dumps(self.dendrogram, indent=4)
        template = """<html>
        <head>
            <script src="jquery-2.0.3.min.js"></script>
            <script src="kinetic-v5.1.0.min.js"></script>
            <script src="inchlib-1.1.0.js"></script>
            <script>
            $(document).ready(function() {{
                var data = {};
                var inchlib = new InCHlib({{
                    target: "inchlib",
                    max_height: 1200,
                    width: 1000,
                }});
                inchlib.read_data(data);
                inchlib.draw();
            }});
            </script>
        </head>

        <body>
            <div id="inchlib"></div>
        </body>
        </html>""".format(dendrogram_json)

        lib2url = {"inchlib-1.1.0.js": "http://localhost:8000/static/js/inchlib-1.1.0.js",
                    "jquery-2.0.3.min.js": "http://localhost:8000/static/js/jquery-2.0.3.min.js",
                    "kinetic-v5.1.0.min.js": "http://localhost:8000/static/js/kinetic-v5.1.0.min.js"}
        
        for lib, url in lib2url.items():
            try:
                source = urllib2.urlopen(url)
                source_html = source.read()

                with open(os.path.join(htmldir, lib), "w") as output:
                    output.write(source_html)
            except urllib2.URLError, e:
                raise Exception("\nCan't download file {}.\nPlease check your internet connection and try again.\nIf the error persists there can be something wrong with the InCHlib server.\n".format(url))

        with open(os.path.join(htmldir, "inchlib.html"), "w") as output:
            output.write(template)

    def add_metadata_from_file(self, metadata_file, delimiter, header=True, metadata_compressed_value="median"):
        """Adds metadata from csv file.
        Metadata_compressed_value specifies the resulted value when the data are compressed (median/mean/frequency)"""
        self.metadata_compressed_value = metadata_compressed_value
        self.metadata, self.metadata_header = self.__read_metadata_file__(metadata_file, delimiter, header)
        self.__connect_metadata_to_data__()

    def add_metadata(self, metadata, header=True, metadata_compressed_value="median"):
        """Adds metadata in a form of list of lists (tuples).
        Metadata_compressed_value specifies the resulted value when the data are compressed (median/mean/frequency)"""
        self.metadata_compressed_value = metadata_compressed_value
        self.metadata, self.metadata_header = self.__read_metadata__(metadata, header)
        self.__connect_metadata_to_data__()

    def __connect_metadata_to_data__(self):
        print("Adding metadata: {} rows".format(len(self.metadata)))
        self.dendrogram["metadata"] = {}

        if self.metadata_header:
            self.dendrogram["metadata"]["feature_names"] = self.metadata_header

        self.dendrogram["metadata"]["nodes"] = self.__connect_additional_data_to_data__(self.metadata, self.metadata_compressed_value)

    
    #we doesn't need this as we doesnt use metadata
    def __read_metadata__(self, metadata, header):
        metadata_header = []
        rows = metadata
        metadata = {}
        data_start = 0

        if header:
            metadata_header = rows[0][1:]
            data_start = 1
        
        for row in rows[data_start:]:
            metadata[str(row[0])] = [r for r in row[1:]]

        return metadata, metadata_header

    
    #we aren't even using metadata_file in our case
    # this function is using metadata file and merging that with the previous file
    def __read_metadata_file__(self, metadata_file, delimiter, header):
        csv_reader = csv.reader(open(metadata_file, "r"), delimiter=delimiter)
        metadata_header = []
        rows = [row for row in csv_reader]
        metadata = {}
        data_start = 0

        if header:
            metadata_header = rows[0][1:]
            data_start = 1
        
        for row in rows[data_start:]:
            metadata_id = str(row[0])
            metadata[metadata_id] = [r for r in row[1:]]

        return metadata, metadata_header

    def add_column_metadata(self, column_metadata, header=True):
        """Adds column metadata in a form of list of lists (tuples). Column metadata doesn't have header row, first item in each row is used as label instead"""
        if header:
            self.column_metadata = [r[1:] for r in column_metadata]
            self.column_metadata_header = [r[0] for r in column_metadata]
        else:
            self.column_metadata = [r for r in column_metadata]
            self.column_metadata_header = False

        self.__check_column_metadata_length__()
        self.__add_column_metadata_to_data__()

    def add_column_metadata_from_file(self, column_metadata_file, delimiter=",", header=True):
        """Adds column metadata from csv file. Column metadata doesn't have header."""
        csv_reader = csv.reader(open(column_metadata_file, "r"), delimiter=delimiter)
        column_metadata = [row for row in csv_reader]
        self.add_column_metadata(column_metadata, header)

    def __check_column_metadata_length__(self):
        features_length = len(self.data[0])
        for row in self.column_metadata:
            if features_length != len(row):
                raise Exception("Column metadata length and features length must be the same.")

    def __add_column_metadata_to_data__(self):
        if self.cluster_object.clustering_axis == "both":
            self.column_data = self.cluster_object.__reorder_data__(self.column_metadata, self.cluster_object.data_order)
        self.dendrogram["column_metadata"] = {"features":self.column_metadata}
        if self.column_metadata_header:
            self.dendrogram["column_metadata"]["feature_names"] = self.column_metadata_header

   #adding the alternative data to input data file we are not even using this 
    def add_alternative_data_from_file(self, alternative_data_file, delimiter, header, alternative_data_compressed_value):
        """Adds alternative_data from csv file."""
        self.alternative_data_compressed_value = alternative_data_compressed_value
        self.add_alternative_data(self.__read_alternative_data_file__(alternative_data_file, delimiter), header, alternative_data_compressed_value)

    #we are not usding alternative data so this method is also not needed
    def add_alternative_data(self, alternative_data, header, alternative_data_compressed_value):
        """Adds alternative data in a form of list of lists (tuples)."""
        self.alternative_data_compressed_value = alternative_data_compressed_value

        if self.cluster_object.clustering_axis == "both":
            alternative_data = self.__reorder_alternative_data__(alternative_data)

        self.dendrogram["alternative_data"] = {}
        self.alternative_data_header = False
        
        if header:
            self.alternative_data_header = alternative_data[0][1:]
            self.dendrogram["alternative_data"]["feature_names"] = self.alternative_data_header
            alternative_data = alternative_data[1:]

        self.alternative_data = self.__read_alternative_data__(alternative_data)

        print("Adding alternative data: {} rows".format(len(self.alternative_data)))
        self.dendrogram["alternative_data"]["nodes"] = self.__connect_additional_data_to_data__(self.alternative_data, self.alternative_data_compressed_value)

    def __reorder_alternative_data__(self, alternative_data):
        alt_data_without_id = [r[1:] for r in alternative_data]
        reordered_data = self.cluster_object.__reorder_data__(alt_data_without_id, self.cluster_object.data_order)
        rows = []
        for i, r in enumerate(alternative_data):
            row = [r[0]]
            row.extend(reordered_data[i])
            rows.append(row)
        return rows

    def __read_alternative_data_file__(self, alternative_data_file, delimiter):
        csv_reader = csv.reader(open(alternative_data_file, "r"), delimiter=delimiter)
        return [r for r in csv_reader]

    def __read_alternative_data__(self, alternative_data):
        return {str(r[0]):r[1:] for r in alternative_data}

	
    # we are not connecting the additional data to the given data so this function is generally not required
    def __connect_additional_data_to_data__(self, additional_data, compressed_value):
        if len(set(additional_data.keys()) & set(self.data_names)) == 0:
            print("No data objects correspond with the clustered data according to their IDs. No additional data added.")
            return

        if not self.dendrogram:
            raise Exception("You must create dendrogram before adding data to it.")

        node2additional_data = {}

        leaves = {n:node for n, node in self.dendrogram["data"]["nodes"].items() if node["count"] == 1}

        if not self.compress:
            for leaf_id, leaf in leaves.items():
                try:
                    node2additional_data[leaf_id] = additional_data[leaf["objects"][0]]
                except Exception, e:
                    continue
        else:
            compressed_value2fnc = {
                "median": lambda values: round(numpy.median(col), 3),
                "mean": lambda values: round(numpy.average(col), 3),
                "frequency": lambda values: self.__get_most_frequent__(col)
            }

            for leaf in leaves:
                objects = []
                for item in leaves[leaf]["objects"]:
                    try:
                        objects.append(additional_data[item])
                    except Exception, e:
                        continue

                cols = zip(*objects)
                row = []
                cols = [list(c) for c in cols]

                for col in cols:
                    if compressed_value in compressed_value2fnc:
                        try:
                            col = [float(c) for c in col]
                            value = compressed_value2fnc[compressed_value](col)
                        except ValueError:
                            value = compressed_value2fnc["frequency"](col)
                    
                    else:
                        raise Exception("Unkown type of metadata_compressed_value: {}. Possible values are: median, mean, frequency.".format(self.metadata_compressed_value))
        
                    row.append(value)

                node2additional_data[leaf] = row

        return node2additional_data

    def __get_most_frequent__(self, col):
        freq2val = {col.count(v):v for v in set(col)}
        value = freq2val[max(freq2val.keys())]
        return value

class Cluster():
    """Class for data clustering"""
	
    def __init__(self):
        self.write_original = False

    #reading the input file in csv format
    def read_csv(self, filename, delimiter=",", header=False, missing_value=False, datatype="numeric"):
        """Reads data from the CSV file"""
        self.filename = filename
        csv_reader = csv.reader(open(self.filename, "r"), delimiter=delimiter)
        rows = [row for row in csv_reader]
        row_mat = [[]]
        col_mat = [[]]
        self.read_data(row_mat, col_mat, rows, header, missing_value, datatype, False)

    ############################################3
    #self implemented function for filtering
    def read_csv_2(self,  row_matrix, col_matrix, filename, delimiter = ",", header = False, missing_value = False, datatype = "numeric") :
        table = list(csv.reader(open(filename, "rb"), delimiter = ','))
        csv_reader = csv.reader(open(self.filename, "r"), delimiter=delimiter)
        rows = [row for row in csv_reader]
        #print("*****************going to read data*********************")
        self.read_data(row_matrix, col_matrix, rows, header,  missing_value, datatype, True)
        
        

        
         
            
    #fucntion to apply operations
    def check(self, a, op, b):
        if op == 0 :
            if a > b :
                return True
        elif op == 1 :
            if a < b :
                return True
        elif op == 2 :
            if a >= b:
                return True
        else :
            if a <= b :
                return True
        return False

    #this module store file in the form of list and also seperate the header and node id from the table
    def read_data(self, row_matrix, col_matrix ,rows, header=False, missing_value=False, datatype="numeric", flag = False):
        """Reads data in a form of list of lists (tuples)"""
        #dictonary to filter data
        #print("value _flag", flag)
        avail_operations = {0 : '>', 1 :'<' , 2:'>=' , 3:'<='}; #dictonary holding the values and operations d
        self.datatype = datatype
        self.missing_value = missing_value
        #header for dendrogram
        self.header = header
        #self.header.insert(0, row[])
        data_start = 0
	   
	    #reading the column header for ex.. dw in our example
	    #data = row wise data
        #change rows[0][1:] to row[0][0:]
        if self.header:
            self.header = rows[0][1:] #from column no 1 to the no of columns in the row
            self.header.insert(0, rows[0][0])
            data_start = 1 #start reading values from table from row no 1

        #condition implemented to get filtered data on input file : to show on dendrogram
        if flag == True:
            self.data_names = [] #1d matrix for storing iteams names
            self.data = [] #2d matrix for storing data coloumns
            print("*****************self_data**********************")

            f = 0
            for i in range(1, len(rows)):
                #print("row ", len(row_matrix))
                for j in range (0, len(row_matrix)) :
                   # check for conditions by check fucntion
                    if self.check( float(rows[i][ int(row_matrix[j][0]) ] ) , int(row_matrix[j][1]), float(row_matrix[j][2]) ) :
                        f = 1
                    else :
                        f = 0;
                        break
                if f == 1:
                    self.data_names.append(str(rows[i][0]))
                    self.data.append(rows[i][1:])

            #print (self.data)
            #self.data_names = [str(rows[0][i]) for row in (rows[data_start:])] #contains the first column of the table
	        #print(self.data_names)
            #print("************************************ ",self.data_names)
#######################################################################3
            #if flag == 1 : # give values to table only when it is called after filtering
            #change row[1:] to row[0:]
            #self.data = [row[1:] for row in rows[data_start:]] #row data from table from 1 to no if columns in table. ex - [[1], [32]]
	        #print(self.data)
            self.original_data = copy.deepcopy(self.data)

            if not self.missing_value is False:
                self.data, self.missing_values_indexes = self.__impute_missing_values__(self.data)
                self.original_data = self.__return_missing_values__(copy.deepcopy(self.data), self.missing_values_indexes)

                self.original_data = [[float(val) if not val is None else None for val in r] for r in self.original_data]
                self.data = [[float(val) if not val is None else None for val in r] for r in self.data]
                #print (self.data)

#######################################################################################
  
#########################################################################################
      
    #this method will tackle with the missing values in data
    def __impute_missing_values__(self, data):
        datatype2impute = {"numeric": {"strategy":"mean", 
                                        "value": lambda x: round(float(value), 3)}, 
                           "binary": {"strategy":"most_frequent", 
                                      "value": lambda x: int(value)}
                           }

        if not self.datatype in DISTANCES:
            raise Exception("".join(["You can choose only from data types: ", ", ".join(DISTANCES.keys())]))

        missing_values_indexes = []
        
        for i, row in enumerate(self.data):
            missing_values_indexes.append([j for j, v in enumerate(row) if v == self.missing_value])

            for j, value in enumerate(row):
                if value == self.missing_value:
                    data[i][j] = numpy.nan
        imputer = preprocessing.Imputer(missing_values="NaN", strategy=datatype2impute[self.datatype]["strategy"])
        #error when using median strategy - minus one dimension in imputed data... omg
        imputed_data = [list(row) for row in imputer.fit_transform(self.data)]
        imputed_data = [[datatype2impute[self.datatype]["value"](value) for value in row] for row in imputed_data]
        return imputed_data, missing_values_indexes
        

   # this method tackles with the the normalization of data and defualt value is btwn 0 and 1 if not given during call
    def normalize_data(self, feature_range=(0,1), write_original=False):
        """Normalizes data to a scale either from 0 to 1 or from range provided. When write_original is set to True, 
        the normalized data will be clustered, but original data will be written to the heatmap."""
        self.write_original = write_original
	#fitting the data into scaler tranform for normalization
        min_max_scaler = preprocessing.MinMaxScaler(feature_range)
        self.data = min_max_scaler.fit_transform(self.data)
        self.data = [[round(v, 3) for v in row] for row in self.data]
    

    #############################################################################
    #self implemented fucntion
    #function which takes unfilterd yules file and return filtered yules file
    def filter_yules(self, result_unfiltered,_dict):
        result_filter = [] #2d matrix to hold filtered data
        print ("inside function")

        n = len(result_unfiltered)
        print("*************** ", n)
        for i in range(0,n):
            #print (result_unfiltered[i][0])
            if(_dict.has_key(result_unfiltered[i][0])):
                temp = []
                for j in range(0, n):
                    if(_dict.has_key(result_unfiltered[0][j])):
                        temp.append(result_unfiltered[i][j])
                result_filter.append(temp)
        #print ("***********result_filter***********")
        #print (result_filter)
        return result_filter

   # this function is responsible for clustering the data which has been read by csv file with defualt clustering by euclideanand axis along the row and linkage through ward
    def cluster_data(self,iteam_names, filename, row_distance="euclidean", row_linkage="single", axis="row", column_distance="euclidean", column_linkage="ward"):
        """Performs clustering according to the given parameters.
        @datatype - numeric/binary
        @row_distance/column_distance - see. DISTANCES variable
        @row_linkage/column_linkage - see. LINKAGES variable
        @axis - row/both
        """
        ###############################################################################3
        _dict= {}; #dictonary which will tell the about the ids present in the new_file

        for iteam in iteam_names :
            temp_dict = {iteam :True};
            _dict.update(temp_dict)
        print("Clustering rows:", row_distance, row_linkage, column_linkage)

	#clustering axis can be slected along rows or coloumns or along both i.e, how we want to do clustering along rows or coloumns acco to data in ur case clustering along row has to be done
        self.clustering_axis = axis
        row_linkage = str(row_linkage)
        
	#in case of row linkage we make matric acco to row.
        ############################################################################################
        # here it is making a matric therefore here we can edit the code according to yules matrix
	############################################################################################
        if row_linkage in RAW_LINKAGES:
            self.clustering = fastcluster.linkage(self.data, method=row_linkage, metric=row_distance)

        else:
	    #print ("self_data ->", self.data)
	    #print ("row_distance =>", row_distance)
            #data = numpy.array(self.data)
            
            self.distance_vector = []
            
            ########################################
            #open and read file in coloumn wise manner
            #dummy = []
            import numpy;
            ######################################
            result_unfiltered = list(csv.reader(open(filename,"rb"),delimiter=',')) #unfiltered yules
            temp = {result_unfiltered[0][0]:True};
            _dict.update(temp) #adding first element of the unfiltered data to dictonary
            ######################################
            result_filter = self.filter_yules(result_unfiltered,_dict) #filtered yules
            #print ("22**************result_filter*******************")
            print (len(result_filter),"   len len  ", len(result_filter[0]))

            #print ("result is file:-",result)
            matrix_len = len(result_filter) - 2
            loop_len = matrix_len*(2 + (matrix_len - 1)) / 2 #sum formula = n*(2*a + (n - 1) * d ) / 2
            print("loop_len ", loop_len)
            i = 2  
            j = 1
            count = 1
            for loop in range (0, loop_len) :
                if result_filter[i][j] == '' or result_filter[i][j] == '#' or result_filter[i][j] == ' ': 
                    self.distance_vector.append(float('0.00'))
                else:
                    self.distance_vector.append(float(result_filter[i][j]))
                i = i + 1
                if i > matrix_len :
                    j = j + 1
                    count = count + 1
                    i = count
            print("dummy ->>> ***********************************")
            #print (dummy)
            '''import csv;
            with open (filename, 'rb') as f:
                reader = csv.reader(f, delimiter = ';') 
                for row in reader():
                    print("column_val -> ", row[0])
                i = i + 1'''
            
            for i in range(0, len(self.distance_vector) ) :
                self.distance_vector[i] = (1.00 - self.distance_vector[i] )
            #import pdb;pdb.set_trace()          

            if self.datatype == "numeric" and not row_distance in DISTANCES[self.datatype]:
                raise Exception("".join(["When clustering numeric data you must choose from these distance measures: ", ", ".join(DISTANCES[self.datatype])]))
            elif (self.datatype == "binary" or self.datatype == "nominal") and not row_distance in DISTANCES[self.datatype]:
                raise Exception("".join(["When clustering binary or nominal data you must choose from these distance measures: ", ", ".join(DISTANCES[self.datatype])]))
            #import pdb;pdb.set_trace()
            self.clustering = fastcluster.linkage(self.distance_vector, method=str(row_linkage))

        if not self.missing_value is False:
            self.data = self.__return_missing_values__(self.data, self.missing_values_indexes)
        self.column_clustering = []

        if axis == "both" and len(self.data[0]) > 2:
            print("Clustering columns:", column_distance, column_linkage)
            self.__cluster_columns__(column_distance, column_linkage)
        
        if self.write_original or self.datatype == "nominal":
            self.data = self.original_data

    def __return_missing_values__(self, data, missing_values_indexes):
        for i, indexes in enumerate(missing_values_indexes):
            if indexes:
                for index in indexes:
                    data[i][index] = None
	
        return data

  
   #for clustering along the coloumns 
    def __cluster_columns__(self, column_distance, column_linkage):
        self.data = [list(col) for col in zip(*self.data)]
        if not self.missing_value is False:
            self.data, missing_values_indexes = self.__impute_missing_values__(self.data)
        

        self.column_clustering = fastcluster.linkage(self.data, method=column_linkage, metric=column_distance)
        self.data_order = hcluster.leaves_list(self.column_clustering)

        if not self.missing_value is False:
            self.data = self.__return_missing_values__(self.data, missing_values_indexes)
        
        self.data = zip(*self.data)
        self.data = self.__reorder_data__(self.data, self.data_order)
        self.original_data = self.__reorder_data__(self.original_data, self.data_order)
        if self.header:
            self.header = self.__reorder_data__([self.header], self.data_order)[0]

    def __reorder_data__(self, data, order):
        for i in xrange(len(data)):
            reordered_data = []
            for j in order:
                reordered_data.append(data[i][j])
            reordered_data.reverse()
            data[i] = reordered_data

        return data

#python file for clustering and making dandogram / can also be intiated by the script
def _process_(arguments):
    c = Cluster()
    c.read_csv(arguments.data_file, arguments.data_delimiter, arguments.data_header, arguments.missing_values, arguments.datatype)
    
    if arguments.normalize:
        c.normalize_data(feature_range=(0,1), write_original=arguments.write_original)

    c.cluster_data(row_distance=arguments.row_distance, row_linkage=arguments.row_linkage, axis=arguments.axis, column_distance=arguments.column_distance, column_linkage=arguments.column_linkage)

    d = Dendrogram(c)
    d.create_cluster_heatmap(compress=arguments.compress, compressed_value=arguments.compressed_value, write_data=not arguments.dont_write_data)
    
    if arguments.metadata:
        d.add_metadata_from_file(metadata_file=arguments.metadata, delimiter=arguments.metadata_delimiter, header=arguments.metadata_header, metadata_compressed_value=arguments.metadata_compressed_value)
    
    if arguments.column_metadata:
        d.add_column_metadata_from_file(column_metadata_file=arguments.column_metadata, delimiter=arguments.column_metadata_delimiter, header=arguments.column_metadata_header)

    if arguments.alternative_data:
        d.add_alternative_data_from_file(alternative_data_file=arguments.alternative_data, delimiter=arguments.alternative_data_delimiter, header=arguments.alternative_data_header, alternative_data_compressed_value=arguments.alternative_data_compressed_value)
    
    if arguments.output_file or arguments.html_dir:
        if arguments.output_file:
            d.export_cluster_heatmap_as_json(arguments.output_file)
        else:
            d.export_cluster_heatmap_as_html(arguments.html_dir)
    else:
        print(json.dumps(d.dendrogram, indent=4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("data_file", type=str, help="csv(text) data file with delimited values")
    parser.add_argument("-o", "--output_file", type=str, help="the name of output file")
    parser.add_argument("-html", "--html_dir", type=str, help="the directory to store HTML page with dependencies")
    parser.add_argument("-rd", "--row_distance", type=str, default="euclidean", help="set the distance to use for clustering rows")
    parser.add_argument("-rl", "--row_linkage", type=str, default="ward", help="set the linkage to use for clustering rows")
    parser.add_argument("-cd", "--column_distance", type=str, default="euclidean", help="set the distance to use for clustering columns (only when clustering by both axis -a parameter)")
    parser.add_argument("-cl", "--column_linkage", type=str, default="ward", help="set the linkage to use for clustering columns (only when clustering by both axis -a parameter)")
    parser.add_argument("-a", "--axis", type=str, default="row", help="define clustering axis (row/both)")
    parser.add_argument("-dt", "--datatype", type=str, default="numeric", help="specify the type of the data (numeric/binary)")
    parser.add_argument("-dd", "--data_delimiter", type=str, default=",", help="delimiter of values in data file")
    parser.add_argument("-m", "--metadata", type=str, default=None, help="csv(text) metadata file with delimited values")
    parser.add_argument("-md", "--metadata_delimiter", type=str, default=",", help="delimiter of values in metadata file")
    parser.add_argument("-dh", "--data_header", default=False, help="whether the first row of data file is a header", action="store_true")
    parser.add_argument("-mh", "--metadata_header", default=False, help="whether the first row of metadata file is a header", action="store_true")
    parser.add_argument("-c", "--compress", type=int, default=0, help="compress the data to contain maximum of specified count of rows")
    parser.add_argument("-cv", "--compressed_value", type=str, default="median", help="the resulted value from merged rows when the data are compressed (median/mean/frequency)")
    parser.add_argument("-mcv", "--metadata_compressed_value", type=str, default="median", help="the resulted value from merged rows of metadata when the data are compressed (median/mean/frequency)")
    parser.add_argument("-dwd", "--dont_write_data", default=False, help="don't write clustered data to the inchlib data format", action="store_true")
    parser.add_argument("-n", "--normalize", default=False, help="normalize data to [0, 1] range", action="store_true")
    parser.add_argument("-wo", "--write_original", default=False, help="cluster normalized data but write the original ones to the heatmap", action="store_true")
    parser.add_argument("-cm", "--column_metadata", type=str, default=None, help="csv(text) metadata file with delimited values without header")
    parser.add_argument("-cmd", "--column_metadata_delimiter", type=str, default=",", help="delimiter of values in column metadata file")
    parser.add_argument("-cmh", "--column_metadata_header", default=False, help="whether the first column of the column metadata is the row label ('header')", action="store_true")
    parser.add_argument("-mv", "--missing_values", type=str, default=False, help="define the string representating missing values in the data")
    parser.add_argument("-ad", "--alternative_data", type=str, default=None, help="csv(text) alternative data file with delimited values")
    parser.add_argument("-adh", "--alternative_data_header", default=False, help="whether the first row of alternative data file is a header", action="store_true")
    parser.add_argument("-add", "--alternative_data_delimiter", type=str, default=",", help="delimiter of values in alternative data file")
    parser.add_argument("-adcv", "--alternative_data_compressed_value", type=str, default="median", help="the resulted value from merged rows of alternative data when the data are compressed (median/mean/frequency)")
    
    args = parser.parse_args()
    _process_(args)
    
