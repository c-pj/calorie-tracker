#pylint: disable=missing-module-docstring
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=invalid-name
#pylint: disable=line-too-long
#pylint: disable=global-statement
#pylint: disable=no-self-use
#pylint: disable=too-many-instance-attributes

import tkinter as tk
import datetime as dt
from tinydb import TinyDB, Query
import matplotlib.pyplot as plt

class DB():
    def __init__(self):
        self.query = Query()
        self.validate = Validate()
        self.initialise_db()

    def initialise_db(self):
        self.db_file = TinyDB('user_data.json')
        self.tbl_user_data = self.db_file.table('user_data')
        self.tbl_entry_search_data = self.db_file.table('entry_search_data')
        self.tbl_intake_calculation_data = self.db_file.table('intake_calculation_data')
        self.tbl_goal_data = self.db_file.table('goals_data')
        self.tbl_diet_data = self.db_file.table('diet_data')
        self.tbl_log_data = self.db_file.table('log_data')
        results = self.tbl_user_data.contains(doc_id = 1)
        if not results:
            self.tbl_user_data.insert({'name': '', 'age': '', 'sex': '', 'height': '', 'waist': '', 'hips': ''})
        results = self.tbl_entry_search_data.contains(doc_id = 1)
        if not results:
            self.tbl_entry_search_data.insert({'entry_search_results': ''})
        results = self.tbl_intake_calculation_data.contains(doc_id = 1)
        if not results:
            self.tbl_intake_calculation_data.insert({'intake_calculation': '0'})
        results = self.tbl_goal_data.contains(doc_id = 1)
        if not results:
            self.tbl_goal_data.insert({'target_weight': '', 'start_date': '', 'target_date': ''})
        results = self.tbl_diet_data.contains(doc_id = 1)
        if not results:
            self.tbl_diet_data.insert({'maintenance_kcal': '', 'required_deficit_surplus': ''})
        results = self.tbl_log_data.contains(doc_id = 1)
        if not results:
            self.tbl_log_data.insert({'entry': '1', 'kcal': '', 'weight': ''})

    def get_user_details(self):
        results = self.tbl_user_data.get(doc_id = 1)
        return results

    def update_user_details(self, name, age, sex, height, waist, hips):
        self.tbl_user_data.update({'name': name, 'age': age, 'sex': sex, 'height': height, 'waist': waist, 'hips': hips}, doc_ids = [1])

    def update_user_details_with_input(self, name, age, sex, height, waist, hips):
        if sex == 'Select Sex':
            sex = ''
        items_to_check_alpha = [name, sex]
        items_to_check_numeric = [age, height, waist, hips]
        if self.validate.alpha(items_to_check_alpha) and self.validate.numeric(items_to_check_numeric) is True:
            self.update_user_details(name, age, sex, height, waist, hips)

    def upsert_log_entry(self, entry, kcal, weight):
        if entry and kcal and weight:
            self.tbl_log_data.upsert({'entry': entry, 'kcal': kcal, 'weight': weight}, self.query.entry == entry)

    def get_last_log_entry(self):
        results = self.tbl_log_data.get(doc_id=len(self.tbl_log_data))
        return results

    def get_entry_search_results(self):
        results = self.tbl_entry_search_data.get(doc_id = 1)
        return results

    def update_entry_search_results(self, search_results):
        self.tbl_entry_search_data.update({'entry_search_results': search_results}, doc_ids = [1])

    def search_log_entries_by_range(self, range_min, range_max):
        if range_min and range_max:
            if self.validate.numeric(range_min) and self.validate.numeric(range_max) is True:
                if int(range_max) - int(range_min) > 29:
                    return False
                if self.validate.range(range_min, range_max) is True:
                    results = self.tbl_log_data.all()
                    string = ''
                    i = int(range_min) - 1
                    while i < int(range_max):
                        log_entry_number = results[i]['entry']
                        log_kcal_consumed = results[i]['kcal']
                        log_weight = results[i]['weight']
                        new_line = ''
                        if i < int(range_max) - 1:
                            new_line = '\n'
                        string += 'No. ' + log_entry_number + ', kcal: ' + log_kcal_consumed + ', W: ' + log_weight + new_line
                        i += 1
                    self.update_entry_search_results(string)

    def display_progress(self):
        results = self.tbl_log_data.all()
        return results

    def update_intake_calculation(self, kcal_per_100, amount_consumed):
        item_intake_total = maths.calculate_item_kcal(kcal_per_100, amount_consumed)
        self.tbl_intake_calculation_data.update({'intake_calculation': item_intake_total}, doc_ids = [1])

    def reset_intake_calculation(self):
        self.tbl_intake_calculation_data.update({'intake_calculation': '0'}, doc_ids = [1])

    def get_intake_calculation(self):
        results = self.tbl_intake_calculation_data.get(doc_id = 1)
        return results

    def update_personal_goal(self, target_weight, start_date_dd, start_date_mm, start_date_yyyy, target_date_dd, target_date_mm, target_date_yyyy):
        if self.validate.numeric(target_weight) and target_weight != '':
            start_date = start_date_dd+'/'+start_date_mm+'/'+start_date_yyyy
            target_date = target_date_dd+'/'+target_date_mm+'/'+target_date_yyyy
            if self.validate.date_format(start_date) and self.validate.date_format(target_date):
                self.tbl_goal_data.update({'target_weight': target_weight, 'start_date': start_date, 'target_date': target_date}, doc_ids = [1])

    def get_personal_goal(self):
        results = self.tbl_goal_data.get(doc_id = 1)
        return results

    def get_diet_data(self):
        results = self.tbl_diet_data.get(doc_id = 1)
        return results

    def get_entry_data(self):
        results = self.tbl_log_data.all()
        return results

    def update_maintenance_kcal(self, maintenance_estimate):
        self.tbl_diet_data.update({'maintenance_kcal': maintenance_estimate}, doc_ids = [1])

    def update_required_daily_kcal(self, required_kcal_estimate):
        self.tbl_diet_data.update({'required_deficit_surplus': required_kcal_estimate}, doc_ids = [1])

class Maths():
    def centimetres_to_inches(self, cm_measurement):
        results = float(cm_measurement)/2.54
        return results

    def inches_to_centimetres(self, in_measurement):
        results = float(in_measurement)*2.54
        return results

    def calculate_item_kcal(self, kcal_per_100, amount_consumed):
        item_intake_total_json = db.get_intake_calculation()
        item_intake_total = item_intake_total_json['intake_calculation']

        results = str(float(item_intake_total)+float(kcal_per_100)*float(amount_consumed))
        return results

    def calculate_maintenance_kcal(self):
        log_data = db.get_entry_data()
        try:
            if log_data[1]['weight'] != '':
                kcal_total = 0
                log_data_weight_prev = 0
                log_data_weight = 0
                difference_between_total = 0
                i = 1
                for _ in log_data[:-1]:
                    log_data_kcal = float(log_data[i]['kcal'])
                    kcal_total += float(log_data_kcal)
                    log_data_weight_prev = float(log_data[i-1]['weight'])
                    log_data_weight = float(log_data[i]['weight'])
                    difference_between_weight = self.calculate_difference(log_data_weight_prev, log_data_weight)
                    difference_between_total += float(difference_between_weight)

                    i += 1
                daily_kcal_consumed = kcal_total/(i-1)
                daily_weight_lost = difference_between_total/(i-1)
                actual_daily_deficit = daily_weight_lost * 100 * 77 #multiply daily_weight_lost by 100 to get gram total, then multiply by kcal in one gram of fat to get daily caloric deficit
                maintenance_kcal = str(round(daily_kcal_consumed+actual_daily_deficit))
                db.update_maintenance_kcal(maintenance_kcal)
        except: #pylint: disable=bare-except
            return False

    def calculate_difference(self, x, y):
        if x >= y:
            result = x - y
        else:
            result = (y - x)*-1
        return result

    def calculate_required_daily_intake(self):
        try:
            last_log_entry_data_json = db.get_last_log_entry()
            current_weight = last_log_entry_data_json['weight'] or ''
            goal_data_json = db.get_personal_goal()
            goal_weight = goal_data_json['target_weight'] or ''
            goal_start_date = goal_data_json['start_date'] or ''
            goal_target_date = goal_data_json['target_date'] or ''
            if goal_start_date != '' and goal_target_date != '':
                days_between = self.find_difference_between_dates(goal_start_date, goal_target_date)
                if days_between > 0:
                    weight_to_change_daily = ((float(current_weight) - float(goal_weight))/days_between)*-1
                    diet_data_json = db.get_diet_data()
                    maintenance_kcal = diet_data_json['maintenance_kcal'] or ''
                    daily_kcal_required = str(round(float(maintenance_kcal) + (weight_to_change_daily * 100 * 77)))
                    db.update_required_daily_kcal(daily_kcal_required)
        except: #pylint: disable=bare-except
            return False

    def find_difference_between_dates(self, start_date, end_date):
        date_a = dt.datetime.strptime(start_date, '%d/%m/%Y')
        date_b = dt.datetime.strptime(end_date, '%d/%m/%Y')
        result = (date_b - date_a).days
        return result

class Validate():
    def alpha(self, array):
        for item in array:
            if not item.isalpha():
                return False
        return True

    def numeric(self, array):
        try:
            array = [float(item) for item in array]
        except: #pylint: disable=bare-except
            return False
        for item in array:
            if not isinstance(item, float):
                return False
        return True

    def range(self, range_min, range_max):
        items_to_check_numeric = [range_min, range_max]
        if self.numeric(items_to_check_numeric) is True:
            last_log_entry_data_json = db.get_last_log_entry()
            db_tbl_max = int(last_log_entry_data_json['entry'])
            if int(range_min) > 0 and int(range_max) <= db_tbl_max:
                return True
            else:
                return False
        else:
            return False

    def date_format(self, date):
        try:
            dt.datetime.strptime(date, '%d/%m/%Y')
            return True
        except: #pylint: disable=bare-except
            return False

class Graph():
    def plot_graph(self):
        log_data = db.display_progress()
        if log_data[0]['weight'] != '':
            log_data_entry = []
            log_data_weight = []
            i = 0
            for _ in log_data:
                log_data_entry.append(float(log_data[i]['entry']))
                log_data_weight.append(float(log_data[i]['weight']))
                i += 1
            plt.plot(log_data_entry, log_data_weight, color='blue', marker='o')
            plt.title('Weight Progression', fontsize=14)
            plt.xlabel('Day', fontsize=14)
            plt.ylabel('Weight', fontsize=14)
            plt.grid(True)
            plt.show()

db = DB()
maths = Maths()
graph = Graph()

#---------------------------------GUI---------------------------------#
class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(FrHome)
        self.title('Calorie Tracker')

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid(row=0, column=0)

class FrHome(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, padx=5, pady=15)
        #--------------------NAVIGATION MENU--------------------#
        self.navigation_menu = tk.Frame(self)
        self.navigation_menu.grid(row=0, column=0, rowspan=5, columnspan=1, sticky='nw')
        tk.Button(self.navigation_menu, text='User Details',
                    command=lambda: master.switch_frame(FrHome), width=15).grid(row=0, column=0)
        tk.Button(self.navigation_menu, text='Display Progress',
                    command=lambda: master.switch_frame(FrDisplayProgress), width=15).grid(row=1, column=0)
        tk.Button(self.navigation_menu, text='Add Entry',
                    command=lambda: master.switch_frame(FrLogEntry), width=15).grid(row=2, column=0)
        tk.Button(self.navigation_menu, text='Edit Details',
                    command=lambda: master.switch_frame(FrUpdatePersonal), width=15).grid(row=3, column=0)
        #--------------------CONTAINER FRAME--------------------#
        self.main_content = tk.Frame(self)
        self.main_content.grid(row=0, column=1, padx=5)
        #-------------------------------------------------------#
        maths.calculate_required_daily_intake()
        #-------------------PERSONAL DETAILS--------------------#
        self.main_content_label_frame = tk.LabelFrame(self.main_content, text='Personal Details', font='Arial 10')
        self.main_content_label_frame.grid(row=0, column=0, sticky='nw')

        user_data_json = db.get_user_details()
        user_name = user_data_json['name'] or ''
        user_age = user_data_json['age'] or ''
        user_sex = user_data_json['sex'] or ''
        user_height = user_data_json['height'] or ''
        user_waist = user_data_json['waist'] or ''
        user_hips = user_data_json['hips'] or ''
        last_log_entry_data_json = db.get_last_log_entry()
        user_weight = last_log_entry_data_json['weight'] or ''

        personal_info_str = 'Name: '+user_name+'    Age: '+user_age+'    Sex: '+user_sex+'    Height: '+user_height+'cm' \
                                +'    Weight: '+user_weight+'kg'+'    Waist: '+user_waist+'in'+'    Hips: '+user_hips+'in'

        tk.Label(self.main_content_label_frame, text=personal_info_str,
                    font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, sticky='nw', padx=5, pady=5)

        #-------------------HEALTH INFORMATION------------------#
        self.main_content_label_frame_2 = tk.LabelFrame(self.main_content, text='Health Information', font='Arial 10')
        self.main_content_label_frame_2.grid(row=1, column=0, sticky='nw')

        user_bmi = ''
        user_whtr = ''
        user_whr = ''

        if user_weight and user_height:
            user_bmi = str(round((float(user_weight))/((float(user_height)/100)**2), 2))
        if user_waist and user_height:
            user_whtr = str(round((float(user_waist))/(maths.centimetres_to_inches(user_height)), 2))
        if user_waist and user_hips:
            user_whr = str(round((float(user_waist))/(round((float(user_hips)))), 2))

        health_info_str = 'Body mass index: '+user_bmi+'    Waist/height ratio: '+user_whtr+'    Waist/hip ratio: '+user_whr

        tk.Label(self.main_content_label_frame_2, text=health_info_str,
                    font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, sticky='nw', padx=5, pady=5)

        #--------------------GOAL INFORMATION-------------------#
        self.main_content_label_frame_2 = tk.LabelFrame(self.main_content, text='Goal Information', font='Arial 10')
        self.main_content_label_frame_2.grid(row=2, column=0, sticky='nw')

        goal_data_json = db.get_personal_goal()
        target_weight = goal_data_json['target_weight'] or ''
        start_date = goal_data_json['start_date'] or ''
        target_date = goal_data_json['target_date'] or ''

        goal_info_str = 'Target weight: '+target_weight+'kg'+'    Start: '+start_date+'    End: '+target_date

        tk.Label(self.main_content_label_frame_2, text=goal_info_str,
                    font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, sticky='nw', padx=5, pady=5)

        #--------------------DIET INFORMATION-------------------#
        self.main_content_label_frame_2 = tk.LabelFrame(self.main_content, text='Caloric Estimates (based on log data and goal)', font='Arial 10')
        self.main_content_label_frame_2.grid(row=3, column=0, sticky='nw')

        diet_data_json = db.get_diet_data()
        maintenance_kcal = diet_data_json['maintenance_kcal'] or ''
        required_deficit_surplus = diet_data_json['required_deficit_surplus'] or ''

        diet_info_str = 'Maintenance: '+maintenance_kcal+'kcal'+'    Required intake: '+required_deficit_surplus+'kcal'

        tk.Label(self.main_content_label_frame_2, text=diet_info_str,
                    font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, sticky='nw', padx=5, pady=5)

class FrDisplayProgress(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, padx=5, pady=15)
        #--------------------NAVIGATION MENU--------------------#
        self.navigation_menu = tk.Frame(self)
        self.navigation_menu.grid(row=0, column=0, rowspan=5, columnspan=1, sticky='nw')
        tk.Button(self.navigation_menu, text='User Details',
                    command=lambda: master.switch_frame(FrHome), width=15).grid(row=0, column=0)
        tk.Button(self.navigation_menu, text='Display Progress',
                    command=lambda: master.switch_frame(FrDisplayProgress), width=15).grid(row=1, column=0)
        tk.Button(self.navigation_menu, text='Add Entry',
                    command=lambda: master.switch_frame(FrLogEntry), width=15).grid(row=2, column=0)
        tk.Button(self.navigation_menu, text='Edit Details',
                    command=lambda: master.switch_frame(FrUpdatePersonal), width=15).grid(row=3, column=0)
        #--------------------CONTAINER FRAME--------------------#
        self.main_content = tk.Frame(self)
        self.main_content.grid(row=0, column=1, padx=5)
        #-------------------------------------------------------#

        self.main_content_label_frame_sub_1 = tk.LabelFrame(self.main_content, text='Display Progress', font='Arial 10')
        self.main_content_label_frame_sub_1.grid(row=0, column=0, sticky='nw', padx=10, pady=10)

        maths.calculate_maintenance_kcal()

        tk.Button(self.main_content_label_frame_sub_1, text='Open Graph in New Window', command=lambda: [graph.plot_graph(), master.switch_frame(FrDisplayProgress)]).grid(row=0,
                    column=6, rowspan=1, columnspan=1, padx=15, pady=25)

