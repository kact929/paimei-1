#
# PIDA Function
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

from sql_singleton import *

from basic_block import *
from defines     import *

class function (pgraph.graph, pgraph.node):
    '''
    '''
    dbid                = None
    database_file       = None
    __cached            = False

    __ea_start          = None
    __ea_end            = None
    __name              = None
    __is_import         = False
    __flags             = None

    # TODO: implement RPC functionality
    __rpc_cache         = False
    __rpc_uuid          = None
    __rpc_opcode        = None
                        
    # Frame info        
    __frame_info_cache  = False
    __saved_reg_size    = 0
    __frame_size        = 0
    __ret_size          = 0
    __local_var_size    = 0
    __arg_size          = 0
    __local_var_cache   = False
    __local_vars        = {}                       
    __arg_cache         = False
    __args              = {}

    __nodes             = None

    # GHETTO - we want to store the actual function to function edge start address.
    outbound_eas        = {}
    
    # does not require an accessor                    
    module              = None
                        
                        
    # is this runtime only?
    chunks              = []
                           
    ext                 = {}    

    ####################################################################################################################
    def __init__ (self, database_id, database_file):
        '''
        Analyze all the function chunks associated with the function starting at ea_start.
        self.fill(ea_start).

        @see: defines.py

        @type  ea_start: DWORD
        @param ea_start: Effective address of start of function (inclusive)
        @type  depth:    Integer
        @param depth:    (Optional, Def=DEPTH_FULL) How deep to analyze the module
        @type  analysis: Integer
        @param analysis: (Optional, Def=ANALYSIS_NONE) Which extra analysis options to enable
        @type  module:   pida.module
        @param module:   (Optional, Def=None) Pointer to parent module container
        '''

        self.dbid = database_id
        self.database_file = database_file

    ####################################################################################################################
    def __load_from_sql(self):
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        sql = "SELECT name, module, start_address, end_address FROM function WHERE id = %d;" % self.dbid
        curs.execute(sql)
                
        results = curs.fetchone()
        
        if results is None:
            raise "Function [ID:%d] does not exist in the database" % self.dbid
        
        self.__name     = results[0]
        self.module     = results[1]        
        self.__ea_start = results[2]
        self.__ea_end   = results[3]
        
        self.__cached = True

    def __load_frame_info_from_sql(self):
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        sql = "SELECT saved_reg_size, frame_size, ret_size, local_var_size, arg_size FROM frame_info WHERE function = %d;" % self.dbid
        curs.execute(sql)
                
        results = curs.fetchone()        
        
        if results is None:
            raise "Frame information for function [ID:%d] does not exist in the database" % self.dbid
            
        self.__saved_reg_size   = results[0]
        self.__frame_size       = results[1]
        self.__ret_size         = results[2]
        self.__local_var_size   = results[3]
        self.__arg_size         = results[4]
            
        self.__frame_info_cache = True
        
    def __load_args_from_sql (self):
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        # TODO: discuss with pedram how we want the values filled in
        sql = "SELECT name FROM function_variables WHERE function = %d AND flags = 1;" % self.dbid
        curs.execute(sql)
                
        results = curs.fetchall()
        
        if results:
            for arg in results:
                self.__args.append(results[0])
                
        self.__arg_cache = True
                
    def __load_local_vars_from_sql (self):
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        # TODO: discuss with pedram how we want the values filled in
        sql = "SELECT name FROM function_variables WHERE function = %d AND flags = 2;" % self.dbid
        curs.execute(sql)
                
        results = curs.fetchall()
        
        if results:
            for localvar in results:
                self.__local_vars.append(results[0])      
                
        self.__local_var_cache = True

    ####################################################################################################################
    # nodes accessors
        
    def __getNodes (self):
        '''
        Gets the signature of the module
        
        @rtype:  String
        @return: The signature of the module
        '''
        
        if self.__nodes == None:
            ret_val = {}
            ss = sql_singleton()
            
            cursor = ss.connection(self.database_file).cursor()
            
            results = cursor.execute("SELECT id FROM basic_block WHERE function = %d" % self.dbid).fetchall()
            
            for basic_block_id in results:
                new_basic_block = basic_block(basic_block_id, self.database_file)
                ret_val[new_basic_block.ea_start] = new_basic_block
                
            self.__nodes = ret_val
        return self.__nodes
        
    def __setNodes (self, value):
        '''
        Sets the nodes of the module. This will generate an error.
        
        @type  value: String
        @param value: The signature of the module.
        '''
        
        raise TypeError, "nodes and functions are not directly writable for modules. This is a read-only property"
        
    def __deleteNodes (self):
        '''
        destructs the signature of the module
        '''
        pass 
    
    ####################################################################################################################
    # num_instruction
    
    def __getNumInstructions (self):
        '''
        The number of instructions in the function
        
        @rtype:  Integer
        @return: The number of instructions in the function
        '''
        
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        sql = "SELECT count(*) FROM instruction WHERE function = %d;" % self.dbid
        curs.execute(sql)
        
        try:
            ret_val = curs.fetchone()[0]
        except:
            ret_val = 0
            
        return ret_val
        
    ####
    
    def __setNumInstructions (self, value):
        '''
        Sets the number of instructions (raises an exception - READ ONLY)
        
        @type  value: Integer
        @param value: The number of instructions in the function
        '''
        raise TypeError, "num_instructions is a read-only property"
        return -1
    
    ####
        
    def __deleteNumInstructions (self):
        '''
        destructs the num_instructions
        '''
        pass # dynamically generated property value

    ####################################################################################################################
    # ea_start accessors
    
    def __getEaStart (self):
        '''
        Gets the starting address of the function.
        
        @rtype:  DWORD
        @return: The starting address of the function
        '''
        
        if not self.__cached:
            self.__load_from_sql()            
            
        return self.__ea_start
        
    ####
    
    def __setEaStart (self, value):
        '''
        Sets the starting address of the function
        
        @type  value: DWORD
        @param value: The starting address of the function
        '''
        
        if self.__cached:
            self.__ea_start = value
            
        ss = sql_singleton()    
        curs = ss.connection(self.database_file).cursor()                    
        curs.execute("UPDATE function SET start_address=%d where id=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteEaStart (self):
        '''
        destructs the address of the function
        '''
        del self.__ea_start

    ####################################################################################################################
    # ea_end accessors
    
    def __getEaEnd (self):
        '''
        The ending address of the function. This should not be treated as an absolute due to function chunking.
        
        @rtype:  DWORD
        @return: The ending address of the function
        '''
        
        if not self.__cached:
            self.__load_from_sql()
            
        return self.__ea_end
        
    ####
    
    def __setEaEnd (self, value):
        '''
        Sets the ending address of the function
        
        @type  value: DWORD
        @param value: The ending address of the function
        '''
        
        if self.__cached:
            self.__ea_end = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE function SET end_address=%d where id=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteEaEnd (self):
        '''
        destructs the ending address of the function
        '''
        del self.__ea_end
        
    ####################################################################################################################
    # name accessors
    
    def __getName (self):
        '''
        Gets the name of the function.
        
        @rtype:  String
        @return: The name of the function.
        '''
        
        if not self.__cached:
            self.__load_from_sql()
            
        return self.__name
        
    ####
    
    def __setName (self, value):
        '''
        Sets the name of the function.
        
        @type  value: String
        @param value: The name of the function.
        '''
        
        if self.__cached:
            self.__name = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE function SET name='%s' where id=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteName (self):
        '''
        destructs the name of the function
        '''
        del self.__name     

    ####################################################################################################################
    # is_import accessors
    
    def __getIsImport (self):
        '''
        Gets the indicator if the function is an import.
        
        @rtype:  Boolean
        @return: The indicator if the function is an import.
        '''
        
        if not self.__cached:
            self.__load_from_sql()
            
        return self.__is_import
        
    ####
    
    def __setIsImport (self, value):
        '''
        Sets the indicator if the function is an import.
        
        @type  value: Boolean
        @param value: The indicator if the function is an import.
        '''
        
        raise TypeError, "is_import is a read-only property"
        return -1
    
    ####
        
    def __deleteIsImport (self):
        '''
        destructs the indicator if the function is an import
        '''
        del self.__is_import 
        
    ####################################################################################################################
    # flags accessors
    
    def __getFlags (self):
        '''
        Gets the function flags.
        
        @rtype:  Unknown
        @return: The function flags.
        '''
        
        if not self.__cached:
            self.__load_from_sql()
            
        return self.__flags
        
    ####
    
    def __setFlags (self, value):
        '''
        Sets the function flags.
        
        @type  value: Unknown
        @param value: The function flags.
        '''
        
        if self.__cached:
            self.__flags = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE function SET flags=%d where id=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteFlags (self):
        '''
        destructs the function flags
        '''
        del self.__flags 

    ####################################################################################################################
    # saved_reg_size accessors
    
    def __getSavedRegSize (self):
        '''
        Gets the saved register size.
        
        @rtype:  Integer
        @return: The saved register size.
        '''
        
        if not self.__frame_info_cache:            
            self.__load_frame_info_from_sql()
            
        return self.__saved_reg_size
        
    ####
    
    def __setSavedRegSize (self, value):
        '''
        Sets the saved register size.
        
        @type  value: Integer
        @param value: The saved register size.
        '''
        
        if self.__frame_info_cache:
            self.__saved_reg_size = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE frame_info SET saved_reg_size=%d where function=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteSavedRegSize (self):
        '''
        destructs the saved register size
        '''
        del self.__saved_reg_size 
        
    ####################################################################################################################
    # frame_size accessors
    
    def __getFrameSize (self):
        '''
        Gets the frame size.
        
        @rtype:  Integer
        @return: The frame size.
        '''
        
        if not self.__frame_info_cache:
            self.__load_frame_info_from_sql()
            
        return self.__frame_size
        
    ####
    
    def __setFrameSize (self, value):
        '''
        Sets the frame size.
        
        @type  value: Integer
        @param value: The frame size.
        '''
        
        if self.__frame_info_cache:
            self.__frame_size = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE frame_info SET frame_size=%d where function=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteFrameSize (self):
        '''
        destructs the frame size
        '''
        del self.__frame_size 

    ####################################################################################################################
    # ret_size accessors
    
    def __getRetSize (self):
        '''
        Gets the return size.
        
        @rtype:  Integer
        @return: The return size.
        '''
        
        if not self.__frame_info_cache:
            self.__load_frame_info_from_sql()
            
        return self.__ret_size
        
    ####
    
    def __setRetSize (self, value):
        '''
        Sets the return size.
        
        @type  value: Integer
        @param value: The return size.
        '''
        
        if self.__frame_info_cache:
            self.__ret_size = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE frame_info SET ret_size=%d where function=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteRetSize (self):
        '''
        destructs the return size
        '''
        del self.__ret_size 

    ####################################################################################################################
    # local_var_size accessors
    
    def __getLocalVarSize (self):
        '''
        Gets the local variable frame size.
        
        @rtype:  Integer
        @return: The local variable frame size.
        '''
        
        if not self.__frame_info_cache:
            self.__load_frame_info_from_sql()
            
        return self.__local_var_size
        
    ####
    
    def __setLocalVarSize (self, value):
        '''
        Sets the local variable frame size.
        
        @type  value: Integer
        @param value: The local variable frame size.
        '''
        
        if self.__frame_info_cache:
            self.__local_var_size = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE frame_info SET local_var_size=%d where function=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteLocalVarSize (self):
        '''
        destructs the local variable frame size
        '''
        del self.__local_var_size 

    ####################################################################################################################
    # arg_size accessors
    
    def __getArgSize (self):
        '''
        Gets the argument frame size.
        
        @rtype:  Integer
        @return: The argument frame size.
        '''
        
        if not self.__frame_info_cache:
            self.__load_frame_info_from_sql()
            
        return self.__arg_size
        
    ####
    
    def __setArgSize (self, value):
        '''
        Sets the argument frame size.
        
        @type  value: Integer
        @param value: The argument frame size.
        '''
        
        if self.__frame_info_cache:
            self.__arg_size = value
            
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        curs.execute("UPDATE frame_info SET arg_size=%d where function=%d" % (value, self.dbid))
        ss.connection().commit()
    
    ####
        
    def __deleteArgSize (self):
        '''
        destructs the argument frame size
        '''
        del self.__arg_size 

    ####################################################################################################################
    # local_vars accessors
    
    def __getLocalVars (self):
        '''
        Gets the local variable dictionary.
        
        @rtype:  Integer
        @return: The argument frame size.
        '''
        
        if not self.__local_var_cache:
            self.__load_local_vars_from_sql()
            
        return self.__local_vars
        
    ####
    
    def __setLocalVars (self, value):
        '''
        Sets the argument dictionary.
        
        @type  value: Integer
        @param value: The argument frame size.
        '''
        
        #TODO test how it actually handles a += accessor
        
        if self.__local_var_cache:
            pass
            
        #ss = sql_singleton()
        #curs = ss.connection(self.database_file).cursor()
        #curs.execute("UPDATE frame_info SET arg_size=%d where function=%d" % (value, self.dbid))
        #ss.connection().commit()
    
    ####
        
    def __deleteLocalVars (self):
        '''
        destructs the argument dictionary
        '''
        del self.__local_vars


    ####################################################################################################################
    # args accessors
    
    def __getArgs (self):
        '''
        Gets the argument dictionary.
        
        @rtype:  Integer
        @return: The argument frame size.
        '''
        
        if not self.__arg_cache:
            self.__load_args_from_sql()
            
        return self.__args
        
    ####
    
    def __setArgs (self, value):
        '''
        Sets the argument dictionary.
        
        @type  value: Integer
        @param value: The argument frame size.
        '''
        
        #TODO test how it actually handles a += accessor
        
        if self.__arg_cache:
            pass
            
        #ss = sql_singleton()
        #curs = ss.connection(self.database_file).cursor()
        #curs.execute("UPDATE frame_info SET arg_size=%d where function=%d" % (value, self.dbid))
        #ss.connection().commit()
    
    ####
        
    def __deleteArgs (self):
        '''
        destructs the argument dictionary
        '''
        del self.__args
        
    ####################################################################################################################
    # num_local_vars accessors
    
    def __getNumLocalVars (self):
        '''
        Gets the number of local variables.
        
        @rtype:  Integer
        @return: The number of local variables.
        '''
        
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        ret_val = curs.execute("SELECT count(*) FROM function_variables WHERE function = %d AND flags & %d > 0" % (self.dbid, VAR_TYPE_LOCAL)).fetchone()[0]
              
        return ret_val
        
    ####
    
    def __setNumLocalVars (self, value):
        '''
        Sets the number of local variables. (will raise an exception, this is a READ-ONLY property)
        
        @type  value: Integer
        @param value: The number of local variables.
        '''
        
        raise TypeError, "num_local_vars is a read-only property"
    
    ####
        
    def __deleteNumLocalVars (self):
        '''
        destructs the number of local variables
        '''
        pass # dynamically generated property value
        
    ####################################################################################################################
    # num_args accessors
    
    def __getNumArgs (self):
        '''
        Gets the number of function arguments.
        
        @rtype:  Integer
        @return: The number of function arguments.
        '''
        
        ss = sql_singleton()
        curs = ss.connection(self.database_file).cursor()
        ret_val = curs.execute("SELECT count(*) FROM function_variables WHERE function = %d AND flags & %d > 0" % (self.dbid, VAR_TYPE_ARGUMENT)).fetchone()[0]
              
        return ret_val
        
    ####
    
    def __setNumArgs (self, value):
        '''
        Sets the number of function arguments.
        
        @type  value: Integer
        @param value: The number of function arguments.
        '''
        
        raise TypeError, "num_args is a read-only property"
    
        
    ####
        
    def __deleteNumArgs (self):
        '''
        destructs the number of function arguments
        '''
        pass # dynamically generated property value 


    ####################################################################################################################
    def find_basic_block (self, ea):
        '''
        Locate and return the basic block that contains the specified address.

        @type  ea: DWORD
        @param ea: An address within the basic block to find

        @rtype:  pida.basic_block
        @return: The basic block that contains the given address or None if not found.
        '''

        ss = sql_singleton()                        
        curs = ss.connection(self.database_file).cursor()
        results = curs.execute("SELECT id FROM basic_block WHERE function = %d AND start_address <= %d AND end_address >= %d" % (self.dbid, ea, ea)).fetchone()
        
        if results:
            return basic_block(results[0], self.database_file)
                
        return None


    ####################################################################################################################
    def render_node_gml (self, graph):
        '''
        Overload the default node.render_node_gml() routine to create a custom label. Pass control to the default
        node renderer and then return the merged content.

        @type  graph: pgraph.graph
        @param graph: Top level graph object containing the current node

        @rtype:  String
        @return: Contents of rendered node.
        '''

        self.label  = "<span style='font-family: Courier New; font-size: 10pt; color: #000000'>"
        self.label += "<p><font color=#004080><b>%08x %s</b></font></p>" % (self.ea_start, self.name)

        self.gml_height = 100
        self.gml_width  = (len(self.name) + 10) * 10

        if not self.is_import:
            self.label += "<b>size</b>: <font color=#FF8040>%d</font><br>" % (self.ea_end - self.ea_start)
            self.label += "<b>arguments</b>:<br>"

            for key, arg in self.args.items():
                self.label += "&nbsp;&nbsp;&nbsp;&nbsp;[%02x]%s<br>" % (key, arg)

                required_width = (len(arg) + 10) * 10

                if required_width > self.gml_width:
                    self.gml_width = required_width

                self.gml_height += 20

            self.label += "<b>local variables</b>:<br>"

            for key, var in self.local_vars.items():
                self.label += "&nbsp;&nbsp;&nbsp;&nbsp;[%02x] %s<br>" % (key, var)

                required_width = (len(var) + 10) * 10

                if required_width > self.gml_width:
                    self.gml_width = required_width

                self.gml_height += 20

        self.label += "</span>"

        return super(function, self).render_node_gml(graph)


    ####################################################################################################################
    def render_node_graphviz (self, graph):
        '''
        Overload the default node.render_node_graphviz() routine to create a custom label. Pass control to the default
        node renderer and then return the merged content.

        @type  graph: pgraph.graph
        @param graph: Top level graph object containing the current node

        @rtype:  pydot.Node()
        @return: Pydot object representing node
        '''

        self.shape = "ellipse"

        if self.is_import:
            self.label = "%s" % (self.name)
        else:
            self.label  = "%08x %s\\n" % (self.ea_start, self.name)
            self.label += "size: %d"   % (self.ea_end - self.ea_start)

        return super(function, self).render_node_graphviz(graph)


    ####################################################################################################################
    def render_node_udraw (self, graph):
        '''
        Overload the default node.render_node_udraw() routine to create a custom label. Pass control to the default
        node renderer and then return the merged content.

        @type  graph: pgraph.graph
        @param graph: Top level graph object containing the current node

        @rtype:  String
        @return: Contents of rendered node.
        '''

        if self.is_import:
            self.label = "%s" % (self.name)
        else:
            self.label  = "%08x %s\\n" % (self.ea_start, self.name)
            self.label += "size: %d"   % (self.ea_end - self.ea_start)

        return super(function, self).render_node_udraw(graph)


    ####################################################################################################################
    def render_node_udraw_update (self):
        '''
        Overload the default node.render_node_udraw_update() routine to create a custom label. Pass control to the
        default node renderer and then return the merged content.

        @rtype:  String
        @return: Contents of rendered node.
        '''

        if self.is_import:
            self.label = "%s" % (self.name)
        else:
            self.label  = "%08x %s\\n" % (self.ea_start, self.name)
            self.label += "size: %d"   % (self.ea_end - self.ea_start)

        return super(function, self).render_node_udraw_update()
        
    ####################################################################################################################
    # PROPERTIES
    
    num_instructions    = property(__getNumInstructions,    __setNumInstructions,   __deleteNumInstructions, "num_instructions")
    ea_start            = property(__getEaStart,            __setEaStart,           __deleteEaStart, "ea_start")
    ea_end              = property(__getEaEnd,              __setEaEnd,             __deleteEaEnd, "ea_end")
    name                = property(__getName,               __setName,              __deleteName, "name")
    is_import           = property(__getIsImport,           __setIsImport,          __deleteIsImport, "is_import")
    flags               = property(__getFlags,              __setFlags,             __deleteFlags, "flags")
                                                                                    
    # Frame info properties                                                         

    saved_reg_size      = property(__getSavedRegSize,       __setSavedRegSize,      __deleteSavedRegSize, "saved_reg_size")
    frame_size          = property(__getFrameSize,          __setFrameSize,         __deleteFrameSize, "frame_size")
    ret_size            = property(__getRetSize,            __setRetSize,           __deleteRetSize, "ret_size")
    local_var_size      = property(__getLocalVarSize,       __setLocalVarSize,      __deleteLocalVarSize, "local_var_size")
    arg_size            = property(__getArgSize,            __setArgSize,           __deleteArgSize, "arg_size")
                                                   
    num_local_vars      = property(__getNumLocalVars,       __setNumLocalVars,      __deleteNumLocalVars, "num_local_vars")
    num_args            = property(__getNumArgs,            __setNumArgs,           __deleteNumArgs, "num_args")
                                                                                    
    nodes               = property(__getNodes,              __setNodes,             __deleteNodes, "nodes")
    args                = property(__getArgs,               __setArgs,              __deleteArgs, "args")    
    local_vars          = property(__getLocalVars,          __setLocalVars,         __deleteLocalVars, "local_vars")    