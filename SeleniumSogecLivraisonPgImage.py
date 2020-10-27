#!/usr/bin/env python
#coding=cp1252
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import time
import datetime
from threading import Thread
from e_bdd import ProdDb
from e_bdd import ProdDb2
from e_mail import CMail
import json
import sys
import urllib

reload(sys)
sys.setdefaultencoding("cp1252")


class CLivraison_Sgc(object):
    def __init__(self,sous_doc="",table_lire="",lot_cour="",sql_critere=" 1=1 ",commande=""):
        self.driver = None

#        self.chromeexe="C:/Documents and Settings/tantely.RES-TANTELY-IAM/Local Settings/Application Data/Google/Chrome/Application/chrome.exe"
#        self.chromedriverexe="C:/chromedriver_win32/chromedriver.exe"

#        self.chromeexe="/usr/bin/google-chrome-stable"
#        self.chromedriverexe="/usr/local/bin/chromedriver"

       
#        self.chromeOps = webdriver.ChromeOptions()
#        self.chromeOps._binary_location = self.chromeexe
#        self.chromeOps._arguments = ["--enable-internal-flash"]
#        self.chromeOps.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
                   
           
        
          
           
           
        

#        self.driver.implicitly_wait(20)
        self.base_url = "https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/login"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.tb_fields = []
        self.tb_codebar = []
        self.db = ProdDb()
        self.error = 0
        self.msg_error = ""
        self.table_content = table_lire
        self.table_critere = sql_critere
        self.lot_courrier = lot_cour
        self.pid = 0
        self.tb_client = []
        
        self.sgc_online_valeur_id = ""
        self.sgc_online_pli_id = ""
        self.champs_sgc = ""
        self.champs_vvt = ""
        self.sous_dossier = sous_doc
        self.valeur = ""
        self.type_objet = ""
        self.url = ""
        self.date_creation_site = ""
        self.date_extraction = ""
        self.date_livraison = ""
        self.heure_livraison = ""
        self.commande = commande
        
        #driver actions
        print "DEBUT : " , datetime.datetime.now()
#        self.connecter_site()
        self.db_correspondance()
        
        self.db_verif_non_valide_site()
        #self.envoi_mail_fini()
        if self.error>0:
            print "Erreur trouvee :", self.msg_error
        print "FIN : " , datetime.datetime.now()

    def envoi_mail_fini(self):
#        try:
        db = ProdDb2()
        s_liste = ""
        sql_liste = "select string_agg(n_client,', ') as liste from sgc_online_pli where sous_dossier='%s' and date_livraison='%s' and flag_livraison=1 limit 1 " %(self.sous_dossier,self.date_livraison)
        trs = db.openrecordset(sql_liste)
        for rs in trs:
            if rs['liste']!=None:
                s_liste = str(rs['liste']).encode("cp1252")

        s_liste_erreur = ""
        sql_liste = "select string_agg(n_client,', ') as liste from sgc_online_pli where sous_dossier='%s' and date_livraison='%s' and flag_livraison=2 limit 1 " %(self.sous_dossier,self.date_livraison)
        trs = db.openrecordset(sql_liste)
        for rs in trs:
            if rs['liste']!=None:
                s_liste_erreur = str(rs['liste']).encode("cp1252")

        dateheurenow=datetime.datetime.now()
        sujet="Sogec livraison automatique - "+ self.sous_dossier +" - Liste recap num client"
        sbodymail="Sous-Dossier %s liste num client %s " %(self.sous_dossier,s_liste)
        if s_liste_erreur!="":
            sbodymail += "<br> Voici les erreurs : %s " % (s_liste_erreur)
            
        mail = CMail(sujet.encode("cp1252"),dateheurenow,sbodymail)
        if mail.envoyer_mail()==False:
            pass
        db.setNothing()
#        except:
#            pass

    def db_verif_non_valide_site(self):
        try:
            db = ProdDb2()
            prod = ProdDb()
            #self.driver = webdriver.Chrome(self.chromedriverexe, chrome_options=self.chromeOps)
            firefox_profile = webdriver.FirefoxProfile()
