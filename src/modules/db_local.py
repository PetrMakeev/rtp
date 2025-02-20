import sqlite3
from datetime import datetime
from src.modules.filters import el_zvan, el_obrazov


class DB_Local:
    def __init__(self, db_name="rtp.db"):
        self.db_name = db_name
        self.DBconn = sqlite3.connect(self.db_name)
        self.cursor = self.DBconn.cursor()
        
        query = """ CREATE TABLE IF NOT EXISTS "podr" (
                    "id"	INTEGER NOT NULL,
                    "podr"	TEXT NOT NULL,
                    "ordPodr"	INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )"""
        cursor = self.execute_query(query) 
        
        query = """ CREATE TABLE IF NOT EXISTS "prikaz" (
                    "id"	INTEGER NOT NULL,
                    "nomPrikaz"	TEXT NOT NULL,
                    "dtPrikaz"	TEXT NOT NULL,
                    "pdfLink"	TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )"""
        cursor = self.execute_query(query) 
        
        query = """ CREATE TABLE IF NOT EXISTS "rtp" (
                    "id"	INTEGER NOT NULL,
                    "family"	TEXT NOT NULL,
                    "name"	TEXT NOT NULL,
                    "lastname"	TEXT NOT NULL,
                    "idPodr"	INTEGER NOT NULL,
                    "dol"	TEXT NOT NULL,
                    "obrazov"	INTEGER NOT NULL,
                    "zvanie"	INTEGER NOT NULL,
                    "rezTeor"	INTEGER NOT NULL,
                    "rezFiz"	INTEGER NOT NULL,
                    "rezTech"	INTEGER NOT NULL,
                    "rezSob"	INTEGER NOT NULL,
                    "idPrikaz"	INTEGER NOT NULL,
                    "rtpDo"	TEXT NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )"""
        cursor = self.execute_query(query) 
        
        self.DBconn.commit()  

            
        

    def close_connection(self):
        if self.DBconn:
            self.DBconn.close()

    def execute_query(self, query, params=None):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None



    def read_rtp_to_edit(self, curr_id):
        #             0       1        2        3          4         5        6       7          8          9           10         11          12      13
        #     14            15            16
        query = (
            "SELECT r.id, r.family, r.name, r.lastname, r.idPodr, r.dol, r.obrazov, r.zvanie, r.rezTeor, r.rezTech, r.rezFiz, r.rezSob, r.idPrikaz, r.rtpDo, " 
            "podr.podr, p.nomPrikaz, p.dtPrikaz "
            "FROM rtp AS r "
            "JOIN prikaz AS p ON r.idPrikaz = p.id JOIN podr ON r.idPodr = podr.id "
            "WHERE r.id = ?"
        )
        cursor = self.execute_query(query, (curr_id,))
        result = cursor.fetchone()
        return list(result) if result else []


    def rtp_save(self, rtp):
        if rtp.get("id") == -1:
            # сохраняем нового специалиста
            query = """
                INSERT INTO rtp (
                    family, name, lastname, idPodr, dol, obrazov, zvanie, rezTeor, rezFiz, rezTech, rezSob, idPrikaz, rtpDo
                ) VALUES (
                    :family, :name, :lastname, :idPodr, :dolzh, :obrazov, :zvanie, :rezTeor, :rezFiz, :rezTech, :rezSob, :idPrikaz, :rtpDo
                )
            """
        else:
            # сохраняем изменения в сведения о специалисте
             query = """
                UPDATE rtp
                SET 
                    family = :family,
                    name = :name,
                    lastname = :lastname,
                    idPodr = :idPodr,
                    dol = :dolzh,
                    zvanie = :zvanie,
                    obrazov = :obrazov,
                    rezTeor = :rezTeor,
                    rezFiz = :rezFiz,
                    rezTech = :rezTech,
                    rezSob = :rezSob,
                    idPrikaz = :idPrikaz,
                    rtpDo = :rtpDo
                WHERE id = :id
            """
        
        try:
            
            # Выполняем запрос
            self.execute_query(query, rtp)
            self.DBconn.commit()
            print("Запись успешно добавлена.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
        except Exception as ex:
            print(f"Непредвиденная ошибка: {ex}")
        
        
    def rtp_del(self, curr_id):
        query = (
            "DELETE FROM rtp    "
            "WHERE id = ?"
        )
        cursor = self.execute_query(query, (curr_id,))
        self.DBconn.commit() 
    
    
        

    def read_prikaz(self):
        query = "SELECT id, nomPrikaz, dtPrikaz, pdfLink FROM prikaz order by dtPrikaz"
        cursor = self.execute_query(query)
        if cursor:
            rezult = cursor.fetchall()
            return [
                [
                    el[0],
                    el[1],
                    datetime.strptime(el[2], "%Y-%m-%d"),
                    el[3]
                ]
                for el in rezult
            ]
        return []


    def read_prikaz_to_edit(self, curr_id):
        query = (
            "SELECT p.nomPrikaz, p.dtPrikaz, p.pdfLink "
            "FROM prikaz AS p  "
            "WHERE p.id = ?"
        )
        cursor = self.execute_query(query, (curr_id,))
        result = cursor.fetchone()
        return list(result) if result else []



    def prikaz_save(self, prikaz):
        if prikaz.get("id") == -1:
            # сохраняем нового специалиста
            query = """
                INSERT INTO prikaz (
                    nomPrikaz, dtPrikaz, pdfLink
                ) VALUES (
                    :prikaz_nom, :prikaz_dt, :pdf_link
                )
            """
        else:
            # сохраняем изменения в сведения о специалисте
             query = """
                UPDATE prikaz
                SET 
                    nomPrikaz = :prikaz_nom,
                    dtPrikaz = :prikaz_dt,
                    pdfLink = :pdf_link
                WHERE id = :id
            """
        
        try:
            # # устанавливаем  формат даты Python
            # prikaz['prikaz_dt'] = datetime(prikaz['prikaz_dt'].year, 
            #                                prikaz['prikaz_dt'].month, 
            #                                prikaz['prikaz_dt'].day, 
            #                                0,0,0)
            
            # Выполняем запрос
            self.execute_query(query, prikaz)
            self.DBconn.commit()
            print("Запись успешно добавлена.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
        except Exception as ex:
            print(f"Непредвиденная ошибка: {ex}")
            
            

    def prikaz_del(self, curr_id):
        query = (
            "DELETE FROM prikaz AS p  "
            "WHERE p.id = ?"
        )
        cursor = self.execute_query(query, (curr_id,)) 
        self.DBconn.commit()       
        

    def check_rtp_on_prikaz(self, prikaz_id):
        query = (
            "SELECT id  "
            "FROM rtp  "
            "WHERE idPrikaz = ?"
        )
        cursor = self.execute_query(query, (prikaz_id,))
        result = cursor.fetchone()
        return list(result) if result else []
    
    def check_rtp_on_podr(self, podr_id):
        query = (
            "SELECT id  "
            "FROM rtp  "
            "WHERE idPodr = ?"
        )
        cursor = self.execute_query(query, (podr_id,))
        result = cursor.fetchone()
        return list(result) if result else []    
                   

    # применяем фильтр и получаем данные для грида
    def read_rtp_filter(self, filter_podr, filter_zvan, filter_obrazov, filter_prikaz, filter_dopusk_ist, filter_dopusk_tg):
        str_where = ""

        if filter_podr:
            str_where = filter_podr
        if filter_zvan:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_zvan} "   
        if filter_obrazov:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_obrazov} "           
        if filter_prikaz:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_prikaz} "   
        if filter_dopusk_ist:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_dopusk_ist} "    
        if filter_dopusk_tg:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_dopusk_tg} "    
        
        str_where = ("WHERE " + str_where) if not str_where == '' else ''
        
        query = (
            "SELECT r.id, " +
            "TRIM(r.family) || ' ' || TRIM(r.name) || ' ' || TRIM(r.lastname) AS fio, " +
            "p.podr, r.dol, r.zvanie, r.obrazov, r.rezTeor, r.rezFiz, r.rezTech, r.rezSob, r.rtpDo " +
            "FROM rtp as r " +
            "JOIN podr AS p ON r.idPodr = p.id " +
            str_where +
            "ORDER BY r.family, r.name, r.lastname" 
        )

        cursor = self.execute_query(query)
        if cursor:
            results = cursor.fetchall()
            processed_results = []
            for el in results:
                try:
                    rtpDo = datetime.strptime(el[10], "%Y-%m-%d") if el[10] else None
                except ValueError as e:
                    print(f"Error parsing date for id {el[0]}: {e}")
                    rtpDo = None  # Можно установить значение по умолчанию
                
                
                processed_results.append([
                    str(el[0]).strip(),  # id
                    el[1],  # fio
                    el[2],  # podr
                    el[3],  # dol
                    el_zvan[el[4]],  # zvanie
                    el_obrazov[el[5]],  # obrazov
                    el[6],  # rezTeor
                    el[7],  # rezFiz
                    el[8],  # rezTech
                    el[9],  # rezDob
                    rtpDo  # Преобразованная дата или None
                ])
            return processed_results
        return []


    # применяем фильтр и получаем данные для грида
    def read_rtp_export(self, filter_podr, filter_zvan, filter_obrazov, filter_prikaz, filter_dopusk_ist, filter_dopusk_tg):
        str_where = ""
        if filter_podr:
            str_where = filter_podr
        if filter_zvan:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_zvan} "   
        if filter_obrazov:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_obrazov} "           
        if filter_prikaz:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_prikaz} "   
        if filter_dopusk_ist:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_dopusk_ist} "    
        if filter_dopusk_tg:
            str_where = str_where + f"{' AND ' if not str_where == '' else ''} {filter_dopusk_tg} "    
        
        str_where = ("WHERE " + str_where) if not str_where == '' else ''
        
        
        
        query = (
            "SELECT r.id, " +
            "TRIM(r.family) || ' ' || TRIM(r.name) || ' ' || TRIM(r.lastname) AS fio, " +
            "p.podr, r.dol, r.zvanie, r.obrazov, r.rezTeor, r.rezFiz, r.rezTech, r.rezSob, r.rtpDo, prikaz.nomPrikaz, prikaz.dtPrikaz " +
            "FROM rtp as r " +
            "JOIN podr AS p ON r.idPodr = p.id " +
            "JOIN prikaz ON r.idPrikaz = prikaz.id " +
            str_where +
            "ORDER BY r.family, r.name, r.lastname" 
        )
        
        cursor = self.execute_query(query)
        if cursor:
            results = cursor.fetchall()
            processed_results = []
            for i, el in enumerate(results):
                try:
                    rtpDo = datetime.strptime(el[10], "%Y-%m-%d").strftime("%d.%m.%Y") if el[10] else None
                    prikaz = f'от {datetime.strptime(el[12], "%Y-%m-%d").strftime("%d.%m.%Y")} № {el[11]}'
                except ValueError as e:
                    print(f"Error parsing date for id {el[0]}: {e}")
                    rtpDo = None  # Можно установить значение по умолчанию
                
                
                processed_results.append([
                    i+1,  # id
                    el[1],  # fio
                    el[2],  # podr
                    el[3],  # dol
                    el_zvan[el[4]],  # zvanie
                    el_obrazov[el[5]],  # obrazov
                    prikaz, # prikaz
                    el[6],  # rezTeor
                    el[7],  # rezFiz
                    el[8],  # rezTech
                    el[9],  # rezDob
                    rtpDo  # Преобразованная дата или None
                ])
            return processed_results
        return []



    def read_podr(self):
        query = "SELECT id, podr, ordPodr FROM podr order by ordPodr"
        cursor = self.execute_query(query)
        if cursor:
            rezult = cursor.fetchall()
            return [
                [
                    el[0],
                    el[1],
                    el[2]
                ]
                for el in rezult
            ]
        return []
    
    def podr_save(self, podr):
        if podr.get("id") == -1:
            
            # определяем новый номер порядка
            query = (
                "select max(ordPodr) as maxord FROM podr  "
            )
            cursor = self.execute_query(query)
            result = cursor.fetchone()
            if result[0]:
                podr["ord"] = result[0] + 1  
            else:
                podr["ord"] = 1
            
            
            # сохраняем нового специалиста
            query = """
                INSERT INTO podr (
                    podr, ordPodr
                ) VALUES (
                    :podr, :ord
                )
            """
        else:
            # сохраняем изменения в сведения о специалисте
             query = """
                UPDATE podr
                SET 
                    podr = :podr,
                    ordPodr = :ord
                WHERE id = :id
            """
        
        try:
            
            # Выполняем запрос
            self.execute_query(query, podr)
            self.DBconn.commit()
            print("Запись успешно добавлена.")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи: {e}")
        except Exception as ex:
            print(f"Непредвиденная ошибка: {ex}")
            
            
    def podr_del(self, curr_id):
        query = (
            "DELETE FROM podr AS p  "
            "WHERE p.id = ?"
        )
        cursor = self.execute_query(query, (curr_id,)) 
        self.DBconn.commit()                
        
        
    def ordPodr_swap(self, id1=None, ord1=None, id2=None, ord2=None):
        if id1 and ord1 and id2 and ord2:
            query = (
                "UPDATE podr " +
                "SET ordPodr = CASE " +
                    f"WHEN id = {id1} THEN {ord2} " +
                    f"WHEN id = {id2} THEN {ord1} " +
                    "ELSE ordPodr " +               # Сохраняет текущее значение для остальных записей
                "END " +
                f"WHERE id IN ({id1}, {id2})"
            )
            cursor = self.execute_query(query) 
            self.DBconn.commit()  