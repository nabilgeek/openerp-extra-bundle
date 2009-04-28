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

from osv import osv, fields
import pooler
from copy import deepcopy
from mx import DateTime
import time
import datetime

class hr_holidays_note(osv.osv_memory):
    _name='hr.holidays.note'
    _rec_name = 'note'
    _columns = {
        'note' : fields.text('Note', size=64),
    } 
hr_holidays_note()
 
class wizard_hr_holidays_evaluation(osv.osv_memory):
    _name='wizard.hr.holidays.evaluation'
    _rec_name = 'holiday_status_id'
    _columns = {
        'holiday_status_id':fields.many2one('hr.holidays.status','Holiday Status', required=True, help='This is where you specify the holiday type to synchronize. It will create the "holidays per employee" accordingly if necessary, or replace the value "Max leaves allowed" into the existing one.'),
        'hr_timesheet_group_id':fields.many2one('hr.timesheet.group', 'Timesheet Group', required=True, help='This field allow you to filter on only the employees that have a contract using this working hour.'),
        'float_time':fields.float('Time', required=True, help='''This time depicts the amount per day earned by an employee working a day. 
The computation is: total earned = time * number of working days'''),
        'date_current' : fields.date('Date', help='This field allow you to choose the date to use, for forecast matter e.g')
    }
    _defaults = {
            'date_current' : lambda *a: time.strftime('%Y-%m-%d'),
                 }
    
    def action_create(self, cr, uid, ids, context=None):
        value = {}
        data = {}
        objs = []
        bjs = []
        my_dict = {}
        obj_contract = self.pool.get('hr.contract')
        obj_self = self.browse(cr, uid, ids, context=context)[0]
        group_ids = obj_self.hr_timesheet_group_id.name
        obj_ids = obj_contract.search(cr, uid, [('working_hours_per_day_id', '=', group_ids)])
        for rec_con in obj_contract.browse(cr,uid,obj_ids):
            name=rec_con.employee_id.id
            s_date = rec_con.date_start
            
            cr.execute("select distinct(ht.dayofweek), sum(ht.hour_to - ht.hour_from) from hr_timesheet_group as htg, hr_timesheet as ht where ht.tgroup_id = htg.id and htg.id = %s group by ht.dayofweek" %obj_self.hr_timesheet_group_id.id)
            tsg = cr.fetchall()
            alldays = map(lambda x: x[0], tsg)
            nod = len(alldays)
            alltime = map(lambda x: x[1], tsg)
            how = 0
            for k in alltime:
                how += k
            hpd = how/nod
            
            user_obj = self.pool.get('hr.holidays.per.user')
            user_ids = user_obj.search(cr, uid, [('employee_id', '=', name),('holiday_status', '=', obj_self.holiday_status_id.id)])
            if user_ids:
                old_leave = user_obj.browse(cr, uid, user_ids, context)[0].max_leaves
                
            cr.execute("""SELECT distinct(to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd')) 
                        FROM hr_attendance ha, hr_attendance ha2 
                        WHERE ha.action='sign_in' 
                            AND ha2.action='sign_out' 
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd'))=(to_date(to_char(ha2.name, 'YYYY-MM-dd'),'YYYY-MM-dd')) 
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd') <= %s)  
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd') >= %s) 
                            AND ha.employee_id = %s """, (obj_self.date_current,s_date,name))
            results = cr.fetchall()
            all_dates = map(lambda x: x[0], results)
            days = len(all_dates)
            hrss = days * obj_self.float_time

            if hrss < hpd:
                x = 0
            else:
                day = hrss / hpd
                x = int(day)
                y = day - x
                if y >= 0.5:
                    x += 0.5

            if len(user_ids) == 0:
                data = {'employee_id': name, 'holiday_status': obj_self.holiday_status_id.id, 'max_leaves' : x}
                user_id = user_obj.create(cr, uid, data, context)
                objs.append(user_id)
                return objs
            else:
                user_emp_ids = user_obj.search(cr, uid, [('employee_id', '=', name),('holiday_status', '=', obj_self.holiday_status_id.id)])
                ser_obj = self.pool.get('hr.holidays.per.user').write(cr, uid, user_emp_ids, {'max_leaves':x})

                #value['note'] = ''
                emp_name = rec_con.employee_id.name
                my_dict[name] = [emp_name, old_leave, x, x-old_leave]
                
        header = ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-16s \n! %-20s \n! %-16s ', [_('employee name'), 'Previous holiday number', 'Active holiday number', 'differnce'])
        detail = ""
        detail += self.format_table(header, my_dict)
        
        value['note'] = detail
        note_id = self.pool.get('hr.holidays.note').create(cr, uid, value, context)
        bjs.append(note_id)
            
        return {
            'domain': "[('id','in', ["+','.join(map(str,bjs))+"])]",
            'name': _('Summary Report'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays.note',
            'type': 'ir.actions.act_window'
            }
         
    def action_cancel(self,cr,uid,ids,context=None):
        return {}
    
    def format_table(self, header=[], data_list={}): #This function can work forwidget="text_wiki"
        detail = ""
        detail += (header[0]) % tuple(header[1])
        frow = '\n|-'
        for i in header[1]:
            frow += '\n| %s'
        for key, value in data_list.items():
            detail += (frow) % tuple(value)
        detail = detail + '\n|}'
        return detail
    
wizard_hr_holidays_evaluation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: