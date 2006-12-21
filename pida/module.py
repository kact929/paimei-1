#
# PIDA Module
# Copyright (C) 2006 Pedram Amini <pedram.amini@gmail.com>
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

'''
@author:       Pedram Amini, Cameron Hotchkies
@license:      GNU General Public License 2.0 or later
@contact:      pedram.amini@gmail.com
@organization: www.openrce.org
'''

import sys
import pgraph

from sql_singleton import *

from function import *
from defines  import *


class module (pgraph.graph):
    '''
    '''

    # most of these should be read via properties
    __name          = None
    __base          = None
    __signature     = None
    
    __nodes         = None
    
    dbid            = None      # Database ID
    database_file   = None
    
    __cached        = False
    ext             = {}    
    ####################################################################################################################
    def __init__ (self, database_file, database_id=1):
        '''
        Analysis of an IDA database requires the instantiation of this class and will handle, depending on the requested
        depth, the analysis of all functions, basic blocks, instructions and more specifically which analysis techniques
        to apply. For the full list of ananylsis options see defines.py. Specifying ANALYSIS_IMPORTS will require an
        extra one-time scan through the entire structure to propogate functions (nodes) and cross references (edges) for
        each reference API call. Specifying ANALYSIS_RPC will require an extra one-time scan through the entire IDA
        database and will propogate additional function level attributes.

        The signature attribute was added for use in the PaiMei process stalker module, for ensuring that a loaded
        DLL is equivalent to the PIDA file with matching name. Setting breakpoints in a non-matching module is
        obviously no good.

        @see: defines.py

        @type  name:      String
        @param name:      (Optional) Module name
        @type  signature: String
        @param signature: (Optional) Unique file signature to associate with module
        @type  depth:     Integer
        @param depth:     (Optional, Def=DEPTH_FULL) How deep to analyze the module
        @type  analysis:  Integer
        @param analysis:  (Optional, Def=ANALYSIS_NONE) Which extra analysis options to enable
        '''

        # run the parent classes initialization routine first.
        # this will need to be fixed
        #super(module, self).__init__(name)

        ss = sql_singleton()
        ss.connection(database_file)
        

        self.dbid = database_id
        self.database_file = database_file
 
    ####################################################################################################################
    
    def load_from_sql(self):
        '''
	Loads the information about a module from a SQL datastore. (Assumption of MySQL as backend)

	@type  host: String
	@param host: the hostname of the SQL datastore

	@type  username: String
	@param username: The username for authenticating to the SQL datastore

	@type  password: String
	@param password: The password for authenticating to the SQL datastore
	'''
        
        ss = sql_singleton()
        ss.connection(self.db_filename)
        sql = ss.LOAD_MODULE % (self.dbid)        
         
        cr = ss.cursor()
        
        results = cr.execute(sql).fetchone()
        
        self.name = results["name"]
        
        self.__cached = True
	
    ####################################################################################################################
    # name accessors
    
    def getName (self):
        '''
        The name of the module.
        
        @rtype:  String
        @return: The name of the module
        '''
        
        if not self.__cached:
            self.load_from_sql()
            
        return self.__name
        
    ####
      
    def setName (self, value):
        '''
        Sets the name of the module.
        
        @type  value: String
        @param value: The name of the module.
        '''
        
        if self.__cached:
            self.__name = value
            
        ss = sql_singleton()                        
        
        ss.cursor().execute("UPDATE module SET name='%s' where id=%d" % (value, self.dbid))
        ss.connection().commit()
        
    ####
        
    def deleteName (self):
        '''
        destructs the name of the module
        '''
        del self.__name 
            
    ####################################################################################################################
    # base accessors
        
    def getBase (self):
        '''
        Gets the base address of the module
        
        @rtype:  Dword
        @return: The base address of the module
        '''
        
        if not self.__cached:
            self.load_from_sql()
            
        return self.__base        
        
    def setBase (self, value):
        '''
        Sets the base address of the module.
        
        @type  value: Dword
        @param value: The base address of the module.
        '''
        
        if self.__cached:
            self.__base = value
        
        ss = sql_singleton()                        
        
        ss.cursor().execute("UPDATE module SET base=%d where id=%d" % (value, self.dbid))
        ss.connection().commit()
        
    def deleteBase (self):
        '''
        destructs the base address of the module
        '''
        del self.__base 
            
    ####################################################################################################################
    # signature accessors
        
    def getSignature (self):
        '''
        Gets the signature of the module
        
        @rtype:  String
        @return: The signature of the module
        '''
        
        if not self.__cached:
            self.load_from_sql()
            
        return self.__signature
        
    def setSignature (self, value):
        '''
        Sets the signature of the module.
        
        @type  value: String
        @param value: The signature of the module.
        '''
        
        if self.__cached:
            self.__signature = value
            
        ss = sql_singleton()
        ss.cursor().execute("UPDATE module SET signature='%s' where id=%d" % (value, self.dbid))
        ss.connection().commit()
        
    def deleteSignature (self):
        '''
        destructs the signature of the module
        '''
        del self.__signature
    
    ####################################################################################################################
    # num_functions
    
    def getNumFunctions (self):
        '''
        The number of instructions in the function
        
        @rtype:  Integer
        @return: The number of instructions in the function
        '''
        
        ss = sql_singleton()
        cr = ss.cursor()
        sql = "SELECT count(*) FROM function WHERE module = %d;" % self.dbid
        cr.execute(sql)
        
        try:
            ret_val = cr.fetchone()[0]
        except:
            ret_val = 0
            
        return ret_val
        
    ####
    
    def setNumFunctions (self, value):
        '''
        Sets the number of instructions (raises an exception - READ ONLY)
        
        @type  value: Integer
        @param value: The number of instructions in the function
        '''
        raise TypeError, "num_instructions is a read-only property"
        return -1
    
    ####
        
    def deleteNumFunctions (self):
        '''
        destructs the num_instructions
        '''
        pass # dynamically generated property value
        
    ####################################################################################################################
    # nodes accessors
        
    def getNodes (self):
        '''
        Gets the signature of the module
        
        @rtype:  String
        @return: The signature of the module
        '''
        
        if self.__nodes == None:
            ret_val = {}
            ss = sql_singleton()
            
            cursor = ss.connection(self.database_file).cursor()
            
            results = cursor.execute("SELECT id FROM function WHERE module = %d" % self.dbid).fetchall()
             
            for function_id in results:
                new_function = function(function_id, self.database_file)
                ret_val[new_function.ea_start] = new_function
                
            self.__nodes = ret_val
            
        return self.__nodes
        
    def setNodes (self, value):
        '''
        Sets the nodes of the module. This will generate an error.
        
        @type  value: String
        @param value: The signature of the module.
        '''
        
        raise TypeError, "nodes and functions are not directly writable for modules. This is a read-only property"
        
    def deleteNodes (self):
        '''
        destructs the signature of the module
        '''
        del self.__nodes
            
    ####################################################################################################################
    def find_function (self, ea):
        '''
        Locate and return the function that contains the specified address.

        @type  ea: DWORD
        @param ea: An address within the function to find

        @rtype:  pida.function
        @return: The function that contains the given address or None if not found.
        '''

        for func in self.nodes.values():
            # this check is necessary when analysis_depth == DEPTH_FUNCTIONS
            if func.ea_start == ea:
                return func

            for bb in func.nodes.values():
                if bb.ea_start <= ea <= bb.ea_end:
                    return func

        return None


    ####################################################################################################################
    def next_ea (self, ea=None):
        '''
        Return the instruction after to the one at ea. You can call this routine without an argument after the first
        call. The overall structure of PIDA was not really designed for this kind of functionality, so this is kind of
        a hack.

        @todo: See if I can do this better.

        @type  ea: (Optional, def=Last EA) Dword
        @param ea: Address of instruction to return next instruction from or -1 if not found.
        '''

        if not ea and self.current_ea:
            ea = self.current_ea

        function = self.find_function(ea)

        if not function:
            return -1

        ea_list = []

        for bb in function.nodes.values():
            ea_list.extend(bb.instructions.keys())

        ea_list.sort()

        try:
            idx = ea_list.index(ea)

            if idx == len(ea_list) - 1:
                raise Exception
        except:
            return -1

        self.current_ea = ea_list[idx + 1]
        return self.current_ea


    ####################################################################################################################
    def prev_ea (self, ea=None):
        '''
        Within the function that contains ea, return the instruction prior to the one at ea. You can call this routine
        without an argument after the first call. The overall structure of PIDA was not really designed for this kind of
        functionality, so this is kind of a hack.

        @todo: See if I can do this better.

        @type  ea: (Optional, def=Last EA) Dword
        @param ea: Address of instruction to return previous instruction to or None if not found.
        '''

        if not ea and self.current_ea:
            ea = self.current_ea

        function = self.find_function(ea)

        if not function:
            return -1

        ea_list = []

        for bb in function.nodes.values():
            ea_list.extend(bb.instructions.keys())

        ea_list.sort()

        try:
            idx = ea_list.index(ea)

            if idx == 0:
                raise Exception
        except:
            return -1

        self.current_ea = ea_list[idx - 1]
        return self.current_ea


    ####################################################################################################################
    def rebase (self, new_base):
        '''
        Rebase the module and all components with the new base address. This routine will check if the current and
        requested base addresses are equivalent, so you do not have to worry about checking that yourself.

        @type  new_base: Dword
        @param new_base: Address to rebase module to
        '''

        # nothing to do.
        if new_base == self.base:
            return
            
        # TODO: rewrite for SQL backing

        # rebase each function in the module.
        for function in self.nodes.keys():
            self.nodes[function].id       = self.nodes[function].id       - self.base + new_base
            self.nodes[function].ea_start = self.nodes[function].ea_start - self.base + new_base
            self.nodes[function].ea_end   = self.nodes[function].ea_end   - self.base + new_base

            function = self.nodes[function]

            # rebase each basic block in the function.
            for bb in function.nodes.keys():
                function.nodes[bb].id       = function.nodes[bb].id       - self.base + new_base
                function.nodes[bb].ea_start = function.nodes[bb].ea_start - self.base + new_base
                function.nodes[bb].ea_end   = function.nodes[bb].ea_end   - self.base + new_base

                bb = function.nodes[bb]

                # rebase each instruction in the basic block.
                for ins in bb.instructions.keys():
                    bb.instructions[ins].ea = bb.instructions[ins].ea - self.base + new_base

                # fixup the instructions dictionary.
                old_dictionary  = bb.instructions
                bb.instructions = {}

                for key, val in old_dictionary.items():
                    bb.instructions[key - self.base + new_base] = val

            # fixup the functions dictionary.
            old_dictionary = function.nodes
            function.nodes = {}

            for key, val in old_dictionary.items():
                function.nodes[val.id] = val

            # rebase each edge between the basic blocks in the function.
            for edge in function.edges.keys():
                function.edges[edge].src =  function.edges[edge].src - self.base + new_base
                function.edges[edge].dst =  function.edges[edge].dst - self.base + new_base
                function.edges[edge].id  = (function.edges[edge].src << 32) + function.edges[edge].dst

            # fixup the edges dictionary.
            old_dictionary = function.edges
            function.edges = {}

            for key, val in old_dictionary.items():
                function.edges[val.id] = val

        # fixup the modules dictionary.
        old_dictionary = self.nodes
        self.nodes     = {}

        for key, val in old_dictionary.items():
            self.nodes[val.id] = val

        # rebase each edge between the functions in the module.
        for edge in self.edges.keys():
            self.edges[edge].src =  self.edges[edge].src - self.base + new_base
            self.edges[edge].dst =  self.edges[edge].dst - self.base + new_base
            self.edges[edge].id  = (self.edges[edge].src << 32) + self.edges[edge].dst

        # finally update the base address of the module.
        self.base = new_base


    ####################################################################################################################
    def uuid_bin_to_string (self, uuid):
        '''
        Convert the binary representation of a UUID to a human readable string.

        @type  uuid: Raw
        @param uuid: Raw binary bytes consisting of the UUID

        @rtype:  String
        @return: Human readable string representation of UUID.
        '''

        import struct

        (block1, block2, block3) = struct.unpack("<LHH", uuid[:8])
        (block4, block5, block6) = struct.unpack(">HHL", uuid[8:16])

        return "%08x-%04x-%04x-%04x-%04x%08x" % (block1, block2, block3, block4, block5, block6)
    
    ####################################################################################################################
    # PROPERTIES
    
    name            = property(getName, setName, deleteName, "name")
    base            = property(getBase, setBase, deleteBase, "base")
    signature       = property(getSignature, setSignature, deleteSignature, "signature")
    nodes           = property(getNodes, setNodes, deleteNodes, "nodes")
    num_functions   = property(getNumFunctions, setNumFunctions, deleteNumFunctions, "num_functions")