#            firefox_profile.set_preference('browser.migration.version', 9001)
#            firefox_profile.set_preference('permissions.default.stylesheet', 2)
#            firefox_profile.set_preference('permissions.default.image', 2)
#            firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
#            firefox_profile.set_preference('pdfjs.disabled','true')
#            firefox_profile.set_preference('plugin.disable_full_page_plugin_for_types','')
            
            
            self.driver = webdriver.Firefox(firefox_profile)
            self.driver.implicitly_wait(20)        
            self.connecter_site()
            driver = self.driver
            driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/saisie")
            json = self.get_datatable_json()
            tb_c = eval(json)
            for lig in tb_c:
                n_client = str(lig[1])
                sql_liste = "select * from sgc_online_pli where sous_dossier='%s' and date_livraison='%s' and n_client='%s' and flag_livraison=1  " %(self.sous_dossier,self.date_livraison,n_client)
               
                trs = db.openrecordset(sql_liste)
                for rs in trs:
                    iidenr = str(rs['sgc_online_pli_id'])
                    sql_upd = "update sgc_online_pli set flag_livraison=2 where sgc_online_pli_id=" + iidenr
                    db.runSql(sql_upd)
                    try:
                        sql_prod_upd = "update %s set __s='Q' where n_client='%s'" % (self.table_content,n_client)
                        prod.runSql(sql_prod_upd)
                    except:
                        pass
                    try:
                        sql_prod_upd = "update %s set __s='Q' where cb_participant='%s'" % (self.table_content,n_client)
                        prod.runSql(sql_prod_upd)
                    except:
                        pass
            time.sleep(10)
            driver.close()
            driver.quit()
            db.setNothing()
            prod.setNothing()
        except:
            try: 
                time.sleep(10)
                driver.close()
                driver.quit()
            except:
                pass
 
        
    def db_correspondance(self,lastidenr="0"):

        try:
            print "Debut db_correspondance"
            #self.driver = webdriver.Chrome(self.chromedriverexe, chrome_options=self.chromeOps)
            #self.chromeOps 
            print "Apres paramétrage de driver"  
            firefox_profile = webdriver.FirefoxProfile()
#            firefox_profile.set_preference('browser.migration.version', 9001)
#            firefox_profile.set_preference('permissions.default.stylesheet', 2)
#            firefox_profile.set_preference('permissions.default.image', 2)
#            firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
#            firefox_profile.set_preference('pdfjs.disabled','true')
#            firefox_profile.set_preference('plugin.disable_full_page_plugin_for_types','')
            
            
            self.driver = webdriver.Firefox(firefox_profile)
            
            #self.pid = self.driver.binary.process.pid
            self.driver.implicitly_wait(20)
            self.connecter_site()

            self.tb_client = []
            self.driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/saisie")
            json = self.get_datatable_json()
            tb_c = eval(json)
            for lig in tb_c:
                n_client = str(lig[1])
                self.tb_client.append(n_client)
            
            driver = self.driver
    #        driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/formulaire/0")
            curdb = ProdDb()
            curdb2 = ProdDb2()
            tchamps = curdb2.openrecordset("select champs_sgc,champs_vv ,1 as ecraser from sgc_online_dessin_enr where sous_dossier='" + self.sous_dossier + "' and champs_sgc!='pa_id' ")

            trs = curdb.openrecordset("select * from " + str(self.table_content) + " where __s='Q' and " + str(self.table_critere) + " and n_client is not null and n_client <> '' order by idenr limit 100")
            i = 0
            iidenr = "0"
            date_livraison = curdb.getDateJMA()
            self.date_livraison = curdb.getDateJMA()
            self.heure_livraison = curdb.getHours()
            for rs in trs:
                i+=1
                iidenr = str(rs["idenr"])
                n_client = 0
                
                try:
                    if rs["n_client"]!=None:
                        n_client = str(rs["n_client"])
                except:
                    pass
                
                try:
                    if rs["cb_participant"]!=None:
                        n_client = str(rs["cb_participant"])
                except:
                    pass
    #            print "https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/formulaire/" + str(n_client) + "["
                
                print "n_client:"+n_client
                if n_client in self.tb_client:                        
                    driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/formulaire/" + str(n_client))
                    self.error = 0
                    self.msg_error = ""
                    time.sleep(4)
                    ecrasement = "0"
                    for rchamps in tchamps:
                        ecrasement = str(rchamps["ecraser"])
                        if str(rchamps["champs_vv"])=="iban":
                            ecrasement = 0
                        if str(rchamps["champs_vv"])=="bic":
                            ecrasement = 0
                        if str(rchamps["champs_vv"])=="pays":
                            ecrasement = 0
                        if str(rchamps["champs_vv"])=="code_pays":
                            ecrasement = 0
