# pyGTK --- --- --- --- --- --- --- --- ---
import pygtk
pygtk.require('2.0')
import gtk
# ElementTree - --- --- --- --- --- --- ---
import xml.etree.ElementTree as ET
# --- --- --- --- --- --- --- --- --- --- --- --- 
import sys
# --- --- --- --- --- --- --- --- --- --- --- --- 

xml_2_ns = {
	'http://www.s3.org/XML/1998/namespace' : 'xml',
	}

ns_2_xml = {
	'xml' : 'http://www.s3.org/XML/1998/namespace',
}
	
def extend_tree(treestore, element, parent_node, ns_list):
	'''
	'''

	node_label = '%s' % strip_ns_from_str(element.tag, ns_list)
	
	# if element.text != None:
		# text = element.text.strip()
		# if (len(text) > 0):
			# node_label = '%s' % (strip_ns_from_str(element.tag, ns_list))   
	
	node = treestore.append(parent_node, [node_label])  

	# add attribute name/val pairs to node
	for name, value in element.items():
		name = strip_ns_from_str(name, ns_list)
		value = strip_ns_from_str(value, ns_list)
		label = '%s = %s' % (name, value)
		treestore.append(node, [label])
	 
	if element.text != None:
		if len(element.text.strip()) > 0:
			discard = treestore.append(node, [strip_ns_from_str(element.text, ns_list)])  
	
	# recurse over children
	for child_element in element.getchildren():
		child_node = extend_tree(treestore, child_element, node, ns_list)      

	return node
		
def etree_to_gtk_treestore(tree):
	'''
	construct gtk.TreeStore(str) from ElementTree
	'''
	
	ns_list = ns_list_from_tree(tree)
	
	root_e = tree.getroot()
		
	treestore = gtk.TreeStore(str)
	root_label = '%s' % strip_ns_from_str(root_e.tag, ns_list)
	root_node = treestore.append(None, [root_label])  
	
	for child_e in root_e.getchildren():
		extend_tree(treestore, child_e, root_node, ns_list)  
		
	 # add attribute name/val pairs to node
	for name, value in root_e.items():
		name = strip_ns_from_str(name, ns_list)
		value = strip_ns_from_str(value, ns_list)    
		label = '%s = %s' % (name, value)
		treestore.append(None, [label])
	
	# if ns is global
	for ns in ns_list:
		label = 'xmlns : %s' % ns
		treestore.append(None, [label])
	
	return treestore 

def ns_from_string(s):
	left = s.find('{')
	right = s.find('}')
	ns = s[left+1:right]      
	return ns

def process_potential_ns_string(s, ns_list):

	if s == None:
		return

	if (s.find('{') != -1) and (s.find('}') != -1):
		ns = ns_from_string(s)
		if (ns not in ns_list):
			ns_list.append(ns)
 
def ns_list_from_element(el, ns_list):

	# tag
	process_potential_ns_string(el.tag, ns_list)
	# text
	process_potential_ns_string(el.text, ns_list)  
	
	# attributes
	for name, value in el.items():
		process_potential_ns_string(name, ns_list)
		process_potential_ns_string(value, ns_list)
	
	for child_el in el.getchildren():
		ns_list_from_element(child_el, ns_list)    
	
	return ns_list
	
def ns_list_from_tree(etree):
	'''
	'''  
	ns_list = []  
	root_e = etree.getroot()    
	
	# tag
	process_potential_ns_string(root_e.tag, ns_list)
	# text
	process_potential_ns_string(root_e.text, ns_list)  
	
	# attributes
	for name, value in root_e.items():
		process_potential_ns_string(name, ns_list)
		process_potential_ns_string(value, ns_list)
	
	# child elements
	for child_el in root_e.getchildren():
		ns_list_from_element(child_el, ns_list)

	return ns_list
	
def strip_ns_from_str(s, ns_list):
	stripped = str(s)
	for ns in ns_list:
		token = '{%s}' % ns
		loc = stripped.find(token)
		if (loc != -1):
			stripped = stripped[:loc] + stripped[loc + len(token):len(stripped)]
			
	return stripped
	
class XMLTreeView:
	'''
	'''
	def delete_event(self, widget, event=None, data=None):
		'''
		'''
		gtk.main_quit()
		return False
		
	def __init__(self, path, title='pyxtree - XML tree viewer - python2 gtk', xsize=900, ysize = 500):
		'''
		'''  
		self.window = gtk.Dialog()
		self.window.connect("destroy", self.delete_event)		
		self.window.set_border_width(0)		    
		
		self.swin_tree = gtk.ScrolledWindow()
		self.swin_tree.set_border_width(10)
		self.swin_tree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		self.window.vbox.pack_start(self.swin_tree, True, True, 0)
		
		self.swin_text = gtk.ScrolledWindow()
		self.swin_text.set_border_width(10)
		self.swin_text.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		self.window.vbox.pack_start(self.swin_text, True, True, 0)    
		
		self.window.set_title(title)
		self.window.set_size_request(xsize, ysize)
		self.window.connect("delete_event", self.delete_event)

		etree = ET.parse(path)    
		self.treestore = etree_to_gtk_treestore(etree) 

		# create the TreeView using treestore
		self.treeview = gtk.TreeView(self.treestore)
		self.tvcolumn = gtk.TreeViewColumn(path)
		self.treeview.append_column(self.tvcolumn)
		self.cell = gtk.CellRendererText()
		# add the cell to the tvcolumn and allow it to expand
		self.tvcolumn.pack_start(self.cell, True)
		# set the cell "text" attribute to column 0 - retrieve text
		# from that column in treestore
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
		# make it searchable
		self.treeview.set_search_column(0)
		# Allow sorting on the column
		#self.tvcolumn.set_sort_column_id(0)
		# Allow drag and drop reordering of rows
		#self.treeview.set_reorderable(True)
		
		self.swin_tree.add_with_viewport(self.treeview)    
		self.swin_tree.show()
		
		xfile = open(path, 'r')
		xtext = xfile.read()
		xfile.close()
		
		label = gtk.Label(xtext)
		
		# ns_list = ns_list_from_tree(etree)
		
		# ns_str = ''
		# for ns in ns_list:
			# ns_str = ns_str + str(ns) + '\n'    
		
		# label = gtk.Label(ns_str)

		label.set_alignment(xalign=0, yalign=0.5) 
		
		self.swin_text.add_with_viewport(label)    
		self.swin_text.show()    
		
		self.window.show_all()

def main(path = None):  
	'''
	'''
	if path != None:
		tree_view = XMLTreeView(path)	
		gtk.main()	

# ------------------------------------

from optparse import OptionParser

def src_file_from_cmd_args():
	'''
	'''
	parser = OptionParser('python2 pygtk xml tree viewer')
	parser.add_option("-f", "--file", dest="filename",
	                  help="xml file", metavar="FILE")
	(options, args) = parser.parse_args()

	return options.filename

if __name__ == "__main__":
	file_path = src_file_from_cmd_args()
	if file_path != None:
		main(path=file_path)
	else:
		main()
