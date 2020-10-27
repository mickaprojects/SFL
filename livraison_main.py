#!/usr/bin/env python
#coding=cp1252
import threading

from e_bdd import ProdDb
from e_bdd import ProdDb2
from SeleniumSogecLivraisonPgImage import CLivraison_Sgc
import ConfigParser as cfgparser
import os

import sys
reload(sys)
sys.setdefaultencoding('cp1252')

class CExecution(object):
    def __init__(self,sous_dossier=''):
        self.error = 0
        self.msg_error = ""
        self.sous_dossier = sous_dossier
        self.cl1=None
        self.db_execution_lecture()

    def db_execution_lecture(self):
       
        try:
            db = ProdDb()
            sql_liste = "select * from sgc_online_prestation where (table_livraison is not null or table_livraison !='') and (sous_dossier='%s') " % (self.sous_dossier)
            trs_conf = db.openrecordset(sql_liste)
            for rs_conf in trs_conf:
                is_online = False
                table = ""
                sous_dossier = ""
                lot_courrier = ""
                if str(rs_conf["full_online"]).encode("cp1252")=="1":
                    is_online = True
                if rs_conf["sous_dossier"]!=None:
                    sous_dossier = str(rs_conf["sous_dossier"]).encode("cp1252")
                if rs_conf["table_livraison"]!=None:
                    table = str(rs_conf["table_livraison"]).encode("cp1252")

                if not is_online:
                    sql_lot = "select distinct lot_courrier,commande from %s where __s='Q'" % (table)
                    trs_lot = db.openrecordset(sql_lot)
                    for rs_lot in trs_lot:
                        lot_courrier = ""
                        commande = ""
                        if rs_lot['lot_courrier'] != None:
                            lot_courrier = str(rs_lot['lot_courrier']).encode("cp1252")
                            if rs_lot['commande']!=None:                            
                                commande = str(rs_lot['commande']).encode("cp1252")
                                
                            critere_lot_courrier = " lot_courrier='%s' " % (lot_courrier)
                            self.cl1 = CLivraison_Sgc(sous_dossier,table,lot_courrier,critere_lot_courrier,commande)
                else:
                    self.cl1 = CLivraison_Sgc(sous_dossier,table,"")
            db.setNothing()
            try:
                self.cl1.driver.close() 
                self.cl1.driver.quit() 
            except:  
                pass
             
            
        except:
            try:
                self.cl1.driver.close() 
                self.cl1.driver.quit()
            except:  
                pass
        
            
               



class Threaded_Livraison(threading.Thread):
    def __init__(self,sous_doc="",table="",lot_cour="",sql_critere=" 1=1 "):
        threading.Thread.__init__(self)
        self.error = 0
        self.msg_error = ""
        self.sous_dossier = sous_doc
        self.table_livraison = table
        self.critere = sql_critere
        self.lot_courrier = lot_cour


    def run(self):
        try:
            cl1 = CLivraison_Sgc(self.sous_dossier,self.table_livraison,self.lot_courrier,self.critere) 
        except:
            self.error = 1
            self.msg_error = "Erreur lancement livraison selenium pour le sous dossier %s " % (self.sous_dossier)
            print self.msg_error + " probleme thread"


def tuer_process(proc1):
    try:        
        os.kill(proc1, signal.SIGTERM)    
    except:
        pass

if __name__=="__main__":
#    print "debut"
    try: 
        config = cfgparser.ConfigParser()
        config.read("param.ini")
        sous_doc=config.get("travail", "idsousdossier")
        if os.path.exists('pro.lock')==False:
            fichierlock=open('pro.lock','w')
            fichierlock.close() 
            c1 = CExecution(sous_doc)
            
            if os.path.exists('pro.lock')==True:
                os.remove("pro.lock") 

    except:
     
        if os.path.exists('pro.lock')==True:
            os.remove("pro.lock")  
        
              
       
      
#    print "fin"    