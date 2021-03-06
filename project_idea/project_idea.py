# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class project(osv.osv):
    _inherit = "project.project"
    _columns = {
                "idea_ids": fields.one2many('idea.idea', 'project_id', 'Ideas'),                
        }
project()

class idea_idea(osv.osv):
    _inherit = "idea.idea"
    _columns = {                
                'project_id': fields.many2one('project.project', 'Project', select=True),
    }
idea_idea()
