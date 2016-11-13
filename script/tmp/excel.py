# -*- coding:utf-8 -*-

import os
import xlrd
import re
import sys
sys.path.append('../..')
from script.db_base import  DB
import time
reload(sys)
sys.setdefaultencoding('utf-8')

mode = 'online'

def storeData(file_path, table_name):
    '''open an excel file'''
    file = xlrd.open_workbook(file_path)
    '''get the first sheet'''
    sheet = file.sheet_by_index(0)
    '''get the number of rows and columns'''
    nrows = sheet.nrows
    ncols = sheet.ncols
    # print "nrows = ", nrows
    # print "ncols = ", ncols
    # print "sheet.row_values(0) = ", sheet.row_values(0)
    if ncols != 7:
        print "Missing Parameters ncols = ", ncols
        sys.exit()

    index=0
    cur_time = int(time.time())
    db = DB(mode)
    for i in range(3, nrows):
        if not sheet.row_values(i)[0]:
            print "Missing Parameters company"
            continue

        index +=1
        contact_tel = str(sheet.row_values(i)[1]).strip().encode('utf-8')
        if not contact_tel or contact_tel=='':
            contact_tel = ''
        elif '-' in contact_tel or '－' in contact_tel or '－' in contact_tel or '—' in contact_tel:
            contact_tel = contact_tel
        elif re.match(r"\d+$", contact_tel) or '.' in contact_tel:
            contact_tel = contact_tel[:-2]
        else:
            print "Missing Parameters contact_tel = ", i, contact_tel
            sys.exit()

        contact_phone = str(sheet.row_values(i)[2]).strip().encode('utf-8')
        if not contact_phone or contact_phone=='':
            contact_phone = ''
        elif '-' in contact_phone:
            contact_phone = contact_phone
        elif re.match(r"\d+$", contact_phone) or '.' in contact_phone:
            contact_phone = contact_phone[:-2]
        else:
            print "Missing Parameters contact_phone = ", i, contact_phone
            sys.exit()

        # col_datas = {'key':'company, company_short, contact_tel, contact_phone, contact_person, contact_email, area, category, link, brief, last_update_time, create_time'}
        # data = '\'{cmp}\', \'{cmpsh}\', \'{tel}\', \'{phone}\', \'{person}\', \'{email}\', \'{area}\', \'{cat}\', \'{link}\',  \'{brief}\',  {ut}, {ct} '.format(
        #         cmp=sheet.row_values(i)[0], cmpsh=sheet.row_values(i)[1],
        #         tel=contact_tel, phone=contact_phone, person=sheet.row_values(i)[4],
        #         email=sheet.row_values(i)[5],area=sheet.row_values(i)[6],cat=sheet.row_values(i)[7], link=sheet.row_values(i)[8], brief=sheet.row_values(i)[9],
        #         ut=cur_time, ct=cur_time)
        col_datas = {'key':'company, contact_tel, contact_phone, contact_person, contact_email, area, category, last_update_time, create_time'}
        data = '\'{cmp}\', \'{tel}\', \'{phone}\', \'{person}\', \'{email}\', \'{area}\', \'{cat}\', {ut}, {ct} '.format(
                cmp=sheet.row_values(i)[0], tel=contact_tel, phone=contact_phone, person=sheet.row_values(i)[3],
                email=sheet.row_values(i)[4],area=sheet.row_values(i)[5],cat=sheet.row_values(i)[6],ut=cur_time, ct=cur_time)
        col_datas['val'] = data

        #print "col_datas = ", col_datas
        db.insert(table_name, col_datas)
    db.commit()
    return index

def getFilesList(self, dir):
    path_list = []
    table_list = []
    file_name_list = os.listdir(dir)
    for file_name in file_name_list:
      path = os.path.join(dir, file_name)
      if os.path.isdir(path):
          '''get the files in sub folder recursively'''
          tmp_lists = self.getFilesList(path)
          path_list.extend(tmp_lists[0])
          table_list.extend(tmp_lists[1])
      else:
          path_list.append(path)
          '''convert file name to mysql table name'''
          file_name = file_name.split('.')[0] #remove .xls
          # file_name = file_name.split('from')[0] #remove characters after 'from'
          file_name = file_name.strip()#remove redundant space at both ends
          file_name = file_name.replace(' ','_') #replace ' ' with '_'
          file_name = file_name.replace('-','_') #replace ' ' with '_'
          file_name = file_name.lower() #convert all characters to lowercase
          table_list.append(file_name)
    return [path_list, table_list]

# python excel.py ./advertiser.xlsx advertiser
if __name__ == "__main__":
    #print "sys.argv = ", sys.argv
    if len(sys.argv)!=3:
        print "Missing Parameters"
        sys.exit()

    # ./ advertiser.xlsx advertiser
    filepath = sys.argv[1]
    tablename = sys.argv[2]
    #advertiser.xlsx
    num = storeData(filepath, tablename)
    print "table_name = ", tablename
    print "[ %d ] data have been stored in TABLE:[ %s ]"%(num, tablename)