class FrLogEntry(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, padx=5, pady=15)
        #--------------------NAVIGATION MENU--------------------#
        self.navigation_menu = tk.Frame(self)
        self.navigation_menu.grid(row=0, column=0, rowspan=5, columnspan=1, sticky='nw')
        tk.Button(self.navigation_menu, text='User Details',
                    command=lambda: master.switch_frame(FrHome), width=15).grid(row=0, column=0)
        tk.Button(self.navigation_menu, text='Display Progress',
                    command=lambda: master.switch_frame(FrDisplayProgress), width=15).grid(row=1, column=0)
        tk.Button(self.navigation_menu, text='Add Entry',
                    command=lambda: master.switch_frame(FrLogEntry), width=15).grid(row=2, column=0)
        tk.Button(self.navigation_menu, text='Edit Details',
                    command=lambda: master.switch_frame(FrUpdatePersonal), width=15).grid(row=3, column=0)
        #--------------------CONTAINER FRAME--------------------#
        self.main_content = tk.Frame(self)
        self.main_content.grid(row=0, column=1, padx=5)
        #-------------------------------------------------------#

        last_log_entry_data_json = db.get_last_log_entry()
        log_entry_number = last_log_entry_data_json['entry'] or ''
        log_min_number = '1'
        log_kcal_consumed = last_log_entry_data_json['kcal'] or ''
        log_weight = last_log_entry_data_json['weight'] or ''
        log_new_entry_number = int(last_log_entry_data_json['entry']) + 1 or ''
        if log_entry_number == '1' and log_kcal_consumed == '':
            log_new_entry_number = '1'
            log_kcal_consumed = 'N/A'
            log_weight = 'N/A'
        if int(log_entry_number) - 29 > 0:
            log_min_number = str(int(log_entry_number) - 29)

        self.main_content_label_frame = tk.LabelFrame(self.main_content, text='Add Log Entry', font='Arial 10')
        self.main_content_label_frame.grid(row=0, column=0, sticky='nw')

        #-------------------DAILY KCAL INTAKE-------------------#
        self.main_content_label_frame_sub_1 = tk.LabelFrame(self.main_content_label_frame, text='Daily Calories and Weight', font='Arial 10')
        self.main_content_label_frame_sub_1.grid(row=0, column=0, sticky='nw', padx=10, pady=10)
        self.entries_container_1 = tk.Frame(self.main_content_label_frame_sub_1)
        self.entries_container_1.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.entries_container_1, text='Entry No.',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_log_no = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        entry_log_no.insert(-1, log_new_entry_number)
        entry_log_no.grid(row=0, column=1, rowspan=1, columnspan=1, pady=0)

        tk.Label(self.entries_container_1, text='Kcal',
            font='Arial 9').grid(row=0, column=2, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_log_kcal = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        entry_log_kcal.insert(-1, '')
        entry_log_kcal.grid(row=0, column=3, rowspan=1, columnspan=1, pady=0)

        tk.Label(self.entries_container_1, text='Weight (kg)',
            font='Arial 9').grid(row=0, column=4, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_log_weight = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        entry_log_weight.insert(-1, '')
        entry_log_weight.grid(row=0, column=5, rowspan=1, columnspan=1, pady=0)

        tk.Button(self.entries_container_1, text='Submit', command=lambda: [db.upsert_log_entry(entry_log_no.get(),
                    entry_log_kcal.get(), entry_log_weight.get()), master.switch_frame(FrLogEntry)]).grid(row=0, column=6, rowspan=1, columnspan=1, padx=5, pady=5)

        self.previous_entry_data_container = tk.Frame(self.main_content_label_frame_sub_1)
        self.previous_entry_data_container.grid(row=1, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.previous_entry_data_container, text='Previous entry: ' + log_entry_number + ', kcal: ' + log_kcal_consumed + ', weight: ' + log_weight,
        font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)

        #--------------------INTAKE CALULATOR-------------------#
        self.main_content_label_frame_sub_1 = tk.LabelFrame(self.main_content_label_frame, text='Intake Calculator (per food/drink item)', font='Arial 10')
        self.main_content_label_frame_sub_1.grid(row=1, column=0, sticky='nw', padx=10, pady=10)
        self.entries_container_1 = tk.Frame(self.main_content_label_frame_sub_1)
        self.entries_container_1.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.entries_container_1, text='Kcal Per 100g/ml',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        intake_kcal_per_100 = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        intake_kcal_per_100.grid(row=0, column=1, rowspan=1, columnspan=1, pady=0)

        tk.Label(self.entries_container_1, text='Multiplier',
            font='Arial 9').grid(row=0, column=2, rowspan=1, columnspan=1, padx=5, pady=5)
        intake_amount_consumed = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        intake_amount_consumed.grid(row=0, column=3, rowspan=1, columnspan=1, pady=0)

        tk.Button(self.entries_container_1, text='Add to Total', command=lambda: [db.update_intake_calculation(intake_kcal_per_100.get(),
                    intake_amount_consumed.get()), master.switch_frame(FrLogEntry)]).grid(row=0, column=4, rowspan=1, columnspan=1, padx=5, pady=5)

        self.previous_entry_data_container = tk.Frame(self.main_content_label_frame_sub_1)
        self.previous_entry_data_container.grid(row=1, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.previous_entry_data_container, text='Total kcal consumed: ',
        font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)

        item_intake_total_json = db.get_intake_calculation()
        item_intake_total = item_intake_total_json['intake_calculation']

        tk.Label(self.previous_entry_data_container, text=item_intake_total,
        font='Arial 9').grid(row=0, column=2, rowspan=1, columnspan=1, padx=5, pady=5)

        tk.Button(self.previous_entry_data_container, text='Reset Calculation', command=lambda: [db.reset_intake_calculation(),
                    master.switch_frame(FrLogEntry)]).grid(row=0, column=3, rowspan=1, columnspan=1, padx=5, pady=5)

        #--------------------SEARCH FUNCTION--------------------#
        self.main_content_label_frame_2 = tk.LabelFrame(self.main_content, text='Search Entries by Range (max range: 30)', font='Arial 10')
        self.main_content_label_frame_2.grid(row=0, column=3, sticky='nw', padx=5)

        self.entries_container_2 = tk.Frame(self.main_content_label_frame_2)
        self.entries_container_2.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.entries_container_2, text='Start',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        search_entry_min = tk.Entry(self.entries_container_2, font='Arial 10', width=10)
        search_entry_min.insert(-1, log_min_number)
        search_entry_min.grid(row=0, column=1, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Label(self.entries_container_2, text='End',
            font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        search_entry_max = tk.Entry(self.entries_container_2, font='Arial 10', width=10)
        search_entry_max.insert(-1, log_entry_number)
        search_entry_max.grid(row=1, column=1, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Button(self.entries_container_2, text='Search', command=lambda: [db.search_log_entries_by_range(search_entry_min.get(),
                    search_entry_max.get()), master.switch_frame(FrLogEntry)]).grid(row=2, column=1, rowspan=1, columnspan=1, padx=5, pady=(9,5))

        #--------------------SEARCH RESULTS---------------------#
        results = db.get_entry_search_results()
        entry_range_search = results['entry_search_results']

        self.search_results_container = tk.Frame(self.main_content_label_frame_2, bg='white')
        self.search_results_container.grid(row=0, column=1, sticky='nw', padx=5, pady=5)

        lbl = tk.Label(self.search_results_container, text='Results',
            font='Arial 9', bg='white')
        lbl.grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)

        lbl = tk.Label(self.search_results_container, text=entry_range_search,
            font='Arial 9', bg='white')
        lbl.grid(row=1, column=0, rowspan=1, columnspan=1, padx=5, pady=5)

class FrUpdatePersonal(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, padx=5, pady=15)
        #--------------------NAVIGATION MENU--------------------#
        self.navigation_menu = tk.Frame(self)
        self.navigation_menu.grid(row=0, column=0, rowspan=5, columnspan=1, sticky='nw')
        tk.Button(self.navigation_menu, text='User Details',
                    command=lambda: master.switch_frame(FrHome), width=15).grid(row=0, column=0)
        tk.Button(self.navigation_menu, text='Display Progress',
                    command=lambda: master.switch_frame(FrDisplayProgress), width=15).grid(row=1, column=0)
        tk.Button(self.navigation_menu, text='Add Entry',
                    command=lambda: master.switch_frame(FrLogEntry), width=15).grid(row=2, column=0)
        tk.Button(self.navigation_menu, text='Edit Details',
                    command=lambda: master.switch_frame(FrUpdatePersonal), width=15).grid(row=3, column=0)
        #--------------------CONTAINER FRAME--------------------#
        self.main_content = tk.Frame(self)
        self.main_content.grid(row=0, column=1, padx=5)
        #-------------------------------------------------------#

        user_data_json = db.get_user_details()
        user_name = user_data_json['name'] or ''
        user_age = user_data_json['age'] or ''
        user_sex = user_data_json['sex'] or 'Select Sex'
        user_height = user_data_json['height'] or ''
        user_waist = user_data_json['waist'] or ''
        user_hips = user_data_json['hips'] or ''

        self.main_content_label_frame = tk.LabelFrame(self.main_content, text='Edit Details', font='Arial 10')
        self.main_content_label_frame.grid(row=0, column=0, sticky='nw')

        #-------------------PERSONAL DETAILS--------------------#
        self.main_content_label_frame_sub_1 = tk.LabelFrame(self.main_content_label_frame, text='Personal Details', font='Arial 10')
        self.main_content_label_frame_sub_1.grid(row=0, column=0, sticky='nw', padx=10, pady=10)
        self.entries_container_1 = tk.Frame(self.main_content_label_frame_sub_1)
        self.entries_container_1.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.entries_container_1, text='Name',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_user_name = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        entry_user_name.insert(-1, user_name)
        entry_user_name.grid(row=0, column=1, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Label(self.entries_container_1, text='Age',
            font='Arial 9').grid(row=0, column=2, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_user_age = tk.Entry(self.entries_container_1, font='Arial 10', width=10)
        entry_user_age.insert(-1, user_age)
        entry_user_age.grid(row=0, column=3, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Label(self.entries_container_1, text='Sex',
            font='Arial 9').grid(row=0, column=4, rowspan=1, columnspan=1, padx=5, pady=5)
        options_list = ['Male', 'Female']
        options_message = tk.StringVar(self.entries_container_1)
        options_message.set(user_sex)
        entry_user_sex = tk.OptionMenu(self.entries_container_1, options_message, *options_list)
        entry_user_sex.grid(row=0, column=5, rowspan=1, columnspan=1, padx=5, pady=5)

        #-------------------BODY MEASUREMENTS-------------------#
        self.main_content_label_frame_sub_2 = tk.LabelFrame(self.main_content_label_frame, text='Body Measurements', font='Arial 10')
        self.main_content_label_frame_sub_2.grid(row=1, column=0, sticky='nw', padx=10, pady=10)
        self.entries_container_2 = tk.Frame(self.main_content_label_frame_sub_2)
        self.entries_container_2.grid(row=0, column=0, sticky='nw', padx=5, pady=5)

        tk.Label(self.entries_container_2, text='Height (cm)',
            font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_user_height = tk.Entry(self.entries_container_2, font='Arial 10', width=10)
        entry_user_height.insert(-1, user_height)
        entry_user_height.grid(row=1, column=1, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Label(self.entries_container_2, text='Waist (in)',
            font='Arial 9').grid(row=1, column=2, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_user_waist = tk.Entry(self.entries_container_2, font='Arial 10', width=10)
        entry_user_waist.insert(-1, user_waist)
        entry_user_waist.grid(row=1, column=3, rowspan=1, columnspan=1, pady=(6, 0))

        tk.Label(self.entries_container_2, text='Hips (in)',
            font='Arial 9').grid(row=1, column=4, rowspan=1, columnspan=1, padx=5, pady=5)
        entry_user_hips = tk.Entry(self.entries_container_2, font='Arial 10', width=10)
        entry_user_hips.insert(-1, user_hips)
        entry_user_hips.grid(row=1, column=5, rowspan=1, columnspan=1, pady=(6, 0), padx=(0, 5))

        tk.Button(self.main_content_label_frame, text='Submit', command=lambda: db.update_user_details_with_input(entry_user_name.get(), entry_user_age.get(), options_message.get(),
                    entry_user_height.get(), entry_user_waist.get(), entry_user_hips.get())).grid(row=2, column=0, rowspan=1, columnspan=1, padx=5, pady=5)

        #---------------------PERSONAL GOALS--------------------#
        self.main_content_label_frame_2 = tk.LabelFrame(self.main_content, text='Update Personal Goal', font='Arial 10')
        self.main_content_label_frame_2.grid(row=0, column=1, sticky='nw', padx=(5, 0))
        self.entries_container_3 = tk.Frame(self.main_content_label_frame_2)
        self.entries_container_3.grid(row=0, column=0, sticky='nw', padx=15, pady=5)

        tk.Label(self.entries_container_3, text='Target Weight (kg)',
            font='Arial 9').grid(row=1, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        target_weight = tk.Entry(self.entries_container_3, font='Arial 10', width=10)
        target_weight.insert(-1, '')
        target_weight.grid(row=1, column=1, rowspan=1, columnspan=1, pady=(6, 0))

        self.date_input_container_1 = tk.Frame(self.main_content_label_frame_2)
        self.date_input_container_1.grid(row=1, column=0, sticky='nw', padx=15, pady=5)

        tk.Label(self.date_input_container_1, text='Start Date\n(DD/MM/YYYY)',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        start_date_dd = tk.Entry(self.date_input_container_1, font='Arial 10', width=3)
        start_date_dd.insert(-1, '')
        start_date_dd.grid(row=0, column=1, rowspan=1, columnspan=1, padx=2)
        start_date_mm = tk.Entry(self.date_input_container_1, font='Arial 10', width=3)
        start_date_mm.insert(-1, '')
        start_date_mm.grid(row=0, column=2, rowspan=1, columnspan=1, padx=2)
        start_date_yyyy = tk.Entry(self.date_input_container_1, font='Arial 10', width=5)
        start_date_yyyy.insert(-1, '')
        start_date_yyyy.grid(row=0, column=3, rowspan=1, columnspan=1, padx=2)

        self.date_input_container_2 = tk.Frame(self.main_content_label_frame_2)
        self.date_input_container_2.grid(row=2, column=0, sticky='nw', padx=15, pady=5)

        tk.Label(self.date_input_container_2, text='End Date\n(DD/MM/YYYY)',
            font='Arial 9').grid(row=0, column=0, rowspan=1, columnspan=1, padx=5, pady=5)
        target_date_dd = tk.Entry(self.date_input_container_2, font='Arial 10', width=3)
        target_date_dd.insert(-1, '')
        target_date_dd.grid(row=0, column=1, rowspan=1, columnspan=1, padx=2)
        target_date_mm = tk.Entry(self.date_input_container_2, font='Arial 10', width=3)
        target_date_mm.insert(-1, '')
        target_date_mm.grid(row=0, column=2, rowspan=1, columnspan=1, padx=2)
        target_date_yyyy = tk.Entry(self.date_input_container_2, font='Arial 10', width=5)
        target_date_yyyy.insert(-1, '')
        target_date_yyyy.grid(row=0, column=3, rowspan=1, columnspan=1, padx=2)

        tk.Button(self.date_input_container_2, text='Submit', command=lambda: db.update_personal_goal(target_weight.get(), start_date_dd.get(), start_date_mm.get(),
                    start_date_yyyy.get(), target_date_dd.get(), target_date_mm.get(), target_date_yyyy.get())).grid(row=0, column=4, rowspan=1, columnspan=1, padx=5, pady=5)

#---------------------------------GUI---------------------------------#

def main():
    db.__init__()
    gui = GUI()
    gui.mainloop()

if __name__ == '__main__':
    main()