#                        print "champs =%s valeur = %s ecrasement = %s" % (str(rchamps["champs_vv"]), rs[str(rchamps["champs_vv"])], ecrasement)
                        if rs[str(rchamps["champs_vv"])]!=None:                    
                            sval_print = str(rs[str(rchamps["champs_vv"])])
                            sval_print = sval_print.encode("cp1252")
                            self.set_object_data(str(rchamps["champs_sgc"]), sval_print ,ecrasement)
                        else :
                            if str(ecrasement)=="1":   
                                self.set_object_data(str(rchamps["champs_sgc"]), '' ,ecrasement)
                    if self.error==0:
                        
                        self.btn_click_valider()
                        sql_update = "update " + str(self.table_content) + " set __s='G' where idenr =" + str(iidenr)
                        curdb.runSql(sql_update)
                        sql_maj_lot = "update sgc_online_pli set flag_livraison=1 ,date_livraison='%s',heure_livraison='%s' where n_client ='%s'" % (date_livraison, self.heure_livraison,n_client)
                        curdb2.runSql(sql_maj_lot)
                        if self.commande!="":
                            sql_maj_commande = "update sgc_online_pli set idcommande='%s'  where n_client ='%s'" % (self.commande,n_client)
                            curdb2.runSql(sql_maj_commande)
                            
                    else:
                        print self.msg_error
                        sql_update = "update " + str(self.table_content) + " set __s='E' where idenr =" + str(iidenr)
                        curdb.runSql(sql_update)
                        sql_maj_lot = "update sgc_online_pli set flag_livraison=2 ,date_livraison='%s', heure_livraison='%s' where n_client ='%s'" % (date_livraison,self.heure_livraison,n_client)
                        curdb2.runSql(sql_maj_lot)
                else:
                    sql_update = "update " + str(self.table_content) + " set __s='F' where idenr =" + str(iidenr)
                    curdb.runSql(sql_update)
                    sql_maj_lot = "update sgc_online_pli set flag_livraison=2 ,date_livraison='%s', heure_livraison='%s' where n_client ='%s'" % (date_livraison,self.heure_livraison,n_client)
                    curdb2.runSql(sql_maj_lot)
                    
            time.sleep(10)
            driver.close()
            driver.quit()
            
            nb = curdb.dcount("*",self.table_content,"__s='Q' and " + str(self.table_critere))
            if nb>0:
                self.db_correspondance()
            curdb.setNothing()
            curdb2.setNothing()
        except:
            try:
                time.sleep(10)
                driver.close() 
                driver.quit()
            except:  
                pass
            
        
        
    def init_datas(self):
        self.sgc_online_valeur_id = ""
        self.champs_sgc = ""
        self.champs_vvt = ""
        self.sous_dossier = ""
        self.valeur = ""
        self.type_objet = ""
        self.url = ""
        self.date_creation_site = ""
        self.date_extraction = ""

    def init_datas_ligne(self):
        self.champs_sgc = ""
        self.champs_vvt = ""
        self.valeur = ""
        self.type_objet = ""
        self.date_extraction = ""
        

    def connecter_site(self):
#        todo etape 1 connection au site
        try :
            driver = self.driver
            print "AVANT OUVERTURE DE SITE"
            driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/login")
            print "APRES OUVERTURE DE SITE"
            forms = driver.find_elements_by_name("log")
            logs = driver.find_elements_by_name("login")
            lots = driver.find_elements_by_name("lot")
            the_form = forms[0]
            the_log = logs[0]
            the_lot = lots[0]
            self.select_sousdossier_in_list(self.sous_dossier)
            the_log.click()
            the_log.send_keys("99999")
            the_form.click()
            if self.lot_courrier!="":
                the_lot.click()
                the_lot.send_keys(self.lot_courrier)
                
            the_form.submit()
            time.sleep(3)
        except:
            self.error = 1
            self.msg_error = "Erreur de connection sur le site, probleme login"
            try:
                time.sleep(10)
                driver.close() 
                driver.quit()
            except:  
                pass
            
    def fill_id_list(self):
