# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
{
    "name" : "Extension Module of Document Management System",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Generic Modules/Others",
    "website": "http://www.openerp.com",
    "description": """This is an extension module of document management system with
    * Implementation of Versioning and lock system
""",
    "depends" : ["base","process","document"],
    "init_xml" : [],
    "update_xml" : ['document_extension_view.xml'],
    "demo_xml" : [],
    "active": False,
    "installable": True,
    "certificate": 23638762444717
}