#        todo etape 2 remplissage liste 
        try:
            driver = self.driver
            driver.get("https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/saisie")
            json = self.get_datatable_json()
            self.tb_codebar = eval(json)
            for lig in self.tb_codebar:
                self.url = self.get_url_href(str(lig[2]))
                self.date_creation_site  = str(lig[0])
                self.sgc_online_valeur_id = str(lig[1])
                self.date_extraction = self.db.getDateJMA()
                self.db_insert_list_id()
        except:
            self.error = 2
            self.msg_error = "Erreur, remplissage liste des id"


    def get_list_and_save_data(self):
#        todo parcours liste ids, table pli
        try:            
            curdb = ProdDb()
            s_sql = "select * from sgc_online_pli where flag_extraction=0 and sous_dossier='" + str(self.sous_dossier) + "' order by sgc_online_pli_id asc"
            trs = curdb.openrecordset(s_sql)
            ii = 0
            breaked = False
            for rs in trs:
                ii +=1
                id = str(rs["n_client"])
                self.sgc_online_pli_id = str(rs["sgc_online_pli_id"])
                self.sgc_online_valeur_id = id
                self.get_data_from_id(id)
                self.db_update_flag_extraction()
                if ii==5:
                    breaked= True
                    break
            if breaked:
                time.sleep(10)
                self.driver.close()
                self.driver.quit()
                #self.driver = webdriver.Chrome(self.chromedriverexe, chrome_options=self.chromeOps)
                firefox_profile = webdriver.FirefoxProfile()
#                firefox_profile.set_preference('browser.migration.version', 9001)
#                firefox_profile.set_preference('permissions.default.stylesheet', 2)
#                firefox_profile.set_preference('permissions.default.image', 2)
#                firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
#                firefox_profile.set_preference('pdfjs.disabled','true')
#                firefox_profile.set_preference('plugin.disable_full_page_plugin_for_types','')
                
                
                self.driver = webdriver.Firefox(firefox_profile)
                
                self.driver.implicitly_wait(20)
                self.connecter_site()
                self.fill_id_list()
                self.get_list_and_save_data()            
            curdb.setNothing()
        except:
            self.error = 3
            self.msg_error = "Erreur parcours liste ids, table pli "
        
    def get_data_from_id(self,id):
#        todo navigation par id
        try:            
            driver = self.driver
            s_url = "https://www.offres-de-remboursement-bouygues-telecom.com/bo_saisies/formulaire/" + str(id)
            driver.get(s_url)
            self.get_fields_list()
            self.show_fields_names()
            self.get_images_datas()
            
        except:
            self.error = 4
            self.msg_error = "Erreur navigation par id "


    def select_sousdossier_in_list(self,sous_dossier):
#        todo choix sous_dossier dans liste
        try:            
            self.sous_dossier = sous_dossier
            s_script = "function select_operation(val_op){var obj_sel=document.getElementsByName(\"od_id\")[0];for(i in obj_sel.options){if(obj_sel.options[i].text==val_op){obj_sel.options[i].selected=true;}}};select_operation(\"" + str(sous_dossier) + "\");"
            self.driver.execute_script(s_script)
        except:
            self.error = 5
            self.msg_error = "Erreur choix sous_dossier dans liste"
            
    def get_fields_list(self):
#        todo list des champs dans le formulaire
        ret = ""
        try:
            s_script = "return aFocusOrder;"
            ret = self.driver.execute_script(s_script)
            ret = str(ret).encode('cp1252')
            self.tb_fields = eval(ret)        
        except:
            self.error = 6
            self.msg_error = "Erreur recuperation liste des champs"
        return ret
        
    def show_fields_names(self):
#        todo parcours par champs et insert value data in table
        try :
            for fld_name in self.tb_fields:
                self.champs_sgc = str(fld_name)
                self.type_objet = str(self.get_field_type(fld_name))
                self.valeur = str(self.get_object_data(fld_name))
                self.db_insert_data()
        except:
            self.error = 7
            self.msg_error = "Erreur parcours champs formulaire et insertion dans table"
    
    def get_field_type(self,nam):
#        todo recuperation type du champs
        ret = ""
        try:
            s_script = "return document.getElementsByName(\"" + str(nam) + "\")[0].getAttribute(\"type\");"
            ret = self.driver.execute_script(s_script)
            if ret ==None:
                s_script = "return document.getElementsByName(\"" + str(nam) + "\")[0].tagName;"
                ret = self.driver.execute_script(s_script)
            ret = str(ret).encode('cp1252').upper()
        except e :
            self.error = 8
            self.msg_error = "Erreur recuperation type du champs " + str(nam) + "\n" + str(e.value)
        return ret
    
    def btn_click_valider(self):
        s_script = 'document.getElementById("boutonvalider").click()'
        self.driver.execute_script(s_script)
    
    def get_text_field_value(self,input_name):
#        todo recuperation de la valeur du champs text
        ret = ""
        try:            
            s_script = "return document.getElementsByName(\"" + str(input_name) + "\")[0].value;"
            input_value = self.driver.execute_script(s_script)
            if input_value!=None:
                ret = str(input_value).encode('cp1252')
        except:
            self.error = 9
            self.msg_error = "Erreur de la recuperation de la valeur du champs text"
        return ret
    
    def set_text_field_value(self,input_name,input_value):
#        todo insertion de la valeur du champs text
        input_value_in = input_value
        ret = 0
        try:      
            if input_name.find('date')>=0:
                s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; if (obj_txt.value==''){obj_txt.value= \"" + str(input_value) + "\";}"
                input_value = self.driver.execute_script(s_script)
            else:
                if input_name.find('code_barre')>=0 or input_name.find('imei')>=0:
                    s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; obj_txt.value= \"" + str(input_value) + "\";"
                    input_value = self.driver.execute_script(s_script)                
                else:                    
                    s_script = "return document.getElementsByName(\"" + str(input_name) + "\")[0].value;"
                    input_value_out = str(self.driver.execute_script(s_script)).encode("cp1252")
                    if input_value_out=="":
                        s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; if (obj_txt.value==''){obj_txt.value= \"" + str(input_value) + "\";}"
                        input_value = self.driver.execute_script(s_script)
            ret = 1
        except:
            self.error = 109
            self.msg_error = "Erreur de la insertion de la valeur du champs text " + str(input_name) + " valeur : " + str(input_value)
        return ret


    def set_text_field_value_forcing(self,input_name,input_value):
#        todo insertion de la valeur du champs text avec forcage de la valeur
        input_value_in = input_value
        ret = 0
        try:      
            if input_name.find('date')>=0:
                s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; if (obj_txt.value==''){obj_txt.value= \"" + str(input_value) + "\";}"
                input_value = self.driver.execute_script(s_script)
            else:
                if input_name.find('code_barre')>=0 or input_name.find('imei')>=0:
                    s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; obj_txt.value= \"" + str(input_value) + "\";"
                    input_value = self.driver.execute_script(s_script)                
                else:                    
#                    s_script = "return document.getElementsByName(\"" + str(input_name) + "\")[0].value;"
#                    input_value_out = str(self.driver.execute_script(s_script)).encode("cp1252")
#                    if input_value_out=="":
                    s_script = "var obj_txt = document.getElementsByName(\"" + str(input_name) + "\")[0]; obj_txt.value= \"" + str(input_value) + "\"; "
                    input_value = self.driver.execute_script(s_script)
            ret = 1
        except:
            self.error = 1091
            self.msg_error = "Erreur de la insertion de la valeur du champs text " + str(input_name) + " valeur : " + str(input_value)
        return ret


    def get_checkbox_field_value(self,input_name):
#        todo recuperation de la valeur du champs checkbox
        ret = "0"
        try:            
            s_script = "var bok=document.getElementsByName(\"" + str(input_name) + "\")[0].checked; if (bok) {return \"1\";} else { return \"0\";}"
            checkbox_value = self.driver.execute_script(s_script)
            if checkbox_value!=None:
                ret = checkbox_value
        except:
            self.error = 10
            self.msg_error = "Erreur de la recuperation de la valeur du champs checkbox"
        return ret

    def set_checkbox_field_value(self,input_name,input_value):
#        todo insertion de la valeur du champs checkbox
        ret = 0
        try:            
            if input_value=="1":
                s_script = "document.getElementsByName(\"" + str(input_name) + "\")[0].checked = true;"
                self.driver.execute_script(s_script)
                ret = 1
        except:
            self.error = 110
            self.msg_error = "Erreur de la insertion de la valeur du champs checkbox"
        return ret
        
    def get_select_field_text(self,input_name):
#        todo recuperation de la valeur du champs select
        ret = ""
        try:            
            s_script = "var sels = document.getElementsByName(\"" + str(input_name) + "\")[0];return sels.options[sels.selectedIndex].text;"
            select_text = self.driver.execute_script(s_script)
            if select_text!=None:
                ret = str(select_text).encode('cp1252')
        except:
            self.error = 11
            self.msg_error = "Erreur recuperation de la valeur du champs select"
        return ret

    def set_select_field_text(self,input_name,input_text):
#        todo insertion de la valeur du champs select par texte
        ret = 0
        input_text = urllib.quote( input_text, safe='~()*!.\'')
        input_text = input_text.replace("%E9","%C3%A9")
        try:            
            s_script = "function select_operationt1(val_op){var obj_sel=document.getElementsByName(\"" + str(input_name) + "\")[0];for(i in obj_sel.options){if(encodeURIComponent(obj_sel.options[i].text)==val_op){obj_sel.options[i].selected=true;}}};select_operationt1(\"" + str(input_text) + "\");"
            self.driver.execute_script(s_script)
            ret = 1
        except:
            self.error = 111
            self.msg_error = "Erreur insertion de la valeur du champs select par texte " + str(input_name)
        return ret

    def set_select_field_value(self,input_name,input_value):
#        todo insertion de la valeur du champs select par valeur
        ret = 0
        try:            
            s_script = "function select_operation2(val_op){var obj_sel=document.getElementsByName(\"" + str(input_name) + "\")[0];for(i in obj_sel.options){if(obj_sel.options[i].value==val_op){obj_sel.options[i].selected=true;}}};select_operation2(\"" + str(input_value) + "\");"
            self.driver.execute_script(s_script)
            ret = 1
        except:
            self.error = 1112
            self.msg_error = "Erreur insertion de la valeur du champs select par valeur"
        return ret
    
    def get_radio_field_value(self,input_name):
#        todo recuperation de la valeur du champs radio
        ret = ""
        try:            
            s_script = "function get_my_radio(fld_name){var objs=document.getElementsByName(fld_name);var ret;for(obj in objs){if(objs[obj].checked){ret=objs[obj].value;}}return ret;} return get_my_radio(\"" + str(input_name) + "\");"
            radio_value = self.driver.execute_script(s_script)
            if radio_value!=None:
                ret = str(radio_value).encode('cp1252')
        except:
            self.error = 12
            self.msg_error = "Erreur recuperation de la valeur du champs radio"
        return ret

    def set_radio_field_value(self,input_name,input_value):
#        todo insertion de la valeur du champs radio
        ret = 0
        input_value = input_value.upper()
        try:            
            s_script = 'function set_my_radio(fld_name,fld_value){var objs=document.getElementsByName(fld_name);var ret;for(obj=0;obj<objs.length;obj++){if(objs[obj].value.toUpperCase()==fld_value){objs[obj].checked=true;}}return ret;};set_my_radio("' + str(input_name) + '","' + str(input_value) + '");'
            self.driver.execute_script(s_script)
            ret = 1
        except:
            self.error = 112
            self.msg_error = "Erreur insertion de la valeur du champs radio"
        return ret

    def get_hidden_field_value(self,input_name):
#        todo recuperation de la valeur du champs hidden
        ret = ""
        try:            
            s_script = "function get_my_radio_hidden(fld_name){var objs=document.getElementsByName(fld_name);var ret;for(obj=1;obj<=2;obj++){if(objs[obj].checked){ret=objs[obj].value;}}return ret;} return get_my_radio_hidden(\"" + str(input_name) + "\");"
            radio_value = self.driver.execute_script(s_script)
            if radio_value!=None:
                ret = str(radio_value).encode('cp1252')
        except:
            self.error = 13
            self.msg_error = "Erreur recuperation de la valeur du champs hidden"
        return ret

    def set_hidden_field_value(self,input_name,input_value):
#        todo insertion de la valeur du champs hidden
        ret = 0
        try:            
            if input_value=="":
               input_value = "0"     
            s_script = 'function set_my_radio_hidden(fld_name,fld_value){var objs=document.getElementsByName(fld_name);var ret;for(obj=1;obj<=2;obj++){if(objs[obj].value==fld_value){objs[obj].checked=true;}}return ret;};set_my_radio_hidden("'+ str(input_name) + '","' + str(input_value) + '");'
            self.driver.execute_script(s_script)            
            ret = 1
        except:
            self.error = 113
            self.msg_error = "Erreur insertion de la valeur du champs hidden " + str(input_name)
        return ret
    
    
    
    def get_object_data(self,object_name):
#        todo choix recuperation par type champs
        obj_type = ""
        obj_val = ""
        obj_type = ""
        try:            
            obj_type = str(self.get_field_type(object_name)).upper()        
            if obj_type=="TEXT":
                obj_val = self.get_text_field_value(object_name)
            if obj_type=="PASSWORD":
                obj_val = self.get_text_field_value(object_name)
            elif obj_type=="SELECT":
                obj_val = self.get_select_field_text(object_name)
            elif obj_type=="CHECKBOX":
                obj_val = self.get_checkbox_field_value(object_name)
            elif obj_type =="RADIO":
                obj_val = self.get_radio_field_value(object_name)
            elif obj_type =="HIDDEN":
                obj_val = self.get_hidden_field_value(object_name)
        except:
            self.error = 14
            self.msg_error = "Erreur choix recuperation par type champs"
            print self.msg_error , object_name
        return obj_val

    def set_object_data(self,object_name,object_value, ecraser ="0"):
#        todo choix insertion par type champs
        ret = 0
        try:            
            obj_type = str(self.get_field_type(object_name)).upper()        
            if obj_type=="TEXT":
                if str(ecraser)=="1":                    
                    self.set_text_field_value_forcing(object_name,object_value)
                else:
                    self.set_text_field_value(object_name,object_value)
                    
            if obj_type=="PASSWORD":
                self.set_text_field_value(object_name,object_value)
            elif obj_type=="SELECT":
                self.set_select_field_text(object_name,object_value)
            elif obj_type=="CHECKBOX":
                self.set_checkbox_field_value(object_name,object_value)
            elif obj_type =="RADIO":
                self.set_radio_field_value(object_name,object_value)
            elif obj_type =="HIDDEN":
                self.set_hidden_field_value(object_name,object_value)
            ret = 1
        except:
            print object_name, object_value
            self.error = 114
            self.msg_error = "Erreur choix insertion par type champs"
            
        return ret
    
    def get_datatable_json(self):
#        todo lecture liste des id dans datatables
        ret = ""
        try:            
            s_script = "return oDataTable.fnGetData();"
            s_texte_fck = self.driver.execute_script(s_script)
            ret =  str(s_texte_fck).encode('cp1252')
            if s_texte_fck==None:
                s_script = "return oDataTable.fnGetData();"
                s_texte_fck = self.driver.execute_script(s_script)
                ret = s_texte_fck
        except:
            ret = ""
            self.error = 15
            self.msg_error = "Erreur lecture liste des id dans datatables"
        return ret

    def get_nombre_images(self):
        ret = 0
        s_script = "return document.getElementsByClassName('myimage ax-zoom').length;"
        ret = self.driver.execute_script(s_script)
        return ret

    def get_base64_image(self):
        s_script = "function get_base64(url_image){var img=new Image();img.src=url_image;var canvas=document.createElement('Canvas');canvas.width=img.width;canvas.height=img.height;var context=canvas.getContext('2d');context.drawImage(img,0,0);context.beginPath();return canvas.toDataURL();};var objs=document.getElementsByClassName('myimage ax-zoom');var obj1=objs[0];var base64=get_base64(obj1.src);return base64;"
        base64 = str(self.driver.execute_script(s_script))
        
    def get_base64_image_bynum(self,num):
        s_script = "function get_base64(url_image){var img=new Image();img.src=url_image;var canvas=document.createElement('Canvas');canvas.width=img.width;canvas.height=img.height;var context=canvas.getContext('2d');context.drawImage(img,0,0);context.beginPath();return canvas.toDataURL();};var objs=document.getElementsByClassName('myimage ax-zoom');var obj1=objs[" + str(num) + "];var base64=get_base64(obj1.src);return base64;"
        base64 = str(self.driver.execute_script(s_script))
        return base64

    def get_name_image_bynum(self,num):
        s_script = "return document.getElementsByClassName('myimage ax-zoom')[" + str(num) +"].src;"
        ret = str(self.driver.execute_script(s_script))
        if ret !="":
            ret = ret[ret.rindex('/') + 1:]
        return ret
    
    def get_url_href(self,str_in):
        ret = str_in
        pos = ret.find('"')
        if pos>0:
            ret = ret[pos + 1 :]
            if pos>0:
                pos = ret.find('"')
                ret = ret[:pos]
            else:
                ret = ""
        else:
            ret = ""
        return ret

    def db_insert_data(self):
#        todo bdd table insertion dans valeurs
        try:
            s_sql = """INSERT INTO sgc_online_valeur(
                        sgc_online_pli_id
                        , champs_sgc
                        , valeur
                        , type_objet
                        )
                    """
            s_sql += " VALUES ("
            s_sql += " '" + str(self.sgc_online_pli_id) + "' "
            s_sql += ", '" + str(self.champs_sgc) + "' "
            s_sql += ", '" + str(self.valeur).replace("'","''") + "' "
            s_sql += ", '" + str(self.type_objet) + "' "
            s_sql += " )"
            curdb = ProdDb()
            curdb.runSql(s_sql)
            curdb.setNothing()
        except:
            self.error = 16
            self.msg_error = "Erreur table, insertion dans valeurs"
            
    def db_insert_image_data(self,id_parent="",nom_image="",data_image=""):
        s_sql = """INSERT INTO sgc_online_image(
              sgc_online_pli_id
            , n_ima
            , base_64)
            VALUES (        
        """
        s_sql += " " + str(id_parent) + " "
        s_sql += ", '" + str(nom_image) + "' "
        s_sql += ", '" + str(data_image) + "' "
        s_sql += ")"
        curdb = ProdDb()
        curdb.runSql(s_sql)

    def db_update_flag_extraction(self):
#        todo maj flag extraction dans pli
        try:            
            s_sql = "update sgc_online_pli set flag_extraction=1 where n_client='" + str(self.sgc_online_valeur_id) + "' and sous_dossier='" + str(self.sous_dossier) + "'"
            curdb = ProdDb()
            curdb.runSql(s_sql)
            curdb.setNothing()
        except:
            self.error = 17
            self.msg_error = "Erreur table, maj flag extraction dans pli"
            
    def db_insert_list_id(self):
        try:            
            s_sql = """INSERT INTO sgc_online_pli(
                        sous_dossier
                        , date_sogec
                        , date_extraction
                        , n_client 
                        , url
                    )
                    """
            s_sql += " VALUES ("
            s_sql += " '" + str(self.sous_dossier) + "' "
            s_sql += ", '" + str(self.date_creation_site) + "' "
            s_sql += ", now() "
            s_sql += ", '" + str(self.sgc_online_valeur_id) + "' "
            s_sql += ", '" + str(self.url) + "' "
            s_sql += " ) "
            curdb = ProdDb()
            if curdb.dcount("*","sgc_online_pli","n_client='" + str(self.sgc_online_valeur_id) + "'")==0:            
                curdb.runSql(s_sql)
            curdb.setNothing()
        except:
            self.error = 18
            self.msg_error = "Erreur table, insertion dans pli"
            
    def get_images_datas(self):
        nbim = self.get_nombre_images()
        for i in range(nbim):
            nom_im = self.get_name_image_bynum(i)
            base64 = self.get_base64_image_bynum(i)
            
            self.db_insert_image_data(self.sgc_online_pli_id,nom_im,base64)
        
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
#        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
#    unittest.main()
#    c1 = CLivraison_Sgc("V469")
#    c1 = CLivraison_Sgc("V655")
#    c1 = CLivraison_Sgc("V620","sgc620_q_essai","commande='SGC084' and civilite='M'")
    c1 = CLivraison_Sgc("BC72","sfbc72_l","")
#    c1 = CLivraison_Sgc("V628","sfl628_l","")
#    c1 = CLivraison_Sgc("V621","sfl621_l","")
#    c1 = CLivraison_Sgc("V474","sgo474_l","0000071957")
